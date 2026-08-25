---
title: Create agent tools usingUnity Catalogfunctions
source_url: https://docs.databricks.com/aws/en/generative-ai/agent-framework/create-custom-tool
---

# Create agent tools usingUnity Catalogfunctions

Source: https://docs.databricks.com/aws/en/generative-ai/agent-framework/create-custom-tool

Last updated on **Aug 3, 2026**

# Create agent tools using Unity Catalog functions

Use Unity Catalog functions to create agent tools that execute custom logic and perform specific tasks that extend the capabilities of LLMs beyond language generation.

## When to use Unity Catalog functions vs. MCP servers[​](#when-to-use-unity-catalog-functions-vs-mcp-servers "Direct link to when-to-use-unity-catalog-functions-vs-mcp-servers")

Databricks recommends using Unity Catalog functions as agent tools specifically for structured data retrieval tools when the query is known ahead of time and the agent provides the parameters. See [Connect agents to structured data](/aws/en/agents/custom-agents/structured-retrieval-tools).

In most other use cases, Databricks recommends MCP servers or defining the logic directly in agent code for faster execution, per-user authentication support, and additional flexibility.

## Requirements[​](#requirements "Direct link to Requirements")

To create and use Unity Catalog functions as agent tools, you need the following:

* **Databricks Runtime**: Use Databricks Runtime 15.0 and above
* **Python version**: Install Python 3.10 or above

To run Unity Catalog functions:

