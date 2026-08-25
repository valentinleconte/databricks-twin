"""One-shot (idempotent) setup of every Unity Catalog / Vector Search resource this
scenario's two agent tools depend on. Databricks is a SaaS platform, not something you
`docker compose up` locally (see NOTES.md) — this script is the closest equivalent to
openrag-twin's `make twin-up`: rebuild the backing data plane from scratch on any
workspace that has the CLI authenticated (`databricks auth login --profile databricks-twin`).

What it does NOT do: create the Genie space. That step is UI-only — no
`databricks genie create-space` exists — see the instructions this script prints at the
end, and NOTES.md for the full walkthrough.

Usage:
    uv run --with beautifulsoup4 --with httpx --with markitdown python3 scripts/twin/setup_resources.py
"""

import glob
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from dbsql import run_sql  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CORPUS_DIR = os.path.join(REPO_ROOT, "databricks-docs-md")
PROFILE = os.environ.get("DATABRICKS_CONFIG_PROFILE", "databricks-twin")
CATALOG_SCHEMA = "workspace.databricks_twin"
VS_ENDPOINT = "databricks-twin-vs"
EMBEDDING_MODEL = "databricks-gte-large-en"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    chunks, start = [], 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def sql_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "\\'")


def step(title: str):
    print(f"\n=== {title} ===")


