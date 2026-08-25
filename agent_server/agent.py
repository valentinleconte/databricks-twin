import logging
import os
from typing import AsyncGenerator, Optional

import mlflow
from databricks.sdk import WorkspaceClient
from databricks_langchain import ChatDatabricks, DatabricksMCPServer, DatabricksMultiServerMCPClient
from langchain.agents import create_agent
from mlflow.genai.agent_server import invoke, stream
from mlflow.types.responses import (
    ResponsesAgentRequest,
    ResponsesAgentResponse,
    ResponsesAgentStreamEvent,
    to_chat_completions_input,
)

from agent_server.utils import (
    get_databricks_host_from_env,
    get_session_id,
    get_user_workspace_client,
    process_agent_astream_events,
)

logger = logging.getLogger(__name__)
mlflow.langchain.autolog()
logging.getLogger("mlflow.utils.autologging_utils").setLevel(logging.ERROR)
sp_workspace_client = WorkspaceClient()

# Same two-tool routing scenario as openrag-twin (doc RAG vs. a second, clearly-non-document data
# source), reimplemented with genuinely Databricks-native mechanisms instead of a ported mock:
# a Vector Search index for docs, and a Genie space (NL-to-SQL) for the ticket data. Both run as
# Databricks-hosted MCP servers, so the agent code itself stays this short.
DOC_SEARCH_INDEX = "workspace.databricks_twin.doc_chunks_index"
# Set once the Genie space is created in the UI (CLI cannot create one) and its space_id is known.
GENIE_SPACE_ID = os.environ.get("GENIE_SPACE_ID")

AGENT_INSTRUCTIONS = """You are the support assistant for a Databricks-native RAG platform.

You have up to two tools, and must pick the right one for each question:

1. **Documentation search** (vector search over `workspace.databricks_twin.doc_chunks`) — use for
   questions about how the underlying platform works: Unity Catalog, Vector Search, Genie, MCP,
   Delta tables, the Mosaic AI Agent Framework, etc. Always cite the `source_url` of the passage(s)
   you used when you answer from this tool.

2. **Support ticket lookup** (Genie space over `workspace.databricks_twin.support_tickets`) — use
   for any question about a specific support ticket (status, priority, assignee) or a request to
   list/count/filter tickets (e.g. "how many tickets are Open", "who owns ticket 104").

Pick exactly one tool per turn based on what the question is actually asking. If a question mixes
both, call both tools and combine the results, still citing the doc source_url for the
documentation part. If the ticket lookup finds no matching ticket, say so plainly instead of
guessing. Never invent a source_url or a ticket field that wasn't actually returned by a tool."""


def init_mcp_client(workspace_client: WorkspaceClient) -> DatabricksMultiServerMCPClient:
    host_name = get_databricks_host_from_env()
    servers = [
        DatabricksMCPServer(
            name="doc-search",
            url=f"{host_name}/api/2.0/mcp/vector-search/{DOC_SEARCH_INDEX.replace('.', '/')}",
            workspace_client=workspace_client,
            handle_tool_error=True,
        ),
    ]
    if GENIE_SPACE_ID:
        servers.append(
            DatabricksMCPServer(
                name="support-tickets-genie",
                url=f"{host_name}/api/2.0/mcp/genie/{GENIE_SPACE_ID}",
                workspace_client=workspace_client,
                handle_tool_error=True,
                timeout=60.0,  # Genie's NL-to-SQL round trip is slower than a plain tool call.
            )
        )
    else:
        logger.warning(
            "GENIE_SPACE_ID not set — running with doc search only, no ticket-lookup tool."
        )
    return DatabricksMultiServerMCPClient(servers)


async def init_agent(workspace_client: Optional[WorkspaceClient] = None):
    mcp_client = init_mcp_client(workspace_client or sp_workspace_client)
    try:
        tools = await mcp_client.get_tools()
    except Exception:
        logger.warning("Failed to fetch MCP tools. Continuing without MCP tools.", exc_info=True)
        tools = []
    # databricks-gpt-5-2 (the template's default) doesn't exist on this workspace's pay-per-token
    # roster — verified via `databricks serving-endpoints list`. No Anthropic Claude available
    # either. Using Llama 3.3 70B Instruct: a capable, well-established choice for agentic
    # tool-calling among what's actually READY here.
    return create_agent(tools=tools, model=ChatDatabricks(endpoint="databricks-meta-llama-3-3-70b-instruct"))


@invoke()
async def invoke_handler(request: ResponsesAgentRequest) -> ResponsesAgentResponse:
    outputs = [
        event.item
        async for event in stream_handler(request)
        if event.type == "response.output_item.done"
    ]
    return ResponsesAgentResponse(output=outputs)


@stream()
async def stream_handler(
    request: ResponsesAgentRequest,
) -> AsyncGenerator[ResponsesAgentStreamEvent, None]:
    if session_id := get_session_id(request):
        mlflow.update_current_trace(metadata={"mlflow.trace.session": session_id})

    # By default, uses service principal credentials.
    # For on-behalf-of user authentication, use get_user_workspace_client() instead:
    #   agent = await init_agent(workspace_client=get_user_workspace_client())
    agent = await init_agent()
    user_messages = to_chat_completions_input([i.model_dump() for i in request.input])
    messages = {"messages": [{"role": "system", "content": AGENT_INSTRUCTIONS}] + user_messages}

    async for event in process_agent_astream_events(
        agent.astream(input=messages, stream_mode=["updates", "messages"])
    ):
        yield event
