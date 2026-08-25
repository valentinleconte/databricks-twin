---
title: MCPs and agent tools
source_url: https://docs.databricks.com/aws/en/generative-ai/agent-framework/agent-tool
---

# MCPs and agent tools

Source: https://docs.databricks.com/aws/en/generative-ai/agent-framework/agent-tool

Last updated on **Aug 17, 2026**

# MCPs and agent tools

Databricks governs and manages the tools and MCP servers your agents use through [Unity AI Gateway](/aws/en/ai-gateway/), which controls access and monitors activity from a single control plane, while Unity Catalog enforces permissions and manages credentials so agents and users reach only the tools and data you grant them.

Tools give your agents practical capabilities beyond text generation, like searching documents, querying tables, calling external APIs, or running custom code.

[MCP](https://modelcontextprotocol.io/introduction) is an open-source standard that connects AI agents to tools, resources, and prompts, and is one of several ways to connect tools on Databricks.

To see your available MCP servers, go to your workspace > **AI Gateway** > **MCPs**:

![The MCPs tab in ai-gateway listing available MCP servers in the workspace.](/aws/en/assets/images/ai-gateway-mcp-tab-2e3a2b8d9db81e94f8caf85a1e7ba15e.png)

* + [MCPs for Databricks services](/aws/en/agents/mcp-tools/managed-mcp)
  + Ready-to-use managed MCP servers that give agents governed access to Genie, AI Search, Databricks SQL, and Unity Catalog functions with no server to build or host.
* + [Connect agents to external MCPs and tools](/aws/en/agents/mcp-tools/connect-external)
  + Connect agents to external services like Slack, Google Drive, or any API using external MCP servers, managed OAuth, the Unity Catalog connections proxy, or Unity Catalog function tools.
* + [Host your own MCP](/aws/en/agents/mcp-tools/custom-mcp)
  + Host a custom MCP server as a Databricks app to expose your own tools.
* + [Connect third-party agents to Databricks MCP servers](/aws/en/agents/mcp-tools/connect-clients)
  + Wire up Claude, Cursor, MCP Inspector, and other clients to your Databricks MCPs.
* + [Agent skills for AI coding assistants](/aws/en/agent-skills/)
  + Install skills and plugins that teach coding agents like Claude Code and Cursor how to write Databricks code correctly, alongside the MCP tools they call.
* + [Unity Catalog function tools](/aws/en/agents/custom-agents/create-custom-tool)
  + Create AI agent tools using Unity Catalog functions, including third-party integrations and code interpreter tools.
* + [Work with structured and unstructured data](/aws/en/agents/custom-agents/structured-retrieval-tools)
  + Retrieve structured data with Unity Catalog function tools and query unstructured data with vector search retrieval tools.
