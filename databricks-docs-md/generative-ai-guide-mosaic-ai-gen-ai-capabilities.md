---
title: DatabricksAI capabilities
source_url: https://docs.databricks.com/aws/en/generative-ai/guide/mosaic-ai-gen-ai-capabilities
---

# DatabricksAI capabilities

Source: https://docs.databricks.com/aws/en/generative-ai/guide/mosaic-ai-gen-ai-capabilities

Last updated on **Aug 3, 2026**

# Databricks AI capabilities

Databricks provides a platform for building, evaluating, deploying, and monitoring AI applications (AI apps). It brings together a suite of tools that tackle the [challenges of developing enterprise-grade AI apps](/aws/en/agents/gen-ai-challenges). Databricks [integrates with popular open source frameworks](#oss), adding enterprise-grade governance, observability, and operational tooling, collectively known as LLMOps.

This page lists major features for AI, organized by AI workflow stages.

## Query AI[​](#query-ai "Direct link to Query AI")

Databricks makes state-of-the-art AI models from top model providers readily available through [Databricks-hosted Foundation Models](/aws/en/machine-learning/foundation-model-apis/supported-models). You can also query models from [external providers](/aws/en/machine-learning/foundation-models/external-models/) and your [custom models](/aws/en/machine-learning/model-serving/custom-models). All of these models can be queried through UI, API/SDK, and SQL interfaces. This optionality lets you use AI for all use cases---general chat, complex agents, automated data pipelines, interactive data analytics, and more.

|  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Method Features|  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | | UI * For development, [AI Playground](/aws/en/large-language-models/ai-playground) provides a UI for querying available AI models and agents. * For testing, your agents and apps can be queried and evaluated by domain experts using the [Review App](/aws/en/mlflow3/genai/human-feedback/). * For production, your apps can be hosted with a UI using [Databricks Apps](/aws/en/dev-tools/databricks-apps/) for use inside your organization. For external apps, you can power user-facing apps using [Databricks APIs](/aws/en/reference/api).  |  |  |  |  | | --- | --- | --- | --- | | API and SDK * [Model Serving](/aws/en/machine-learning/model-serving/) provides REST API endpoints for querying models and agents. * See [more query options](/aws/en/machine-learning/model-serving/score-foundation-models#client-options) including the OpenAI client and the Databricks Python SDK.  |  |  | | --- | --- | | SQL * [AI functions](/aws/en/large-language-models/ai-functions) provide task-specific and general-purpose SQL functions for querying models and agents. | | | | | | | |

|  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Method Features|  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | | UI * For development, [AI Playground](/aws/en/large-language-models/ai-playground) provides a UI for querying available AI models and agents. * For testing, your agents and apps can be queried and evaluated by domain experts using the [Review App](/aws/en/mlflow3/genai/human-feedback/). * For production, your apps can be hosted with a UI using [Databricks Apps](/aws/en/dev-tools/databricks-apps/) for use inside your organization. For external apps, you can power user-facing apps using [Databricks APIs](/aws/en/reference/api).  |  |  |  |  | | --- | --- | --- | --- | | API and SDK * [Model Serving](/aws/en/machine-learning/model-serving/) provides REST API endpoints for querying models and agents. * See [more query options](/aws/en/machine-learning/model-serving/score-foundation-models#client-options) including the OpenAI client and the Databricks Python SDK.  |  |  | | --- | --- | | SQL * [AI functions](/aws/en/large-language-models/ai-functions) provide task-specific and general-purpose SQL functions for querying models and agents. | | | | | | | |

## Build AI[​](#build-ai "Direct link to Build AI")

Databricks provides a flexible set of tools for building AI apps, agents, tools, and models. These include UI and code-based frameworks, all of which can optimize AI systems based on your data. You can leverage any open-source AI framework and can integrate custom tools and MCP servers.

|  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Category Features|  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | | Apps * [Databricks Apps](/aws/en/dev-tools/databricks-apps/) provide flexible app development and deployment to authenticated users. * Custom apps can be powered by [Databricks APIs](/aws/en/reference/api).  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | | Agents * [Knowledge Assistant](/aws/en/agents/agent-bricks/knowledge-assistant) provides guided agent development and optimization. * [AI Playground](/aws/en/large-language-models/ai-playground) provides a UI for prototyping tool-calling agents. * [Custom code and open-source frameworks](/aws/en/agents/custom-agents/author-agent) can be developed and deployed using [Custom Agents](/aws/en/agents/custom-agents/author-agent) or [Databricks Apps](/aws/en/dev-tools/databricks-apps/).  |  |  |  |  | | --- | --- | --- | --- | | Tools * [Tool support](/aws/en/agents/mcp-tools/) includes [MCP servers](/aws/en/agents/mcp-tools/) and [Unity Catalog Functions](/aws/en/agents/custom-agents/create-custom-tool), both of which provide Unity Catalog-based governance.  |  |  | | --- | --- | | Models and prompts * Prompt engineering can be done interactively using [AI Playground](/aws/en/large-language-models/ai-playground), or through data-driven optimization using [MLflow Prompt Optimization](/aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/automatically-optimize-prompts). * Fine-tune models using [AI Runtime](/aws/en/machine-learning/ai-runtime/). | | | | | | | | | |

|  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Category Features|  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | | Apps * [Databricks Apps](/aws/en/dev-tools/databricks-apps/) provide flexible app development and deployment to authenticated users. * Custom apps can be powered by [Databricks APIs](/aws/en/reference/api).  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | | Agents * [Knowledge Assistant](/aws/en/agents/agent-bricks/knowledge-assistant) provides guided agent development and optimization. * [AI Playground](/aws/en/large-language-models/ai-playground) provides a UI for prototyping tool-calling agents. * [Custom code and open-source frameworks](/aws/en/agents/custom-agents/author-agent) can be developed and deployed using [Custom Agents](/aws/en/agents/custom-agents/author-agent) or [Databricks Apps](/aws/en/dev-tools/databricks-apps/).  |  |  |  |  | | --- | --- | --- | --- | | Tools * [Tool support](/aws/en/agents/mcp-tools/) includes [MCP servers](/aws/en/agents/mcp-tools/) and [Unity Catalog Functions](/aws/en/agents/custom-agents/create-custom-tool), both of which provide Unity Catalog-based governance.  |  |  | | --- | --- | | Models and prompts * Prompt engineering can be done interactively using [AI Playground](/aws/en/large-language-models/ai-playground), or through data-driven optimization using [MLflow Prompt Optimization](/aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/automatically-optimize-prompts). * Fine-tune models using [AI Runtime](/aws/en/machine-learning/ai-runtime/). | | | | | | | | | |

## Prepare and serve data[​](#prepare-and-serve-data "Direct link to Prepare and serve data")

Databricks simplifies data for AI by unifying governance of traditional data and AI workloads. With all data managed under [Unity Catalog](/aws/en/data-governance/unity-catalog/) with fine-grained access controls, it is easy to adjust data engineering and AI boundaries to fit your organization. Data can be prepared for AI using any [data engineering tools](/aws/en/data-engineering/) such as [Lakeflow pipelines](/aws/en/ldp/). A table in Unity Catalog can be served for AI, using a vector index for unstructured data or a feature table for structured data.

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| Type of data Features|  |  |  |  | | --- | --- | --- | --- | | Unstructured (text, images, etc.) * [AI Search](/aws/en/ai-search/ai-search) automatically indexes your knowledge base at scale for semantic or hybrid search.  |  |  | | --- | --- | | Structured (tables) * [Serverless SQL](/aws/en/agents/custom-agents/structured-retrieval-tools#sql-function-tool) lets you integrate tables and SQL queries into your AI app for analytics or transformations. * [Genie agents](/aws/en/agents/custom-agents/model-serving/multi-agent-genie) can be used in multi-agent systems to answer natural language queries about your structured data. * [Online feature stores](/aws/en/machine-learning/feature-store/online-feature-store) provide real-time feature access for your AI app. | | | | | |

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| Type of data Features|  |  |  |  | | --- | --- | --- | --- | | Unstructured (text, images, etc.) * [AI Search](/aws/en/ai-search/ai-search) automatically indexes your knowledge base at scale for semantic or hybrid search.  |  |  | | --- | --- | | Structured (tables) * [Serverless SQL](/aws/en/agents/custom-agents/structured-retrieval-tools#sql-function-tool) lets you integrate tables and SQL queries into your AI app for analytics or transformations. * [Genie agents](/aws/en/agents/custom-agents/model-serving/multi-agent-genie) can be used in multi-agent systems to answer natural language queries about your structured data. * [Online feature stores](/aws/en/machine-learning/feature-store/online-feature-store) provide real-time feature access for your AI app. | | | | | |

## Deploy and serve AI[​](#deploy-and-serve-ai "Direct link to Deploy and serve AI")

Databricks provides production-ready serving systems for AI apps, agents, and models backed by [Databricks Apps](/aws/en/dev-tools/databricks-apps/). These scalable deployments can be used for both real-time serving and [batch inference](/aws/en/machine-learning/model-inference/). All deployments integrate with [observability](/aws/en/mlflow3/genai/tracing/) and [evaluation and monitoring](/aws/en/mlflow3/genai/eval-monitor/) tooling.

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| Development framework Deployment and serving|  |  |  |  | | --- | --- | --- | --- | | [Databricks Apps](/aws/en/agents/custom-agents/author-agent) Apps and agents can be deployed using Databricks Apps, which provides [UI- and API-based deployment](/aws/en/agents/custom-agents/author-agent).|  |  | | --- | --- | | [Knowledge Assistant](/aws/en/agents/agent-bricks/knowledge-assistant) Knowledge Assistant automates deployment of your agent to [Model Serving](/aws/en/machine-learning/model-serving/) endpoints. | | | | | |

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| Development framework Deployment and serving|  |  |  |  | | --- | --- | --- | --- | | [Databricks Apps](/aws/en/agents/custom-agents/author-agent) Apps and agents can be deployed using Databricks Apps, which provides [UI- and API-based deployment](/aws/en/agents/custom-agents/author-agent).|  |  | | --- | --- | | [Knowledge Assistant](/aws/en/agents/agent-bricks/knowledge-assistant) Knowledge Assistant automates deployment of your agent to [Model Serving](/aws/en/machine-learning/model-serving/) endpoints. | | | | | |

## Trace, evaluate, and monitor AI[​](#trace-evaluate-and-monitor-ai "Direct link to Trace, evaluate, and monitor AI")

Databricks provides [managed MLflow for AI observability, evaluation, and monitoring](/aws/en/mlflow3/genai/). Open-source APIs make integration and portability simple, while the managed service provides production-ready endpoints. Databricks-managed MLflow can be used for AI apps and agents hosted on Databricks and hosted elsewhere.

|  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Category Features|  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | | Tracing and observability * [MLflow Tracing](/aws/en/mlflow3/genai/tracing/) allows you to instrument your AI agents and apps to collect telemetry and observability data for evaluation, production monitoring, and auditing.  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | | Evaluation * [MLflow Evaluation](/aws/en/mlflow3/genai/eval-monitor/) lets you measure the quality of AI systems. * [Built-in and custom LLM judges and scorers](/aws/en/mlflow3/genai/eval-monitor/concepts/scorers) and [evaluation datasets](/aws/en/mlflow3/genai/eval-monitor/build-eval-dataset) let you tailor evaluation to your use case.  |  |  |  |  | | --- | --- | --- | --- | | Monitoring * [Production monitoring](/aws/en/mlflow3/genai/eval-monitor/production-monitoring) lets you measure quality on production traces, using the same judges and scorers from development-time evaluation.  |  |  | | --- | --- | | Human feedback * During development, the Review App lets you run quick [vibe checks using a Chat UI](/aws/en/mlflow3/genai/human-feedback/expert-feedback/live-app-testing) and collect expert feedback in [labeling sessions](/aws/en/mlflow3/genai/human-feedback/expert-feedback/label-existing-traces). * During production, APIs let you [annotate traces with user feedback](/aws/en/mlflow3/genai/tracing/collect-user-feedback/). | | | | | | | | | |

|  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Category Features|  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | | Tracing and observability * [MLflow Tracing](/aws/en/mlflow3/genai/tracing/) allows you to instrument your AI agents and apps to collect telemetry and observability data for evaluation, production monitoring, and auditing.  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | | Evaluation * [MLflow Evaluation](/aws/en/mlflow3/genai/eval-monitor/) lets you measure the quality of AI systems. * [Built-in and custom LLM judges and scorers](/aws/en/mlflow3/genai/eval-monitor/concepts/scorers) and [evaluation datasets](/aws/en/mlflow3/genai/eval-monitor/build-eval-dataset) let you tailor evaluation to your use case.  |  |  |  |  | | --- | --- | --- | --- | | Monitoring * [Production monitoring](/aws/en/mlflow3/genai/eval-monitor/production-monitoring) lets you measure quality on production traces, using the same judges and scorers from development-time evaluation.  |  |  | | --- | --- | | Human feedback * During development, the Review App lets you run quick [vibe checks using a Chat UI](/aws/en/mlflow3/genai/human-feedback/expert-feedback/live-app-testing) and collect expert feedback in [labeling sessions](/aws/en/mlflow3/genai/human-feedback/expert-feedback/label-existing-traces). * During production, APIs let you [annotate traces with user feedback](/aws/en/mlflow3/genai/tracing/collect-user-feedback/). | | | | | | | | | |

## LLMOps[​](#llmops "Direct link to LLMOps")

Databricks provides a full suite of tools for AI operations, or "LLMOps." Unified governance of data and AI assets under [Unity Catalog](/aws/en/data-governance/unity-catalog/) simplifies and secures deployment of AI across an organization. AI Gateway simplifies managing models from many AI model providers. MLflow and Declarative Automation Bundles provide versioning and infrastructure-as-code for implementing robust LLMOps processes.

|  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Category Features|  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | | Data and AI asset governance [Unity Catalog](/aws/en/data-governance/unity-catalog/) provides unified governance for data and AI assets. Data assets include files, tables, vector indexes, and feature stores. AI assets include models, tools, and connections for MCP servers and other APIs.|  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | | Model endpoint governance [AI Gateway](/aws/en/ai-gateway/) provides central governance and monitoring for AI model endpoints.|  |  |  |  | | --- | --- | --- | --- | | Prompt versioning [MLflow](/aws/en/mlflow3/genai/) provides a [Prompt Registry](/aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/), as well as experiment tracking.|  |  | | --- | --- | | Infrastructure as code [MLOps Stacks](/aws/en/machine-learning/mlops/mlops-stacks), which is built on top of [Databricks Assets Bundles](/aws/en/dev-tools/bundles/), provides code-based management and deployment of infrastructure and workflows. | | | | | | | | | |

|  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Category Features|  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | | Data and AI asset governance [Unity Catalog](/aws/en/data-governance/unity-catalog/) provides unified governance for data and AI assets. Data assets include files, tables, vector indexes, and feature stores. AI assets include models, tools, and connections for MCP servers and other APIs.|  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | | Model endpoint governance [AI Gateway](/aws/en/ai-gateway/) provides central governance and monitoring for AI model endpoints.|  |  |  |  | | --- | --- | --- | --- | | Prompt versioning [MLflow](/aws/en/mlflow3/genai/) provides a [Prompt Registry](/aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/), as well as experiment tracking.|  |  | | --- | --- | | Infrastructure as code [MLOps Stacks](/aws/en/machine-learning/mlops/mlops-stacks), which is built on top of [Databricks Assets Bundles](/aws/en/dev-tools/bundles/), provides code-based management and deployment of infrastructure and workflows. | | | | | | | | | |

## Open source support[​](#-open-source-support "Direct link to -open-source-support")

Databricks provides full support for the rapidly growing open-source ecosystem for AI.

For development, you can use any open-source framework and deploy it using [Databricks Apps](/aws/en/dev-tools/databricks-apps/). Databricks services can be used by third-party AI tools and apps by using [MCP servers](/aws/en/agents/mcp-tools/) or the [REST API or SDKs](/aws/en/reference/api).

For observability, evaluation, and monitoring, [MLflow Tracing](/aws/en/mlflow3/genai/tracing/) provides native autologging for [20+ open-source AI frameworks](/aws/en/mlflow3/genai/tracing/integrations/), and you can add custom tracing to any other frameworks or code. The traces can then be used with [MLflow Evaluation and production monitoring](/aws/en/mlflow3/genai/eval-monitor/). The traces follow [OpenTelemetry trace specs](/aws/en/mlflow3/genai/tracing/integrations/open-telemetry) and can be exported to third-party tools.

## Additional resources[​](#-additional-resources "Direct link to -additional-resources")

* [Build agents on Databricks](/aws/en/agents/)
* [Open source vs. managed MLflow on Databricks](/aws/en/mlflow3/genai/overview/oss-managed-diff)

On this page

* [Query AI](#query-ai)* [Build AI](#build-ai)* [Prepare and serve data](#prepare-and-serve-data)* [Deploy and serve AI](#deploy-and-serve-ai)* [Trace, evaluate, and monitor AI](#trace-evaluate-and-monitor-ai)* [LLMOps](#llmops)* [Open source support](#-open-source-support)* [Additional resources](#-additional-resources)
