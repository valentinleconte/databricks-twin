---
title: Connect agents to structured data
source_url: https://docs.databricks.com/aws/en/agents/agent-framework/structured-retrieval-tools
---

# Connect agents to structured data

Source: https://docs.databricks.com/aws/en/agents/agent-framework/structured-retrieval-tools

Last updated on **Aug 3, 2026**

# Connect agents to structured data

Agents often need to query or manipulate structured data to answer questions, update records, or create data pipelines.

Databricks provides multiple approaches for connecting agents to structured data in Unity Catalog tables and external data stores. Use pre-configured MCP servers for immediate access to Genie Agents and SQL warehouses, or build custom tools for specialized workflows.

This page shows how to:

* [Query data in Unity Catalog tables](#genie-space)

* [Use Genie in advanced multi-agent systems](#genie-multi-agent-system)

* [Run SQL against Unity Catalog tables with the Databricks SQL MCP server](#databricks-sql-mcp)
* [Use UC functions to run deterministic, repeatable queries](#sql-function-tool)

## Query data in Unity Catalog tables[​](#query-data-in-unity-catalog-tables "Direct link to query-data-in-unity-catalog-tables")

If your agent needs to query data in Unity Catalog tables, Databricks recommends using Genie Agents. A Genie Agent is a collection of up to 25 Unity Catalog tables that Genie can keep in context and query using natural language. Agents can access the Genie Agent using a pre-configured MCP URL.

To connect to a Genie Agent:

1. Create a Genie Agent with the tables you want to query and share the agent with the users, or service principals, that must access it. See [Create and manage a Genie Agent](/aws/en/genie-agents/set-up).
2. Create an agent and connect it to the pre-configured managed MCP URL for the space: `https://<workspace-hostname>/api/2.0/mcp/genie/{genie_space_id}`.

note

The managed MCP server for Genie invokes Genie as an MCP tool, which means history isn't passed when invoking Genie APIs.

## Add a Genie Agent tool to your agent[​](#add-a-genie-agent-tool-to-your-agent "Direct link to add-a-genie-agent-tool-to-your-agent")

The following examples show how to connect your agent to a Genie Agent MCP server. Replace `<genie-space-id>` with the ID of your Genie Agent.

* OpenAI Agents SDK (Apps)* LangGraph (Apps)* Model Serving

Python

```
from agents import Agent, Runner
from databricks.sdk import WorkspaceClient
from databricks_openai.agents import McpServer

workspace_client = WorkspaceClient()
host = workspace_client.config.host

async with McpServer(
    url=f"{host}/api/2.0/mcp/genie/<genie-space-id>",
    name="genie-space",
    workspace_client=workspace_client,
) as genie_server:
    agent = Agent(
        name="Data analyst agent",
        instructions="You are a data analyst. Use the Genie tool to query structured data and answer questions.",
        model="databricks-claude-sonnet-4-5",
        mcp_servers=[genie_server],
    )
    result = await Runner.run(agent, "What were the top 10 customers by revenue last quarter?")
    print(result.final_output)
```

Grant the app access to the Genie Agent in `databricks.yml`:

YAML

```
resources:
  apps:
    my_agent_app:
      resources:
        - name: 'my_genie_space'
          genie_space:
            space_id: '<genie-space-id>'
            permission: 'CAN_RUN'
```

Python

```
from databricks.sdk import WorkspaceClient
from databricks_langchain import ChatDatabricks, DatabricksMCPServer, DatabricksMultiServerMCPClient
from langgraph.prebuilt import create_react_agent

workspace_client = WorkspaceClient()
host = workspace_client.config.host

mcp_client = DatabricksMultiServerMCPClient([
    DatabricksMCPServer(
        name="genie-space",
        url=f"{host}/api/2.0/mcp/genie/<genie-space-id>",
        workspace_client=workspace_client,
    ),
])

async with mcp_client:
    tools = await mcp_client.get_tools()
    agent = create_react_agent(
        ChatDatabricks(endpoint="databricks-claude-sonnet-4-5"),
        tools=tools,
    )
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "What were the top 10 customers by revenue last quarter?"}]}
    )
    print(result["messages"][-1].content)
```

Grant the app access to the Genie Agent in `databricks.yml`:

YAML

```
resources:
  apps:
    my_agent_app:
      resources:
        - name: 'my_genie_space'
          genie_space:
            space_id: '<genie-space-id>'
            permission: 'CAN_RUN'
```

Python

```
from databricks.sdk import WorkspaceClient
from databricks_mcp import DatabricksMCPClient
import mlflow

workspace_client = WorkspaceClient()
host = workspace_client.config.host

# Connect to the Genie Agent MCP server
mcp_client = DatabricksMCPClient(
    server_url=f"{host}/api/2.0/mcp/genie/<genie-space-id>",
    workspace_client=workspace_client,
)

# List available tools from the Genie Agent
tools = mcp_client.list_tools()

# Log the agent with the required resources for deployment
mlflow.pyfunc.log_model(
    "agent",
    python_model=my_agent,
    resources=mcp_client.get_databricks_resources(),
)
```

To deploy the agent, see [Deploy an agent for AI applications (Model Serving)](/aws/en/agents/custom-agents/model-serving/deploy-agent). For details on logging agents with MCP resources, see [Databricks managed MCP servers](/aws/en/agents/mcp-tools/managed-mcp).

## Genie multi-agent system[​](#genie-multi-agent-system "Direct link to genie-multi-agent-system")

Preview

This feature is in [Public Preview](/aws/en/release-notes/release-types).

For advanced, multi-agent systems, you can also use Genie as an agent rather than integrating it using MCP. When you call Genie as an agent, you can deterministically pass in existing conversation context to Genie.

For a code-first approach, see [Use Genie in multi-agent systems (Model Serving)](/aws/en/agents/custom-agents/model-serving/multi-agent-genie). For a UI-first approach, see [Use Supervisor Agent to create a coordinated multi-agent system](/aws/en/agents/agent-bricks/multi-agent-supervisor).

## Run SQL against Unity Catalog tables with the Databricks SQL MCP server[​](#run-sql-against-unity-catalog-tables-with-the-databricks-sql-mcp-server "Direct link to run-sql-against-unity-catalog-tables-with-the-databricks-sql-mcp-server")

When your agent needs to run AI-generated SQL against Unity Catalog tables through a SQL warehouse, connect it to the Databricks managed Databricks SQL MCP server instead of building a custom tool. The server exposes SQL execution as a tool, and access is governed by Unity Catalog permissions. Connect your agent to the pre-configured managed MCP URL: `https://<workspace-hostname>/api/2.0/mcp/sql`.

For the URL pattern, OAuth scope, `_meta` parameters (such as pinning a specific `warehouse_id`), and connection examples, see [Databricks SQL](/aws/en/agents/mcp-tools/databricks-sql).

## Query data using Unity Catalog SQL function tool[​](#-query-data-using-unity-catalog-sql-function-tool "Direct link to -query-data-using-unity-catalog-sql-function-tool")

Create a structured retrieval tool using Unity Catalog SQL functions when the query is known ahead of time and the agent provides the parameters.

The following example creates a Unity Catalog function called `lookup_customer_info`, which allows an agent to retrieve structured data from a hypothetical `customer_data` table.

Run the following code in a SQL editor.

SQL

```
CREATE OR REPLACE FUNCTION main.default.lookup_customer_info(
  customer_name_input STRING COMMENT 'Name of the customer whose info to look up'
)
RETURNS STRING
COMMENT 'Returns metadata about a particular customer, given the customer''s name, including the customer''s email and ID. The
customer ID can be used for other queries.'
RETURN SELECT CONCAT(
    'Customer ID: ', customer_id, ', ',
    'Customer Email: ', customer_email
  )
  FROM main.default.customer_data
  WHERE customer_name = customer_name_input
  LIMIT 1;
```

After you create a Unity Catalog tool, add it to your agent. See [Create a Unity Catalog function tool](/aws/en/agents/custom-agents/create-custom-tool#create-tool).

On this page

* [Query data in Unity Catalog tables](#query-data-in-unity-catalog-tables)* [Add a Genie Agent tool to your agent](#add-a-genie-agent-tool-to-your-agent)* [Genie multi-agent system](#genie-multi-agent-system)* [Run SQL against Unity Catalog tables with the Databricks SQL MCP server](#run-sql-against-unity-catalog-tables-with-the-databricks-sql-mcp-server)* [Query data using Unity Catalog SQL function tool](#-query-data-using-unity-catalog-sql-function-tool)
