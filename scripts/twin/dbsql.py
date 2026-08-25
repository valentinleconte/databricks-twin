"""Tiny helper to run ad-hoc SQL against a Databricks SQL warehouse from a local
machine, via the Statement Execution API (`POST /api/2.0/sql/statements`).

There's no dedicated `databricks` CLI subcommand for ad-hoc SQL, so this wraps
`databricks api post`/`get` with polling for async statement completion.
Reads config from the environment (falling back to this repo's own .env
values) instead of hardcoding them, so it stays usable from other scripts.
"""

import json
import os
import subprocess
import sys
import time

PROFILE = os.environ.get("DATABRICKS_CONFIG_PROFILE", "databricks-twin")
WAREHOUSE_ID = os.environ.get("DATABRICKS_WAREHOUSE_ID", "1f75e75518a91b9a")  # Serverless Starter Warehouse


def run_sql(statement: str, wait: str = "30s", profile: str = PROFILE, warehouse_id: str = WAREHOUSE_ID):
    body = {"warehouse_id": warehouse_id, "statement": statement, "wait_timeout": wait}
    proc = subprocess.run(
        ["databricks", "api", "post", "/api/2.0/sql/statements", "--json", json.dumps(body), "--profile", profile],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print("CLI ERROR:", proc.stderr, file=sys.stderr)
        sys.exit(1)
    resp = json.loads(proc.stdout)

    statement_id = resp.get("statement_id")
    state = resp.get("status", {}).get("state")
    while state in ("PENDING", "RUNNING"):
        time.sleep(2)
        proc = subprocess.run(
            ["databricks", "api", "get", f"/api/2.0/sql/statements/{statement_id}", "--profile", profile],
            capture_output=True,
            text=True,
        )
        resp = json.loads(proc.stdout)
        state = resp.get("status", {}).get("state")

    if state != "SUCCEEDED":
        print("SQL FAILED:", json.dumps(resp, indent=2), file=sys.stderr)
        sys.exit(1)
    return resp


if __name__ == "__main__":
    stmt = sys.argv[1]
    result = run_sql(stmt)
    print(json.dumps(result, indent=2))
