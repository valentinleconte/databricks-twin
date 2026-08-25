---
title: Get started: Query LLMs and prototype agents with no code
source_url: https://docs.databricks.com/aws/en/getting-started/gen-ai-llm-agent
---

# Get started: Query LLMs and prototype agents with no code

Source: https://docs.databricks.com/aws/en/getting-started/gen-ai-llm-agent

Last updated on **Aug 3, 2026**

# Get started: Query LLMs and prototype agents with no code

This 5-minute no-code tutorial introduces AI on Databricks. You will use the [AI Playground](/aws/en/large-language-models/ai-playground) to do the following:

* Query large language models (LLMs) and compare results side-by-side
* Prototype a tool-calling agent
* Export your agent to Databricks Apps or to a notebook
* Optional: Prototype a question-answer chatbot using retrieval-augmented generation (RAG)

## Before you begin[​](#before-you-begin "Direct link to Before you begin")

Ensure your workspace can access the following:

* [Foundation models](/aws/en/resources/feature-region-support#model-serving-aws).

* [Unity Catalog](/aws/en/data-governance/unity-catalog/get-started).
* Custom Agents. See [Features with limited regional availability](/aws/en/resources/feature-region-support).

## Step 1: Query LLMs using AI Playground[​](#step-1-query-llms-using-ai-playground "Direct link to Step 1: Query LLMs using AI Playground")

Use the AI Playground to query LLMs in a chat interface.

1. In your workspace, select **Playground** from the left navigation pane under **AI/ML**.
2. Type a question such as, "What is RAG?"

Add a new LLM to compare responses side-by-side:

1. In the upper-right, select **+** to add a model for comparison.
2. In the new pane, select a different model using the dropdown selector.
3. Select the **Sync** checkboxes to synchronize the queries.
4. Try a new prompt, such as, "What is a compound AI system?" to see the two responses side-by-side.

![AI playground](https://assets.docs.databricks.com/_static/images/machine-learning/ai-playground.gif)

Keep testing and comparing different LLMs to help you decide on the best one to use to build an agent.

## Step 2: Prototype a tool-calling agent[​](#step-2-prototype-a-tool-calling-agent "Direct link to Step 2: Prototype a tool-calling agent")

Tools allow LLMs to do more than generate language. Tools can query external data, run code, and take other actions. AI Playground gives you a no-code option to prototype tool-calling agents:

1. From Playground, choose a model labelled **Tools enabled**.

   ![Select a tool-calling LLM](/aws/en/assets/images/playground-tools-enabled-32b9b1573519c001726bcef8c40b7e32.png)
2. Select **Tools** > **+ Add tool** and select the built-in Unity Catalog function, `system.ai.python_exec`.

   This function lets your agent run arbitrary Python code.

   ![Select a hosted function tool](/aws/en/assets/images/playground-uc-function-tool-360bc91b3db9df30ba22608089a7a801.png)

   Other tool options include:

   * **UC Function**: Select a Unity Catalog function for your agent to use.
   * **Function definition**: Define a custom function for your agent to call.
   * **AI Search**: Specify an [AI Search index](/aws/en/ai-search/create-ai-search#create-vector-search-index). If your agent uses an AI Search index, its response will cite the sources used.
   * **MCP**: Specify [MCP servers](/aws/en/agents/mcp-tools/) to use managed Databricks MCP servers or external MCP servers.
3. Ask a question that involves generating or running Python code. You can try different variations on your prompt phrasing. If you add multiple tools, the LLM selects the appropriate tool to generate a response.

   ![Prototype the LLM with hosted function tool](/aws/en/assets/images/playground-prototyping-hosted-function-tool-d975aba92273c241a4449964a841a216.png)

## Optional: Prototype a RAG question-answering bot[​](#optional-prototype-a-rag-question-answering-bot "Direct link to Optional: Prototype a RAG question-answering bot")

If you have an AI Search index set up in your workspace, you can prototype a question-answer bot. This type of agent uses documents in an AI Search index to answer questions based on those documents.

1. Click **Tools** > **+ Add tool**. Then, select your AI Search index.

   ![Select an AI Search tool](/aws/en/assets/images/playground-add-vector-search-tool-54316b8fd82e5ae1f64c8c5b16212a58.png)
2. Ask a question related to your documents. The agent can use the index to look up relevant info and will cite any documents used in its answer.

   ![Prototype the LLM with AI Search tool](/aws/en/assets/images/playground-prototyping-vector-search-tool-cac7c977da7b30e9a621d67bfa194e3d.png)

To set up an AI Search index, see [Create an AI Search index](/aws/en/ai-search/create-ai-search#create-vector-search-index).

## Step 3: Export your agent[​](#step-3-export-your-agent "Direct link to step-3-export-your-agent")

After testing your agent in AI Playground, export it so that you can deploy, evaluate, and iterate on it outside the Playground. AI Playground offers two export paths:

* **Export to Databricks Apps (recommended)**: Installs a deployable agent app from the `agent-openai-agents-sdk` template, including a built-in chat UI, MCP tool wiring, and authentication. Choose this path for new agents.
* **Create agent notebook (legacy)**: Generates a Python notebook that defines the agent and deploys it to a Model Serving endpoint. Choose this path if Databricks Apps is not available in your workspace or region.

* Export to Apps (recommended)* Create agent notebook (legacy)

The **Export to Databricks Apps** option generates a deployed agent app that's ready to chat with. The app uses the same model, system prompt, and tools (including MCP servers and vector search) you configured in the Playground.

Before you export, make sure your workspace meets the following requirements:

* Databricks Apps must be enabled in your workspace. See [Set up your Databricks Apps workspace and development environment](/aws/en/dev-tools/databricks-apps/configure-env).
* The endpoint selected in Step 2 must support tools.
* The **Managed MCP Servers** preview must be enabled in your workspace. See [Manage Databricks previews](/aws/en/admin/workspace-settings/manage-previews).

To export the agent:

1. In the Playground, click **Get code** > **Export to Databricks Apps**.
2. In the **Export to Databricks Apps** dialog, set the following:

   * **App Name**: A unique name that starts with `agent-` and contains only lowercase letters, numbers, and hyphens (for example, `agent-research-assistant`).
   * **App Description**: A short description of what the agent does.
   * **MLflow Experiment**: Select an existing MLflow experiment to use for tracing and evaluation, or create a new one.
3. Click **Export**. Databricks does the following:

   1. Validates that the app name is available.
   2. Installs the `agent-openai-agents-sdk` template into your workspace and grants the app permissions for the resources it needs. These resources include the MLflow experiment, serving endpoint, and any MCP servers, Unity Catalog functions, Genie Agents, or vector search indexes you added as tools.
   3. Generates `agent_server/agent.py` from your Playground configuration so the deployed agent matches what you tested.
4. When the success dialog appears, click **View Agent** to open the deployed app and chat with it using the built-in UI.

To customize the agent code, configure authentication, add evaluation, or redeploy with [Databricks Asset Bundles (DABs)](/aws/en/dev-tools/bundles/), see [Author an agent and deploy it on Databricks Apps](/aws/en/agents/custom-agents/author-agent).

After testing your agent in AI Playground, click **Get code** > **Create agent notebook** to export your agent to a Python notebook.

After you export the agent code, Databricks saves a folder with a driver notebook to your workspace. This driver defines a tool-calling [ResponsesAgent](https://mlflow.org/docs/latest/genai/serving/responses-agent/), tests the agent locally, uses [code-based logging](/aws/en/agents/custom-agents/model-serving/log-agent#code-based-logging), registers, and deploys the agent using Custom Agents.

note

The exported notebook currently uses a legacy agent authoring workflow that deploys the agent to Model Serving. Databricks recommends authoring agents using Databricks Apps instead. See [Author an agent and deploy it on Databricks Apps](/aws/en/agents/custom-agents/author-agent).

Use the Supervisor API for a managed agent loop

If you want Databricks to run the agent loop for you, you can use the [Supervisor API (Beta) (deprecated)](/aws/en/agents/agent-bricks/supervisor-api) instead of writing your own. The Supervisor API supports Databricks-hosted tools (Unity Catalog functions, Genie Agents, MCP servers) and client-side function tools that execute in your application code. Choose this option when you don't need custom Python logic between tool calls.

To try it from your Playground configuration, make sure you've added at least one tool in Step 2, then click **Get code** > **Curl API**. When the Playground deployment has tools and uses a [Supervisor-compatible model](/aws/en/agents/agent-bricks/supervisor-api#supported-parameters), the curl is a Supervisor API `POST` request to `/mlflow/v1/responses` with your model, prompt, and hosted tools. The option also requires the **Supervisor API** preview to be enabled. See [Manage Databricks previews](/aws/en/admin/workspace-settings/manage-previews).

To deploy a Supervisor API agent on Databricks Apps, see [Build a custom agent using the Supervisor API (Beta) (deprecated)](/aws/en/agents/custom-agents/supervisor-api-app).

## Next steps[​](#next-steps "Direct link to Next steps")

To author agents using a code-first approach, see [Author an agent and deploy it on Databricks Apps](/aws/en/agents/custom-agents/author-agent).

On this page

* [Before you begin](#before-you-begin)* [Step 1: Query LLMs using AI Playground](#step-1-query-llms-using-ai-playground)* [Step 2: Prototype a tool-calling agent](#step-2-prototype-a-tool-calling-agent)* [Optional: Prototype a RAG question-answering bot](#optional-prototype-a-rag-question-answering-bot)* [Step 3: Export your agent](#step-3-export-your-agent)* [Next steps](#next-steps)
