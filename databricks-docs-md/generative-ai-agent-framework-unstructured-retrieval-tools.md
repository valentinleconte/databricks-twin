---
title: Connect agents to unstructured data
source_url: https://docs.databricks.com/aws/en/generative-ai/agent-framework/unstructured-retrieval-tools
---

# Connect agents to unstructured data

Source: https://docs.databricks.com/aws/en/generative-ai/agent-framework/unstructured-retrieval-tools

Last updated on **Aug 3, 2026**

# Connect agents to unstructured data

Agents often need to query unstructured data like document collections, knowledge bases, or text corpora to answer questions and provide context-aware responses.

Databricks provides multiple approaches for connecting agents to unstructured data in AI Search indexes and external vector stores. Use pre-configured MCP servers for immediate access to Databricks AI Search indexes, develop retriever tools locally with AI Bridge packages, or build custom retriever functions for specialized workflows.

Databricks AI Search was formerly known as Databricks Vector Search. The legacy `/api/2.0/mcp/vector-search/` URL prefix continues to work for backwards compatibility.

## Query a Databricks AI Search index using MCP[​](#query-a-databricks-ai-search-index-using-mcp "Direct link to query-a-databricks-ai-search-index-using-mcp")

Use the Databricks-managed AI Search MCP server to give your agent access to a Databricks AI Search index. First, create an index using Databricks-managed embeddings. See [Create AI Search endpoints and indexes](/aws/en/ai-search/create-ai-search).

The managed MCP URL for AI Search is `https://<workspace-hostname>/api/2.0/mcp/ai-search/{catalog}/{schema}/{index_name}`. Connect to it and list the tools it exposes:

Python

```
from databricks.sdk import WorkspaceClient
from databricks_mcp import DatabricksMCPClient

workspace_client = WorkspaceClient()
host = workspace_client.config.host

mcp_client = DatabricksMCPClient(
    server_url=f"{host}/api/2.0/mcp/ai-search/<catalog>/<schema>/<index-name>",
    workspace_client=workspace_client,
)
tools = mcp_client.list_tools()
```

To build and deploy an agent that uses this server, see [Use MCP servers in Custom Agents](/aws/en/agents/mcp-tools/use-mcp-in-agents). Grant the agent `SELECT` on the index's Unity Catalog securable.

## Other approaches[​](#other-approaches "Direct link to Other approaches")

Query a vector search index outside Databricks

### Query a vector search index hosted outside Databricks[​](#query-a-vector-search-index-hosted-outside-databricks "Direct link to query-a-vector-search-index-hosted-outside-databricks")

If your vector index is hosted outside Databricks, you can create a Unity Catalog connection to connect to the external service and use the connection in your agent code. See [Connect agents to third-party tools with MCP Services](/aws/en/agents/mcp-tools/mcp-services).

The following example creates a retriever that calls a vector index hosted outside Databricks for a PyFunc-flavored agent.

1. Create a Unity Catalog Connection to the external service, in this case, Azure.

   SQL

   ```
   CREATE CONNECTION ${connection_name}
   TYPE HTTP
   OPTIONS (
     host 'https://example.search.windows.net',
     base_path '/',
     bearer_token secret ('<secret-scope>','<secret-key>')
   );
   ```
