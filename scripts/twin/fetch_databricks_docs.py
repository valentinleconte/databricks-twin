import io
import os
import re
import sys

import httpx
from bs4 import BeautifulSoup
from markitdown import MarkItDown

# Self-referential corpus, same trick as openrag-twin's OpenSearch docs: feed the RAG agent
# with the documentation of the platform pieces (Unity Catalog, Vector Search, Genie, MCP,
# Mosaic AI) that actually power it.
URLS = [
    "https://docs.databricks.com/aws/en/lakehouse",
    "https://docs.databricks.com/aws/en/tables/delta-table",
    "https://docs.databricks.com/aws/en/vector-search/vector-search",
    "https://docs.databricks.com/aws/en/generative-ai/agent-framework/unstructured-retrieval-tools",
    "https://docs.databricks.com/aws/en/agents/agent-framework/structured-retrieval-tools",
    "https://docs.databricks.com/aws/en/generative-ai/mcp/managed-mcp",
    "https://docs.databricks.com/aws/en/generative-ai/agent-framework/agent-tool",
    "https://docs.databricks.com/aws/en/generative-ai/guide/mosaic-ai-gen-ai-capabilities",
    "https://docs.databricks.com/aws/en/getting-started/gen-ai-llm-agent",
    "https://docs.databricks.com/aws/en/oltp/projects/",
    "https://docs.databricks.com/aws/en/generative-ai/agent-framework/create-custom-tool",
]

OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else "databricks-docs-md"
os.makedirs(OUT_DIR, exist_ok=True)

md_converter = MarkItDown()


def slug_from_url(url: str) -> str:
    path = url.replace("https://docs.databricks.com/aws/en/", "").strip("/")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", path).strip("-") or "index"
    return slug


results = []
for url in URLS:
    try:
        r = httpx.get(
            url, follow_redirects=True, timeout=30, headers={"User-Agent": "databricks-twin/1.0"}
        )
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        main = soup.find("main") or soup.body
        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else url
        for tag in main.find_all(["nav", "aside", "script", "style", "button", "footer"]):
            tag.decompose()
        html_str = str(main)
        result = md_converter.convert_stream(
            io.BytesIO(html_str.encode("utf-8")), file_extension=".html"
        )
        content = result.text_content.strip()

        slug = slug_from_url(url)
        filename = f"{slug}.md"
        filepath = os.path.join(OUT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"---\ntitle: {title}\nsource_url: {url}\n---\n\n")
            f.write(f"# {title}\n\n")
            f.write(f"Source: {url}\n\n")
            f.write(content)
            f.write("\n")

        results.append((url, filepath, len(content), True, None))
        print(f"OK  {url} -> {filepath} ({len(content)} chars)")
    except Exception as e:  # noqa: BLE001 — one bad page (network, parsing, HTTP error) shouldn't abort the batch
        results.append((url, None, 0, False, str(e)))
        print(f"FAIL {url}: {e}")

ok = sum(1 for r in results if r[3])
print(f"\n{ok}/{len(URLS)} pages converties avec succès dans {OUT_DIR}/")