def main():
    step("Fetch the doc corpus (skipped if databricks-docs-md/ already has files)")
    if not glob.glob(os.path.join(CORPUS_DIR, "*.md")):
        subprocess.run(
            [
                "uv", "run", "--with", "beautifulsoup4", "--with", "httpx", "--with", "markitdown",
                "python3", os.path.join(os.path.dirname(__file__), "fetch_databricks_docs.py"), CORPUS_DIR,
            ],
            check=True,
        )
    else:
        print(f"{len(glob.glob(os.path.join(CORPUS_DIR, '*.md')))} markdown files already present, skipping fetch.")

    step("Create schema + doc_chunks table")
    run_sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG_SCHEMA}")
    run_sql(f"""
        CREATE OR REPLACE TABLE {CATALOG_SCHEMA}.doc_chunks (
          id STRING NOT NULL,
          content STRING,
          title STRING,
          filename STRING,
          source_url STRING
        ) TBLPROPERTIES (delta.enableChangeDataFeed = true)
    """)

    step("Chunk + load doc_chunks")
    rows = []
    for path in sorted(glob.glob(os.path.join(CORPUS_DIR, "*.md"))):
        text = open(path, encoding="utf-8").read()
        m_title = re.search(r"^title:\s*(.+)$", text, re.MULTILINE)
        m_url = re.search(r"^source_url:\s*(.+)$", text, re.MULTILINE)
        title = m_title.group(1).strip() if m_title else os.path.basename(path)
        url = m_url.group(1).strip() if m_url else ""
        filename = os.path.basename(path)
        body = re.sub(r"^---\n.*?\n---\n\n", "", text, flags=re.DOTALL)
        for i, chunk in enumerate(chunk_text(body, CHUNK_SIZE, CHUNK_OVERLAP)):
            chunk = chunk.strip()
            if chunk:
                rows.append((f"{filename.replace('.md', '')}-{i}", chunk, title, filename, url))

    print(f"{len(rows)} chunks from {len(glob.glob(os.path.join(CORPUS_DIR, '*.md')))} files")
    BATCH = 20
    for b in range(0, len(rows), BATCH):
        batch = rows[b : b + BATCH]
        values = ",\n".join(
            f"('{sql_escape(cid)}', '{sql_escape(c)}', '{sql_escape(t)}', '{sql_escape(fn)}', '{sql_escape(u)}')"
            for cid, c, t, fn, u in batch
        )
        run_sql(f"INSERT INTO {CATALOG_SCHEMA}.doc_chunks (id, content, title, filename, source_url) VALUES\n{values}", wait="50s")
    print(f"inserted {len(rows)} rows into {CATALOG_SCHEMA}.doc_chunks")

    step("Create + load support_tickets table")
    ddl_path = os.path.join(os.path.dirname(__file__), "create_tickets.sql")
    for stmt in [s.strip() for s in open(ddl_path).read().split(";") if s.strip()]:
        run_sql(stmt, wait="30s")
    print(f"{CATALOG_SCHEMA}.support_tickets ready")

    step("Create Vector Search endpoint (idempotent-ish: ignore 'already exists')")
    proc = subprocess.run(
        ["databricks", "vector-search-endpoints", "create-endpoint", VS_ENDPOINT, "STANDARD", "--profile", PROFILE],
        capture_output=True, text=True,
    )
    if proc.returncode != 0 and "already exists" not in proc.stderr.lower():
        print(proc.stderr, file=sys.stderr)
        sys.exit(1)
    print(f"endpoint {VS_ENDPOINT} ready")

    step("Create Vector Search index")
    index_name = f"{CATALOG_SCHEMA}.doc_chunks_index"
    index_json = f"""{{
      "name": "{index_name}",
      "endpoint_name": "{VS_ENDPOINT}",
      "primary_key": "id",
      "index_type": "DELTA_SYNC",
      "delta_sync_index_spec": {{
        "source_table": "{CATALOG_SCHEMA}.doc_chunks",
        "pipeline_type": "TRIGGERED",
        "embedding_source_columns": [
          {{"name": "content", "embedding_model_endpoint_name": "{EMBEDDING_MODEL}"}}
        ]
      }}
    }}"""
    proc = subprocess.run(
        ["databricks", "vector-search-indexes", "create-index", "--json", index_json, "--profile", PROFILE],
        capture_output=True, text=True,
    )
    if proc.returncode != 0 and "already exists" not in proc.stderr.lower():
        print(proc.stderr, file=sys.stderr)
        sys.exit(1)
    print(f"index {index_name} creation requested — first sync can take several minutes on a fresh endpoint")

    step("Genie space — manual step, cannot be automated")
    print(f"""
There is no `databricks genie create-space` CLI command. In the workspace UI:
  1. Sidebar > Genie > New
  2. Add table: {CATALOG_SCHEMA}.support_tickets
  3. Configure > Settings > Default warehouse: your serverless SQL warehouse
  4. Copy the space_id from the room URL (.../genie/rooms/<space_id>) into:
       - .env: GENIE_SPACE_ID=<space_id>   (local dev)
       - databricks.yml: the support_tickets_genie resource's space_id (deploy)

After `databricks bundle deploy` creates the app, run grant_genie_table_access() below
(or the two GRANT statements it prints) — CAN_RUN on the genie_space resource in
databricks.yml is not enough on its own: Genie executes its generated SQL with the
*caller's* UC rights on the underlying table, which is a separate grant chain (found
the hard way in prod — see NOTES.md). The table-level SELECT grant IS declared in
databricks.yml (uc_securable), but USE CATALOG / USE SCHEMA have no bundle-resource
equivalent (bundle validate rejects CATALOG/SCHEMA securable_type) and must be granted
via plain SQL, once, after the app's service principal exists.
""")


def grant_genie_table_access(service_principal_id: str):
    """Run once after `databricks bundle deploy` has created the app (so its service
    principal exists). Only USE CATALOG / USE SCHEMA — the table-level SELECT is already
    declared in databricks.yml and applied automatically on deploy."""
    run_sql(f"GRANT USE CATALOG ON CATALOG workspace TO `{service_principal_id}`")
    run_sql(f"GRANT USE SCHEMA ON SCHEMA {CATALOG_SCHEMA} TO `{service_principal_id}`")
    print(f"Granted USE CATALOG / USE SCHEMA on {CATALOG_SCHEMA} to {service_principal_id}")


if __name__ == "__main__":
    main()