2. Define the retriever tool in agent code using the Unity Catalog connection. This example uses MLflow decorators to enable agent tracing.

   note

   To conform to the MLflow retriever schema, the retriever function should return a `List[Document]` object and use the `metadata` field in the Document class to add additional attributes to the returned document, such as `doc_uri` and `similarity_score`. See [MLflow Document](https://mlflow.org/docs/latest/python_api/mlflow.entities.html#mlflow.entities.Document).

   Python

   ```
   import mlflow
   import json

   from mlflow.entities import Document
   from typing import List, Dict, Any
   from dataclasses import asdict

   class VectorSearchRetriever:
     """
     Class using Databricks AI Search to retrieve relevant documents.
     """

     def __init__(self):
       self.azure_search_index = "hotels_vector_index"

     @mlflow.trace(span_type="RETRIEVER", name="vector_search")
     def __call__(self, query_vector: List[Any], score_threshold=None) -> List[Document]:
       """
       Performs vector search to retrieve relevant chunks.
       Args:
         query: Search query.
         score_threshold: Score threshold to use for the query.

       Returns:
         List of retrieved Documents.
       """
       import requests
       from databricks.sdk import WorkspaceClient

       w = WorkspaceClient()
       json = {
         "count": true,
         "select": "HotelId, HotelName, Description, Category",
         "vectorQueries": [
           {
             "vector": query_vector,
             "k": 7,
             "fields": "DescriptionVector",
             "kind": "vector",
             "exhaustive": true,
           }
         ],
       }

       response = requests.post(
         f"{w.config.host}/api/2.0/unity-catalog/connections/{connection_name}/proxy/indexes/{self.azure_search_index}/docs/search?api-version=2023-07-01-Preview",
         headers={
           **w.config.authenticate(),
           "Content-Type": "application/json",
         },
         json=json,
       ).text

       documents = self.convert_vector_search_to_documents(response, score_threshold)
       return [asdict(doc) for doc in documents]

     @mlflow.trace(span_type="PARSER")
     def convert_vector_search_to_documents(
       self, vs_results, score_threshold
     ) -> List[Document]:
       docs = []

       for item in vs_results.get("value", []):
         score = item.get("@search.score", 0)

         if score >= score_threshold:
           metadata = {
             "score": score,
             "HotelName": item.get("HotelName"),
             "Category": item.get("Category"),
           }

           doc = Document(
             page_content=item.get("Description", ""),
             metadata=metadata,
             id=item.get("HotelId"),
           )
           docs.append(doc)

       return docs
   ```
3. To run the retriever, run the following Python code.

   Python

   ```
   retriever = VectorSearchRetriever()
   query = [0.01944167, 0.0040178085 . . .  TRIMMED FOR BREVITY 010858015, -0.017496133]
   results = retriever(query, score_threshold=0.1)
   ```

Develop a local retriever

### Develop a retriever locally using AI Bridge[​](#develop-a-retriever-locally-using-ai-bridge "Direct link to develop-a-retriever-locally-using-ai-bridge")

To build a Databricks AI Search retriever tool locally, use [Databricks AI Bridge packages](https://github.com/databricks/databricks-ai-bridge) like `databricks-langchain` and `databricks-openai`. These packages include helper functions like [`from_vector_search`](https://github.com/search?q=repo:databricks/databricks-ai-bridge+from_vector_search&type=code) and [`from_uc_function`](https://github.com/search?q=repo:databricks/databricks-ai-bridge%20from_uc_function&type=code) to create retrievers from existing Databricks resources.

* LangChain/LangGraph* OpenAI

Install the latest version of `databricks-langchain` that includes Databricks AI Bridge.

Bash

```
%pip install --upgrade databricks-langchain
```

The following code prototypes a retriever tool that queries a hypothetical vector search index and binds it to an LLM locally so you can test its tool-calling behavior.

Provide a descriptive `tool_description` to help the agent understand the tool and determine when to invoke it.

Python

```
from databricks_langchain import VectorSearchRetrieverTool, ChatDatabricks

# Initialize the retriever tool.
vs_tool = VectorSearchRetrieverTool(
  index_name="catalog.schema.my_databricks_docs_index",
  tool_name="databricks_docs_retriever",
  tool_description="Retrieves information about Databricks products from official Databricks documentation."
)

# Run a query against the vector search index locally for testing
vs_tool.invoke("Databricks Agent Framework?")

# Bind the retriever tool to your Langchain LLM of choice
llm = ChatDatabricks(endpoint="databricks-claude-sonnet-4-5")
llm_with_tools = llm.bind_tools([vs_tool])

# Chat with your LLM to test the tool calling functionality
llm_with_tools.invoke("Based on the Databricks documentation, what is Databricks Agent Framework?")
```

For scenarios that use either direct-access indexes or Delta Sync indexes using self-managed embeddings, you must configure the [`VectorSearchRetrieverTool`](https://api-docs.databricks.com/python/databricks-ai-bridge/latest/databricks_langchain.html#databricks_langchain.VectorSearchRetrieverTool) and specify a custom embedding model and text column. See [options for providing embeddings](/aws/en/ai-search/ai-search#options-for-providing-vector-embeddings).

The following example shows you how to configure a `VectorSearchRetrieverTool` with `columns` and `embedding` keys.

Python

```
from databricks_langchain import VectorSearchRetrieverTool
from databricks_langchain import DatabricksEmbeddings

embedding_model = DatabricksEmbeddings(
    endpoint="databricks-bge-large-en",
)

vs_tool = VectorSearchRetrieverTool(
  index_name="catalog.schema.index_name", # Index name in the format 'catalog.schema.index'
  num_results=5, # Max number of documents to return
  columns=["primary_key", "text_column"], # List of columns to include in the search
  filters={"text_column LIKE": "Databricks"}, # Filters to apply to the query
  query_type="ANN", # Query type ("ANN" or "HYBRID").
  tool_name="name of the tool", # Used by the LLM to understand the purpose of the tool
  tool_description="Purpose of the tool", # Used by the LLM to understand the purpose of the tool
  text_column="text_column", # Specify text column for embeddings. Required for direct-access index or delta-sync index with self-managed embeddings.
  embedding=embedding_model # The embedding model. Required for direct-access index or delta-sync index with self-managed embeddings.
)
```

For additional details, see the [API docs](https://api-docs.databricks.com/python/databricks-ai-bridge/latest/databricks_openai.html#databricks_openai.VectorSearchRetrieverTool) for `VectorSearchRetrieverTool`.

Install the latest version of `databricks-openai` that includes Databricks AI Bridge.

Bash

```
%pip install --upgrade databricks-openai
```

The following code prototypes a retriever that queries a hypothetical vector search index and integrates it with OpenAI's GPT models.

Provide a descriptive `tool_description` to help the agent understand the tool and determine when to invoke it.

For more information on OpenAI recommendations for tools, see [OpenAI Function Calling documentation](https://platform.openai.com/docs/guides/function-calling?example=get-weather#handling-function-calls).

Python

```
from databricks_openai import VectorSearchRetrieverTool
from openai import OpenAI
import json

# Initialize OpenAI client
client = OpenAI(api_key=<your_API_key>)

# Initialize the retriever tool
dbvs_tool = VectorSearchRetrieverTool(
  index_name="catalog.schema.my_databricks_docs_index",
  tool_name="databricks_docs_retriever",
  tool_description="Retrieves information about Databricks products from official Databricks documentation"
)

messages = [
  {"role": "system", "content": "You are a helpful assistant."},
  {
    "role": "user",
    "content": "Using the Databricks documentation, answer what is Spark?"
  }
]
first_response = client.chat.completions.create(
  model="gpt-4o",
  messages=messages,
  tools=[dbvs_tool.tool]
)

# Execute function code and parse the model's response and handle function calls.
tool_call = first_response.choices[0].message.tool_calls[0]
args = json.loads(tool_call.function.arguments)
result = dbvs_tool.execute(query=args["query"])  # For self-managed embeddings, optionally pass in openai_client=client

# Supply model with results – so it can incorporate them into its final response.
messages.append(first_response.choices[0].message)
messages.append({
  "role": "tool",
  "tool_call_id": tool_call.id,
  "content": json.dumps(result)
})
second_response = client.chat.completions.create(
  model="gpt-4o",
  messages=messages,
  tools=[dbvs_tool.tool]
)
```

For scenarios that use either direct-access indexes or Delta Sync indexes using self-managed embeddings, you must configure the [`VectorSearchRetrieverTool`](https://api-docs.databricks.com/python/databricks-ai-bridge/latest/databricks_openai.html#databricks_openai.VectorSearchRetrieverTool) and specify a custom embedding model and text column. See [options for providing embeddings](/aws/en/ai-search/ai-search#options-for-providing-vector-embeddings).

The following example shows you how to configure a `VectorSearchRetrieverTool` with `columns` and `embedding` keys.

Python

```
from databricks_openai import VectorSearchRetrieverTool

vs_tool = VectorSearchRetrieverTool(
    index_name="catalog.schema.index_name", # Index name in the format 'catalog.schema.index'
    num_results=5, # Max number of documents to return
    columns=["primary_key", "text_column"], # List of columns to include in the search
    filters={"text_column LIKE": "Databricks"}, # Filters to apply to the query
    query_type="ANN", # Query type ("ANN" or "HYBRID").
    tool_name="name of the tool", # Used by the LLM to understand the purpose of the tool
    tool_description="Purpose of the tool", # Used by the LLM to understand the purpose of the tool
    text_column="text_column", # Specify text column for embeddings. Required for direct-access index or delta-sync index with self-managed embeddings.
    embedding_model_name="databricks-bge-large-en" # The embedding model. Required for direct-access index or delta-sync index with self-managed embeddings.
)
```

For additional details, see the [API docs](https://api-docs.databricks.com/python/databricks-ai-bridge/latest/databricks_openai.html#databricks_openai.VectorSearchRetrieverTool) for `VectorSearchRetrieverTool`.

After your local tool is ready, you can directly productionize it as part of your agent code, or migrate it to a Unity Catalog function, which provides better discoverability and governance but has certain limitations.

Query Databricks AI Search using UC functions (deprecated)

### Query Databricks AI Search using UC functions (deprecated)[​](#query-databricks-ai-search-using-uc-functions-deprecated "Direct link to query-databricks-ai-search-using-uc-functions-deprecated")

note

Databricks recommends MCP servers for most agent tools, but defining tools with Unity Catalog functions remains available for prototyping.

You can create a Unity Catalog function that wraps a [AI Search index](/aws/en/ai-search/query-ai-search) query. This approach:

* Supports production use cases with governance and discoverability
* Uses the [vector\_search()](/aws/en/sql/language-manual/functions/vector_search) SQL function under the hood
* Supports automatic MLflow tracing
  + You must align the function's output to the [MLflow retriever schema](https://mlflow.org/docs/latest/tracing/tracing-schema.html#retriever-spans) by using the `page_content` and `metadata` aliases.
  + Any additional metadata columns must be added to the `metadata` column using the [SQL map function](/aws/en/sql/language-manual/functions/map), rather than as top-level output keys.

Run the following code in a notebook or SQL editor to create the function:

SQL

```
CREATE OR REPLACE FUNCTION main.default.databricks_docs_vector_search (
  -- The agent uses this comment to determine how to generate the query string parameter.
  query STRING
  COMMENT 'The query string for searching Databricks documentation.'
) RETURNS TABLE
-- The agent uses this comment to determine when to call this tool. It describes the types of documents and information contained within the index.
COMMENT 'Executes a search on Databricks documentation to retrieve text documents most relevant to the input query.' RETURN
SELECT
  chunked_text as page_content,
  map('doc_uri', url, 'chunk_id', chunk_id) as metadata
FROM
  vector_search(
    -- Specify your AI Search index name here
    index => 'catalog.schema.databricks_docs_index',
    query => query,
    num_results => 5
  )
```

To use this retriever tool in your agent, wrap it with `UCFunctionToolkit`. This enables automatic tracing through MLflow by automatically generating `RETRIEVER` span types in MLflow logs.

Python

```
from unitycatalog.ai.langchain.toolkit import UCFunctionToolkit

toolkit = UCFunctionToolkit(
    function_names=[
        "main.default.databricks_docs_vector_search"
    ]
)
tools = toolkit.tools
```

Unity Catalog retriever tools have the following caveats:

* SQL clients might limit the maximum number of rows or bytes returned. To prevent data truncation, truncate column values returned by the UDF. For example, you could use `substring(chunked_text, 0, 8192)` to reduce the size of large content columns and avoid row truncation during execution.
* Because this tool is a wrapper for the `vector_search()` function, it is subject to the same limitations as the `vector_search()` function. See [Limitations](/aws/en/sql/language-manual/functions/vector_search#limitations).

For more information about `UCFunctionToolkit` see [Unity Catalog documentation](https://docs.unitycatalog.io/ai/quickstart/).

## Add tracing to a retriever tool[​](#-add-tracing-to-a-retriever-tool "Direct link to -add-tracing-to-a-retriever-tool")

Add MLflow tracing to monitor and debug your retriever. Tracing lets you view inputs, outputs, and metadata for each step of execution.

The previous example adds the [@mlflow.trace decorator](https://mlflow.org/docs/latest/tracing/index.html#tracing-fluent-apis) to both the `__call__` and parsing methods. The decorator creates a [span](https://mlflow.org/docs/latest/tracing/tutorials/concept#concept-of-a-span) that starts when the function is invoked and ends when it returns. MLflow automatically records the function's input and output and any exceptions raised.

note

LangChain, LlamaIndex, and OpenAI library users can use MLflow auto logging in addition to manually defining traces with the decorator. See [Add traces to applications: automatic and manual tracing](/aws/en/mlflow3/genai/tracing/app-instrumentation/).

Python

```
import mlflow
from mlflow.entities import Document

# This code snippet has been truncated for brevity. See the full retriever example above.
class VectorSearchRetriever:
  ...

  # Create a RETRIEVER span. The span name must match the retriever schema name.
  @mlflow.trace(span_type="RETRIEVER", name="vector_search")
  def __call__(...) -> List[Document]:
    ...

  # Create a PARSER span.
  @mlflow.trace(span_type="PARSER")
  def parse_results(...) -> List[Document]:
    ...
```

To verify downstream applications such as Agent Evaluation and the AI Playground render the retriever trace correctly, make sure the decorator meets the following requirements:

* Use the [MLflow retriever span schema](https://mlflow.org/docs/latest/tracing/tracing-schema.html#retriever-spans) and verify the function returns a List[[Document](https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Document)] object.
* The trace name and the `retriever_schema` name must match to configure the trace correctly. See the following section to learn how to set the retriever schema.

### Set retriever schema to verify MLflow compatibility[​](#set-retriever-schema-to-verify-mlflow-compatibility "Direct link to set-retriever-schema-to-verify-mlflow-compatibility")

If the trace returned from the retriever or `span_type="RETRIEVER"` does not conform to [MLflow's standard retriever schema](https://mlflow.org/docs/latest/tracing/tracing-schema.html#retriever-spans), you must manually map the returned schema to MLflow's expected fields. This verifies that MLflow can properly trace your retriever and render traces in downstream applications.

To set the retriever schema manually:

1. Call [mlflow.models.set\_retriever\_schema](https://mlflow.org/docs/latest/python_api/mlflow.models.html#mlflow.models.set_retriever_schema) when you define your agent. Use `set_retriever_schema` to map the column names in the returned table to MLflow's expected fields such as `primary_key`, `text_column`, and `doc_uri`.

   Python

   ```
   # Define the retriever's schema by providing your column names
   mlflow.models.set_retriever_schema(
     name="vector_search",
     primary_key="chunk_id",
     text_column="text_column",
     doc_uri="doc_uri"
     # other_columns=["column1", "column2"],
   )
   ```
2. Specify additional columns in your retriever's schema by providing a list of column names with the `other_columns` field.
3. If you have multiple retrievers, you can define multiple schemas by using unique names for each retriever schema.

The retriever schema set during agent creation affects downstream applications and workflows, such as the review app and evaluation sets. Specifically, the `doc_uri` column serves as the primary identifier for documents returned by the retriever.

* The **review app** displays the `doc_uri` to help reviewers assess responses and trace document origins. See [Review App UI](/aws/en/agents/agent-evaluation/review-app).
* **Evaluation sets** use `doc_uri` to compare retriever results against predefined evaluation datasets to determine the retriever's recall and precision. See [Evaluation sets (MLflow 2)](/aws/en/agents/agent-evaluation/evaluation-set).

## Read files from a Unity Catalog volume[​](#read-files-from-a-unity-catalog-volume "Direct link to read-files-from-a-unity-catalog-volume")

If your agent needs to read unstructured files (text documents, reports, configuration files, etc.) stored in a Unity Catalog volume, you can create tools that use the Databricks SDK [Files API](https://docs.databricks.com/api/workspace/files) to list and read files directly.

The following examples create two tools your agent can use:

* **`list_volume_files`**: Lists files and directories in the volume.
* **`read_volume_file`**: Reads the contents of a text file from the volume.

* LangChain/LangGraph* OpenAI

Install the latest version of `databricks-langchain` that includes Databricks AI Bridge.

Bash

```
%pip install --upgrade databricks-langchain
```

Python

```
from databricks.sdk import WorkspaceClient
from langchain_core.tools import tool

VOLUME = "<catalog>.<schema>.<volume>"  # TODO: Replace with your volume
w = WorkspaceClient()

@tool
def list_volume_files(directory: str = "") -> str:
    """Lists files and directories in the Unity Catalog volume.
    Provide a relative directory path, or leave empty to list the volume root."""
    base = f"/Volumes/{VOLUME.replace('.', '/')}"
    path = f"{base}/{directory.lstrip('/')}" if directory else base
    entries = []
    for f in w.files.list_directory_contents(path):
        kind = "dir" if f.is_directory else "file"
        size = f" ({f.file_size} bytes)" if not f.is_directory else ""
        entries.append(f"  [{kind}] {f.name}{size}")
    return "\n".join(entries) if entries else "No files found."

@tool
def read_volume_file(file_path: str) -> str:
    """Reads a text file from the Unity Catalog volume.
    Provide the path relative to the volume root, for example 'reports/q1_summary.txt'."""
    base = f"/Volumes/{VOLUME.replace('.', '/')}"
    full_path = f"{base}/{file_path.lstrip('/')}"
    resp = w.files.download(full_path)
    return resp.contents.read().decode("utf-8")
```

Bind the tools to an LLM and run a tool-calling loop:

Python

```
from databricks_langchain import ChatDatabricks
from langchain_core.messages import HumanMessage, ToolMessage

llm = ChatDatabricks(endpoint="databricks-claude-sonnet-4-5")
llm_with_tools = llm.bind_tools([list_volume_files, read_volume_file])

messages = [HumanMessage(content="What files are in the volume? Can you read about_databricks.txt and summarize it in 2 sentences?")]
tool_map = {"list_volume_files": list_volume_files, "read_volume_file": read_volume_file}

for _ in range(5):  # max iterations
    response = llm_with_tools.invoke(messages)
    messages.append(response)
    if not response.tool_calls:
        break
    for tc in response.tool_calls:
        result = tool_map[tc["name"]].invoke(tc["args"])
        messages.append(ToolMessage(content=result, tool_call_id=tc["id"]))

print(response.content)
```

Install the latest version of `databricks-openai` that includes Databricks AI Bridge.

Bash

```
%pip install --upgrade databricks-openai
```

Python

```
from databricks.sdk import WorkspaceClient
from databricks_openai import DatabricksOpenAI
import json

VOLUME = "<catalog>.<schema>.<volume>"  # TODO: Replace with your volume
w = WorkspaceClient()
client = DatabricksOpenAI()

# Define the tool specifications
tools = [
    {
        "type": "function",
        "function": {
            "name": "list_volume_files",
            "description": "Lists files and directories in the Unity Catalog volume. Provide a relative directory path, or leave empty to list the volume root.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Relative directory path within the volume. Leave empty for root.",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_volume_file",
            "description": "Reads a text file from the Unity Catalog volume. Provide the path relative to the volume root, for example 'reports/q4_summary.txt'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file relative to the volume root.",
                    }
                },
                "required": ["file_path"],
            },
        },
    },
]

def execute_tool(name: str, args: dict) -> str:
    base = f"/Volumes/{VOLUME.replace('.', '/')}"
    if name == "list_volume_files":
        directory = args.get("directory", "")
        path = f"{base}/{directory.lstrip('/')}" if directory else base
        entries = []
        for f in w.files.list_directory_contents(path):
            kind = "dir" if f.is_directory else "file"
            size = f" ({f.file_size} bytes)" if not f.is_directory else ""
            entries.append(f"[{kind}] {f.name}{size}")
        return "\n".join(entries) if entries else "No files found."
    elif name == "read_volume_file":
        full_path = f"{base}/{args['file_path'].lstrip('/')}"
        resp = w.files.download(full_path)
        return resp.contents.read().decode("utf-8")
    return f"Unknown tool: {name}"

# Call the model with tools
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "List the files in the volume, then read about_databricks.txt and summarize it."},
]

response = client.chat.completions.create(
    model="databricks-claude-sonnet-4-5", messages=messages, tools=tools
)

# Execute tool calls and send results back
while response.choices[0].finish_reason == "tool_calls":
    messages.append(response.choices[0].message)
    for tool_call in response.choices[0].message.tool_calls:
        args = json.loads(tool_call.function.arguments)
        result = execute_tool(tool_call.function.name, args)
        messages.append(
            {"role": "tool", "tool_call_id": tool_call.id, "content": result}
        )
    response = client.chat.completions.create(
        model="databricks-claude-sonnet-4-5", messages=messages, tools=tools
    )

print(response.choices[0].message.content)
```

On this page

* [Query a Databricks AI Search index using MCP](#query-a-databricks-ai-search-index-using-mcp)* [Other approaches](#other-approaches)
    + [Query a vector search index hosted outside Databricks](#query-a-vector-search-index-hosted-outside-databricks)+ [Develop a retriever locally using AI Bridge](#develop-a-retriever-locally-using-ai-bridge)+ [Query Databricks AI Search using UC functions (deprecated)](#query-databricks-ai-search-using-uc-functions-deprecated)* [Add tracing to a retriever tool](#-add-tracing-to-a-retriever-tool)
      + [Set retriever schema to verify MLflow compatibility](#set-retriever-schema-to-verify-mlflow-compatibility)* [Read files from a Unity Catalog volume](#read-files-from-a-unity-catalog-volume)
