---
title: Databricksmanaged MCP servers
source_url: https://docs.databricks.com/aws/en/generative-ai/mcp/managed-mcp
---

# Databricksmanaged MCP servers

Source: https://docs.databricks.com/aws/en/generative-ai/mcp/managed-mcp

Last updated on **Aug 17, 2026**

# Databricks managed MCP servers

Preview

This feature is in [Public Preview](/aws/en/release-notes/release-types).

Databricks managed MCP servers are ready-to-use servers that connect your AI agents to data in Unity Catalog, Databricks AI Search indexes, Genie Agents, and custom functions.

* **No setup**: Databricks hosts the servers and manages authentication.
* **Governed**: Unity Catalog enforces permissions, so agents and users access only the tools and data you grant them.
* **Centralized**: view, monitor, and manage every server from [Unity AI Gateway](/aws/en/ai-gateway/).

To call these servers from agent code, see [Use MCP servers in Custom Agents](/aws/en/agents/mcp-tools/use-mcp-in-agents).

If you are setting up a third-party coding agent such as Claude Code or Cursor, pair these servers with [Databricks AI tools](/aws/en/agent-skills/#ai-tools-and-mcp). Managed MCP servers give the agent governed tools to call. AI tools teaches it the Databricks patterns to apply when it writes code.

## Available managed servers[​](#available-managed-servers "Direct link to available-managed-servers")

Databricks has the following MCP servers that work out of the box. When connecting to managed MCP servers using [on-behalf-of user authentication](/aws/en/agents/custom-agents/model-serving/agent-authentication-model-serving#on-behalf-of-user-authentication), include the corresponding OAuth scope for each server your application needs to access. For setup instructions, see [Authentication methods](/aws/en/agents/mcp-tools/connect-clients#set-up-authentication).

|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Server Use case URL pattern OAuth scope|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | [Genie One](/aws/en/agents/mcp-tools/genie-mcp) Natural-language analytics across your workspace `https://<workspace-hostname>/api/2.0/mcp/genie` `genie`|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | [Genie Agent](/aws/en/agents/mcp-tools/genie-agent) Natural-language analytics scoped to one Genie Agent `https://<workspace-hostname>/api/2.0/mcp/genie/{genie_space_id}` `genie`|  |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | [AI Search](/aws/en/agents/mcp-tools/ai-search) Retrieval over unstructured documents `https://<workspace-hostname>/api/2.0/mcp/ai-search/{catalog}/{schema}/{index_name}` `ai-search`|  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | | [Databricks SQL](/aws/en/agents/mcp-tools/databricks-sql) Developer queries and data engineering `https://<workspace-hostname>/api/2.0/mcp/sql` `sql`|  |  |  |  | | --- | --- | --- | --- | | [Unity Catalog functions](/aws/en/agents/mcp-tools/uc-functions) Predefined SQL logic as tools `https://<workspace-hostname>/api/2.0/mcp/functions/{catalog}/{schema}/{function_name}` `unity-catalog` | | | | | | | | | | | | | | | | | | | | | | | |

|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Server Use case URL pattern OAuth scope|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | [Genie One](/aws/en/agents/mcp-tools/genie-mcp) Natural-language analytics across your workspace `https://<workspace-hostname>/api/2.0/mcp/genie` `genie`|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | [Genie Agent](/aws/en/agents/mcp-tools/genie-agent) Natural-language analytics scoped to one Genie Agent `https://<workspace-hostname>/api/2.0/mcp/genie/{genie_space_id}` `genie`|  |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | [AI Search](/aws/en/agents/mcp-tools/ai-search) Retrieval over unstructured documents `https://<workspace-hostname>/api/2.0/mcp/ai-search/{catalog}/{schema}/{index_name}` `ai-search`|  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | | [Databricks SQL](/aws/en/agents/mcp-tools/databricks-sql) Developer queries and data engineering `https://<workspace-hostname>/api/2.0/mcp/sql` `sql`|  |  |  |  | | --- | --- | --- | --- | | [Unity Catalog functions](/aws/en/agents/mcp-tools/uc-functions) Predefined SQL logic as tools `https://<workspace-hostname>/api/2.0/mcp/functions/{catalog}/{schema}/{function_name}` `unity-catalog` | | | | | | | | | | | | | | | | | | | | | | | |

To connect clients such as Cursor, Claude Desktop, or ChatGPT to any of these servers, see [Connect MCPs to AI assistants and coding agents](/aws/en/agents/mcp-tools/connect-clients).

## Genie One MCP vs. Databricks SQL MCP servers[​](#genie-one-mcp-vs-databricks-sql-mcp-servers "Direct link to genie-one-mcp-vs-databricks-sql-mcp-servers")

For analytics use cases, start with the [Genie One MCP server](/aws/en/agents/mcp-tools/genie-mcp). Genie resolves business terms through Genie Ontology, your governed semantic layer, which produces more accurate answers than an agent writing SQL directly against raw tables. Use the [Databricks SQL MCP server](/aws/en/agents/mcp-tools/databricks-sql) when you need to run a specific query you already wrote, such as validating syntax or authoring a pipeline.

## Tool call arguments vs. `_meta` parameters[​](#tool-call-arguments-vs-_meta-parameters "Direct link to tool-call-arguments-vs-_meta-parameters")

Databricks managed MCP servers handle parameters in two ways:

* **Tool call arguments**: Parameters that an LLM typically generates dynamically based on user input
* **`_meta` parameters**: Configuration parameters that you can preset in your agent code to set behavior deterministically

For the specific `_meta` parameters each server supports, see that server's page (for example, [AI Search](/aws/en/agents/mcp-tools/ai-search) or [Databricks SQL](/aws/en/agents/mcp-tools/databricks-sql)).

## Pricing[​](#pricing "Direct link to Pricing")

Managed MCP server pricing depends on the type of feature:

* Unity Catalog functions use [serverless general compute pricing](https://www.databricks.com/product/pricing/datascience-ml).
* Genie Agents use [serverless SQL compute pricing](https://www.databricks.com/product/pricing/databricks-sql).
* Databricks SQL servers use [Databricks SQL pricing](https://www.databricks.com/product/pricing/databricks-sql).
* AI Search indexes use [AI Search pricing](https://www.databricks.com/product/pricing/vector-search).

## Additional resources[​](#-additional-resources "Direct link to -additional-resources")

* [Use MCP servers in Custom Agents](/aws/en/agents/mcp-tools/use-mcp-in-agents) to call managed MCP servers from agent code.
* [Connect MCPs to AI assistants and coding agents](/aws/en/agents/mcp-tools/connect-clients) to connect clients like Cursor and Claude Desktop.
* [Agent skills for AI coding assistants](/aws/en/agent-skills/) to teach coding agents Databricks development patterns.

On this page

* [Available managed servers](#available-managed-servers)* [Genie One MCP vs. Databricks SQL MCP servers](#genie-one-mcp-vs-databricks-sql-mcp-servers)* [Tool call arguments vs. `_meta` parameters](#tool-call-arguments-vs-_meta-parameters)* [Pricing](#pricing)* [Additional resources](#-additional-resources)