* **Serverless compute** must be enabled in your workspace to execute Unity Catalog functions as agent tools in production. See [Serverless compute requirements](/aws/en/compute/serverless/#requirements).
  + [Local mode execution](#local-mode) for Python functions does not require serverless generic compute to run, however local mode is only intended for development and testing purposes.

To create Unity Catalog functions:

* **Serverless generic compute** must be enabled in your workspace to create functions using the Databricks Workspace Client or SQL body statements.
  + Python functions can be created without serverless compute.

## Create a Unity Catalog function tool[​](#create-a-unity-catalog-function-tool "Direct link to create-a-unity-catalog-function-tool")

The following steps show how to create and test a Unity Catalog function. Run the following code in a Databricks notebook.

prompt

Tell [Genie Code](/aws/en/genie-code/) (Agent mode) to do this for you:

```
Create a Unity Catalog Python function that an AI agent can use as a tool. It should take two floating point numbers and return their sum, with type hints and a Google-style docstring. Register it using the Databricks Function Client, then test calling it.
```

### Install dependencies[​](#install-dependencies "Direct link to Install dependencies")

Install Unity Catalog AI packages with the `[databricks]` extra.

Python

```
# Install Unity Catalog AI integration packages with the Databricks extra
%pip install unitycatalog-ai[databricks]

dbutils.library.restartPython()
```

### Initialize the Databricks Function Client[​](#initialize-the-databricks-function-client "Direct link to Initialize the Databricks Function Client")

Initialize the [Databricks Function Client](https://docs.unitycatalog.io/ai/client/#databricks-function-client), which is a specialized interface for creating, managing, and running Unity Catalog functions in Databricks.

Python

```
from unitycatalog.ai.core.databricks import DatabricksFunctionClient

client = DatabricksFunctionClient()
```

### Define the tool's logic[​](#define-the-tools-logic "Direct link to Define the tool's logic")

Unity Catalog tools are really just Unity Catalog user-defined functions (UDFs) under the hood. When you define a Unity Catalog tool, you're registering a function in Unity Catalog. To learn more about Unity Catalog UDFs, see [SQL and Python user-defined functions (UDFs) in Unity Catalog](/aws/en/udf/unity-catalog).

warning

Executing arbitrary code in an agent tool can expose sensitive or private information that the agent has access to. Customers are responsible for running only trusted code and configuring guardrails and appropriate permissions to prevent unintended access to data.

You can create Unity Catalog functions using one of two APIs:

* `create_python_function` accepts a Python callable.
* `create_function` accepts a SQL body create function statement. See [Create Python functions](/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-sql-function#create-python-functions).

Use the `create_python_function` API to create the function.

To make a Python callable recognizable to the Unity Catalog functions data model, your function must meet the following requirements:

* **Type hints**: The function signature must define valid Python type hints. Both the named arguments and the return value must have their types defined.
* **Do not use variable arguments**: Variable arguments such as \*args and \*\*kwargs are not supported. All arguments must be explicitly defined.
* **Type compatibility**: Not all Python types are supported in SQL. See [Spark Supported Data Types](https://spark.apache.org/docs/latest/sql-ref-datatypes.html).
* **Descriptive docstrings**: The Unity Catalog functions toolkit reads, parses, and extracts important information from your docstring.
  + Docstrings must be formatted according to the [Google docstring syntax](https://google.github.io/styleguide/pyguide.html#383-functions-and-methods).
  + Write clear descriptions for your function and its arguments to help the LLM understand how and when to use the function.
* **Dependency imports**: Libraries must be imported within the function's body. Imports outside the function will not be resolved when running the tool.

The following code snippets uses the `create_python_function` to register the Python callable `add_numbers`:

Python

```
CATALOG = "my_catalog"
SCHEMA = "my_schema"

def add_numbers(number_1: float, number_2: float) -> float:
  """
  A function that accepts two floating point numbers adds them,
  and returns the resulting sum as a float.

  Args:
    number_1 (float): The first of the two numbers to add.
    number_2 (float): The second of the two numbers to add.

  Returns:
    float: The sum of the two input numbers.
  """
  return number_1 + number_2

function_info = client.create_python_function(
  func=add_numbers,
  catalog=CATALOG,
  schema=SCHEMA,
  replace=True
)
```

### Test the function[​](#test-the-function "Direct link to Test the function")

Test your function to check it works as expected. Specify a fully qualified function name in the `execute_function` API to run the function:

Python

```
result = client.execute_function(
  function_name=f"{CATALOG}.{SCHEMA}.add_numbers",
  parameters={"number_1": 36939.0, "number_2": 8922.4}
)

result.value # OUTPUT: '45861.4'
```

## Add Unity Catalog functions to your agent[​](#add-unity-catalog-functions-to-your-agent "Direct link to add-unity-catalog-functions-to-your-agent")

Once you have created and tested your Unity Catalog function, choose one of the following approaches to add it to your agent.

![Mcp icon.](data:image/svg+xml;base64...) **Using MCP (recommended)**

### Using MCP (recommended)[​](#using-mcp-recommended "Direct link to Using MCP (recommended)")

Databricks recommends using MCP servers to add Unity Catalog functions to your agent. The MCP approach provides a simpler integration with automatic tool discovery and built-in authentication support.

The managed MCP URL for Unity Catalog functions is: `https://<workspace-hostname>/api/2.0/mcp/functions/{catalog}/{schema}`. You can optionally specify a specific function by appending `/{function_name}`.

The following examples show how to connect your agent to Unity Catalog functions through MCP. Replace `<catalog>` and `<schema>` with the location of your functions.

* OpenAI Agents SDK (Apps)* LangGraph (Apps)* Model Serving

Python

```
from agents import Agent, Runner
from databricks.sdk import WorkspaceClient
from databricks_openai.agents import McpServer

workspace_client = WorkspaceClient()

async with McpServer.from_uc_function(
    catalog="<catalog>",
    schema="<schema>",
    workspace_client=workspace_client,
    name="uc-functions",
) as uc_server:
    agent = Agent(
        name="Tool-using agent",
        instructions="You are a helpful assistant. Use the available tools to answer questions.",
        model="databricks-claude-sonnet-4-5",
        mcp_servers=[uc_server],
    )
    result = await Runner.run(agent, "Look up customer info for Acme Corp")
    print(result.final_output)
```

Grant the app access to the Unity Catalog function in `databricks.yml`:

YAML

```
resources:
  apps:
    my_agent_app:
      resources:
        - name: 'my_uc_function'
          uc_securable:
            securable_full_name: '<catalog>.<schema>.<function-name>'
            securable_type: 'FUNCTION'
            permission: 'EXECUTE'
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
        name="uc-functions",
        url=f"{host}/api/2.0/mcp/functions/<catalog>/<schema>",
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
        {"messages": [{"role": "user", "content": "Look up customer info for Acme Corp"}]}
    )
    print(result["messages"][-1].content)
```

Grant the app access to the Unity Catalog function in `databricks.yml`:

YAML

```
resources:
  apps:
    my_agent_app:
      resources:
        - name: 'my_uc_function'
          uc_securable:
            securable_full_name: '<catalog>.<schema>.<function-name>'
            securable_type: 'FUNCTION'
            permission: 'EXECUTE'
```

Python

```
from databricks.sdk import WorkspaceClient
from databricks_mcp import DatabricksMCPClient
import mlflow

workspace_client = WorkspaceClient()
host = workspace_client.config.host

# Connect to the UC functions MCP server
mcp_client = DatabricksMCPClient(
    server_url=f"{host}/api/2.0/mcp/functions/<catalog>/<schema>",
    workspace_client=workspace_client,
)

# List available tools
tools = mcp_client.list_tools()

# Log the agent with the required resources for deployment
mlflow.pyfunc.log_model(
    "agent",
    python_model=my_agent,
    resources=mcp_client.get_databricks_resources(),
)
```

To deploy the agent, see [Deploy an agent for AI applications (Model Serving)](/aws/en/agents/custom-agents/model-serving/deploy-agent). For details on logging agents with MCP resources, see [Databricks managed MCP servers](/aws/en/agents/mcp-tools/managed-mcp).

![Function icon.](data:image/svg+xml;base64...) **Using UCFunctionToolkit**

### Using UCFunctionToolkit[​](#using-ucfunctiontoolkit "Direct link to Using UCFunctionToolkit")

This example uses LangChain, but a similar approach can be applied to other libraries. See [Unity Catalog tool integration](/aws/en/agents/custom-agents/unity-catalog-tool-integration).

#### Install additional dependencies[​](#install-additional-dependencies "Direct link to Install additional dependencies")

Install the LangChain integration packages for UCFunctionToolkit.

Python

```
%pip install unitycatalog-langchain[databricks]==0.2.0

# Install the Databricks LangChain integration package
%pip install databricks-langchain==0.5.0

dbutils.library.restartPython()
```

#### Wrap the function using the UCFunctionToolKit[​](#-wrap-the-function-using-the-ucfunctiontoolkit "Direct link to -wrap-the-function-using-the-ucfunctiontoolkit")

Wrap the function using the `UCFunctionToolkit` to make it accessible to agent authoring libraries. The toolkit ensures consistency across different AI libraries and adds helpful features like auto-tracing for retrievers.

Python

```
from databricks_langchain import UCFunctionToolkit

# Create a toolkit with the Unity Catalog function
func_name = f"{CATALOG}.{SCHEMA}.add_numbers"
toolkit = UCFunctionToolkit(function_names=[func_name])

tools = toolkit.tools
```

#### Use the tool in an agent[​](#use-the-tool-in-an-agent "Direct link to Use the tool in an agent")

Add the tool to a LangChain agent using the `tools` property from `UCFunctionToolkit`.

note

This example uses LangChain. However you can integrate Unity Catalog tools with other frameworks such as LlamaIndex, OpenAI, Anthropic, and more. See [Unity Catalog tool integration](/aws/en/agents/custom-agents/unity-catalog-tool-integration).

This example authors a simple agent using LangChain `AgentExecutor` API for simplicity. For production workloads, use the agent authoring workflow seen in [Author an agent and deploy it on Databricks Apps](/aws/en/agents/custom-agents/author-agent).

Python

```
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from databricks_langchain import (
  ChatDatabricks,
  UCFunctionToolkit,
)
import mlflow

# Initialize the LLM (optional: replace with your LLM of choice)
LLM_ENDPOINT_NAME = "databricks-meta-llama-3-3-70b-instruct"
llm = ChatDatabricks(endpoint=LLM_ENDPOINT_NAME, temperature=0.1)

# Define the prompt
prompt = ChatPromptTemplate.from_messages(
  [
    (
      "system",
      "You are a helpful assistant. Make sure to use tools for additional functionality.",
    ),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
  ]
)

# Enable automatic tracing
mlflow.langchain.autolog()

# Define the agent, specifying the tools from the toolkit above
agent = create_tool_calling_agent(llm, tools, prompt)

# Create the agent executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
agent_executor.invoke({"input": "What is 36939.0 + 8922.4?"})
```

## Improve tool-calling with clear documentation[​](#-improve-tool-calling-with-clear-documentation "Direct link to -improve-tool-calling-with-clear-documentation")

Good documentation helps your agents know when and how to use each tool. Follow these best practices for documenting your tools:

* For Unity Catalog functions, use the `COMMENT` clause to describe tool functionality and parameters.
* Clearly define expected inputs and outputs.
* Write meaningful descriptions to make tools easier for agents, and humans, to use.

### Example: Effective tool documentation[​](#example-effective-tool-documentation "Direct link to Example: Effective tool documentation")

The following example shows clear `COMMENT` strings for a tool that queries a structured table.

SQL

```
CREATE OR REPLACE FUNCTION main.default.lookup_customer_info(
  customer_name STRING COMMENT 'Name of the customer whose info to look up.'
)
RETURNS STRING
COMMENT 'Returns metadata about a specific customer including their email and ID.'
RETURN SELECT CONCAT(
    'Customer ID: ', customer_id, ', ',
    'Customer Email: ', customer_email
  )
  FROM main.default.customer_data
  WHERE customer_name = customer_name
  LIMIT 1;
```

### Example: Ineffective tool documentation[​](#example-ineffective-tool-documentation "Direct link to Example: Ineffective tool documentation")

The following example lacks important details, making it harder for agents to use the tool effectively:

SQL

```
CREATE OR REPLACE FUNCTION main.default.lookup_customer_info(
  customer_name STRING COMMENT 'Name of the customer.'
)
RETURNS STRING
COMMENT 'Returns info about a customer.'
RETURN SELECT CONCAT(
    'Customer ID: ', customer_id, ', ',
    'Customer Email: ', customer_email
  )
  FROM main.default.customer_data
  WHERE customer_name = customer_name
  LIMIT 1;
```

## Run functions using serverless or local mode[​](#run-functions-using-serverless-or-local-mode "Direct link to Run functions using serverless or local mode")

When an AI service determines a tool call is needed, integration packages (`UCFunctionToolkit` instances) run the `DatabricksFunctionClient.execute_function` API.

The `execute_function` call can run functions in two execution modes: serverless or local. This mode determines which resource runs the function.

### Serverless mode for production[​](#serverless-mode-for-production "Direct link to Serverless mode for production")

Serverless mode is the default and recommended option for production use cases when executing Unity Catalog functions as agent tools. This mode uses serverless generic compute (Spark Connect serverless) to execute functions remotely, and [Lakeguard](/aws/en/compute/lakeguard) ensures that your agent's process remains secure and free from the risks of running arbitrary code locally.

note

Unity Catalog functions executed as agent tools require serverless generic compute (Spark Connect serverless), not serverless SQL warehouses. Attempts to run tools without serverless generic compute will produce errors like `PERMISSION_DENIED: Cannot access Spark Connect`.

Python

```
# Defaults to serverless if `execution_mode` is not specified
client = DatabricksFunctionClient(execution_mode="serverless")
```

When your agent requests a tool execution in **serverless** mode, the following happens:

1. The `DatabricksFunctionClient` sends a request to Unity Catalog to retrieve the function definition if the definition has not been locally cached.
2. The `DatabricksFunctionClient` extracts the function definition and validates the parameter names and types.
3. The `DatabricksFunctionClient` submits the execution as a UDF to serverless generic compute.

### Local mode for development[​](#local-mode-for-development "Direct link to local-mode-for-development")

Local mode executes Python functions in a local subprocess instead of making requests to serverless generic compute. This allows you to troubleshoot tool calls more effectively by providing local stack traces. It is designed for developing and debugging Python Unity Catalog functions.

When your agent requests running a tool in **local** mode, the `DatabricksFunctionClient` does the following:

1. Sends a request to Unity Catalog to retrieve the function definition if the definition has not been locally cached.
2. Extracts the Python callable definition, caches the callable locally, and validates the parameter names and types.
3. Invokes the callable with the specified parameters in a restricted subprocess with timeout protection.

Python

```
# Defaults to serverless if `execution_mode` is not specified
client = DatabricksFunctionClient(execution_mode="local")
```

Running in `"local"` mode provides the following features:

* **CPU time limit:** Restricts the total CPU runtime for callable execution to prevent excessive computational loads.

  The CPU time limit is based on actual CPU usage, not wall-clock time. Due to system scheduling and concurrent processes, CPU time can exceed wall-clock time in real-world scenarios.
* **Memory limit:** Restricts the virtual memory allocated to the process.
* **Timeout protection:** Enforces a total wall-clock timeout for running functions.

Customize these limits using environment variables (read further).

### Local mode limitations[​](#local-mode-limitations "Direct link to Local mode limitations")

* **Python functions only**: SQL-based functions are not supported in local mode.
* **Security considerations for untrusted code**: While local mode runs functions in a subprocess for process isolation, there is a potential security risk when executing arbitrary code generated by AI systems. This is primarily a concern when functions execute dynamically generated Python code that hasn't been reviewed.
* **Library version differences**: Library versions may differ between serverless and local execution environments, which could lead to different function behavior.

## Environment variables[​](#environment-variables "Direct link to environment-variables")

Configure how functions run in the `DatabricksFunctionClient` using the following environment variables:

|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Environment variable** **Default value** **Description**|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | `EXECUTOR_MAX_CPU_TIME_LIMIT` `10` seconds Maximum allowable CPU execution time (local mode only).|  |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | `EXECUTOR_MAX_MEMORY_LIMIT` `100` MB Maximum allowable virtual memory allocation for the process (local mode only).|  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | | `EXECUTOR_TIMEOUT` `20` seconds Maximum total wall clock time (local mode only).|  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | | `UCAI_DATABRICKS_SESSION_RETRY_MAX_ATTEMPTS` `5` The Maximum number of attempts to retry refreshing the session client in case of token expiry.|  |  |  | | --- | --- | --- | | `UCAI_DATABRICKS_SERVERLESS_EXECUTION_RESULT_ROW_LIMIT` `100` The Maximum number of rows to return when running functions using serverless compute and `databricks-connect`. | | | | | | | | | | | | | | | | | |

|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Environment variable** **Default value** **Description**|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | `EXECUTOR_MAX_CPU_TIME_LIMIT` `10` seconds Maximum allowable CPU execution time (local mode only).|  |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | `EXECUTOR_MAX_MEMORY_LIMIT` `100` MB Maximum allowable virtual memory allocation for the process (local mode only).|  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | | `EXECUTOR_TIMEOUT` `20` seconds Maximum total wall clock time (local mode only).|  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | | `UCAI_DATABRICKS_SESSION_RETRY_MAX_ATTEMPTS` `5` The Maximum number of attempts to retry refreshing the session client in case of token expiry.|  |  |  | | --- | --- | --- | | `UCAI_DATABRICKS_SERVERLESS_EXECUTION_RESULT_ROW_LIMIT` `100` The Maximum number of rows to return when running functions using serverless compute and `databricks-connect`. | | | | | | | | | | | | | | | | | |

## Call external APIs with `http_request` (legacy)[​](#call-external-apis-with-http_request-legacy "Direct link to call-external-apis-with-http_request-legacy")

You can create a Unity Catalog function that wraps `http_request()` to call external services from SQL-based tool definitions. This approach remains supported but is no longer recommended for new integrations. For the walkthrough, including the SQL example and connection-type limitations, see [Unity Catalog function tools with HTTP connection](/aws/en/agents/mcp-tools/uc-function-http).

## Example notebooks[​](#example-notebooks "Direct link to Example notebooks")

The following notebooks demonstrate creating agent tools that connect to external services using Unity Catalog functions.

#### Slack messaging agent tool

[Open notebook in new tab](https://docs.databricks.com/aws/en/notebooks/source/generative-ai/slack-agent-tool.html)[Open in Databricks](https://login.databricks.com/signin?destination_url=%2Fopen%3Fp%3DeyJhY3Rpb24iOiJpbXBvcnRub3RlYm9vayIsInBheWxvYWQiOnsidXJsIjoiaHR0cHM6Ly9kb2NzLmRhdGFicmlja3MuY29tL2F3cy9lbi9ub3RlYm9va3Mvc291cmNlL2dlbmVyYXRpdmUtYWkvc2xhY2stYWdlbnQtdG9vbC5odG1sIn19&utm_source=open-in-databricks&utm_medium=docs&utm_campaign=docs%2Fagents%2Fcustom-agents%2Fcreate-custom-tool&utm_content=https%3A%2F%2Fdocs.databricks.com%2Faws%2Fen%2Fnotebooks%2Fsource%2Fgenerative-ai%2Fslack-agent-tool.html)

#### Microsoft Graph API agent tool

[Open notebook in new tab](https://docs.databricks.com/aws/en/notebooks/source/generative-ai/microsoft-graph-api-agent-tool.html)[Open in Databricks](https://login.databricks.com/signin?destination_url=%2Fopen%3Fp%3DeyJhY3Rpb24iOiJpbXBvcnRub3RlYm9vayIsInBheWxvYWQiOnsidXJsIjoiaHR0cHM6Ly9kb2NzLmRhdGFicmlja3MuY29tL2F3cy9lbi9ub3RlYm9va3Mvc291cmNlL2dlbmVyYXRpdmUtYWkvbWljcm9zb2Z0LWdyYXBoLWFwaS1hZ2VudC10b29sLmh0bWwifX0%253D&utm_source=open-in-databricks&utm_medium=docs&utm_campaign=docs%2Fagents%2Fcustom-agents%2Fcreate-custom-tool&utm_content=https%3A%2F%2Fdocs.databricks.com%2Faws%2Fen%2Fnotebooks%2Fsource%2Fgenerative-ai%2Fmicrosoft-graph-api-agent-tool.html)

#### Azure AI Search agent tool

[Open notebook in new tab](https://docs.databricks.com/aws/en/notebooks/source/generative-ai/azure-ai-search-agent-tool.html)[Open in Databricks](https://login.databricks.com/signin?destination_url=%2Fopen%3Fp%3DeyJhY3Rpb24iOiJpbXBvcnRub3RlYm9vayIsInBheWxvYWQiOnsidXJsIjoiaHR0cHM6Ly9kb2NzLmRhdGFicmlja3MuY29tL2F3cy9lbi9ub3RlYm9va3Mvc291cmNlL2dlbmVyYXRpdmUtYWkvYXp1cmUtYWktc2VhcmNoLWFnZW50LXRvb2wuaHRtbCJ9fQ%253D%253D&utm_source=open-in-databricks&utm_medium=docs&utm_campaign=docs%2Fagents%2Fcustom-agents%2Fcreate-custom-tool&utm_content=https%3A%2F%2Fdocs.databricks.com%2Faws%2Fen%2Fnotebooks%2Fsource%2Fgenerative-ai%2Fazure-ai-search-agent-tool.html)

## Next steps[​](#next-steps "Direct link to Next steps")

* Add Unity Catalog tools to agents programmatically. See [Author an agent and deploy it on Databricks Apps](/aws/en/agents/custom-agents/author-agent).
* Add Unity Catalog tools to agents using the AI Playground UI. See [Get started: Query LLMs and prototype agents with no code](/aws/en/getting-started/gen-ai-llm-agent).
* Manage Unity Catalog functions using the Function Client. See [Unity Catalog documentation - Function client](https://docs.unitycatalog.io/ai/client/#unity-catalog-function-client)
* [Connect agents to third-party tools with MCP Services](/aws/en/agents/mcp-tools/mcp-services) for an overview of all approaches to connect agents to external services.

On this page

* [When to use Unity Catalog functions vs. MCP servers](#when-to-use-unity-catalog-functions-vs-mcp-servers)* [Requirements](#requirements)* [Create a Unity Catalog function tool](#create-a-unity-catalog-function-tool)
      + [Install dependencies](#install-dependencies)+ [Initialize the Databricks Function Client](#initialize-the-databricks-function-client)+ [Define the tool's logic](#define-the-tools-logic)+ [Test the function](#test-the-function)* [Add Unity Catalog functions to your agent](#add-unity-catalog-functions-to-your-agent)
        + [Using MCP (recommended)](#using-mcp-recommended)+ [Using UCFunctionToolkit](#using-ucfunctiontoolkit)* [Improve tool-calling with clear documentation](#-improve-tool-calling-with-clear-documentation)
          + [Example: Effective tool documentation](#example-effective-tool-documentation)+ [Example: Ineffective tool documentation](#example-ineffective-tool-documentation)* [Run functions using serverless or local mode](#run-functions-using-serverless-or-local-mode)
            + [Serverless mode for production](#serverless-mode-for-production)+ [Local mode for development](#local-mode-for-development)+ [Local mode limitations](#local-mode-limitations)* [Environment variables](#environment-variables)* [Call external APIs with `http_request` (legacy)](#call-external-apis-with-http_request-legacy)* [Example notebooks](#example-notebooks)* [Next steps](#next-steps)
