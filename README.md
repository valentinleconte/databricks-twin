<div align="center">

# databricks-twin

<h3><em>A functional exploration of Databricks' agentic AI stack, built to prove I understand the platform — not just describe it</em></h3>

</div>

---

<!-- TODO once the pitch video exists — mirror openrag-twin's embed pattern
(GitHub Pages player, since raw.githubusercontent.com serves video as
application/octet-stream and downloads instead of playing). -->

## Why this exists

<!-- TODO: adapt from openrag-twin's framing. Key facts already true, ready to write:
- Built for a Databricks-related interview.
- Unlike OpenRAG (a self-hostable open-source product), Databricks is a SaaS platform —
  no "clone and docker-compose up" equivalent. Say so honestly; don't force the OpenRAG
  narrative where it doesn't fit.
- Started from a real, actively-maintained official template
  (databricks/app-templates/agent-langgraph), not a from-scratch reimplementation —
  same "extend a real product" spirit as OpenRAG.
- License is Databricks' own (not Apache 2.0) — terms actually read, not assumed;
  summarize honestly (see NOTES.md for the full text worked through).
-->

## What I'm demonstrating

<!-- TODO: the differentiator vs openrag-twin isn't "agentic vs classic RAG" again —
that's already proven there. Here it's:
1. The SAME routing-agent pattern (decide, don't just retrieve), reimplemented on a second
   vendor's real primitives — proof the understanding transfers, not vendor-specific luck.
2. A deliberate exploration of a Databricks-native capability with no OpenRAG analog:
   Genie (natural-language-to-SQL over a governed Unity Catalog table) as a *hosted* tool
   via the Supervisor API, contrasted with a hand-written custom tool (OpenRAG's ticket
   mock) — write up that contrast once both are actually built and can be compared fairly.
-->

## Architecture

<!-- TODO: Mermaid diagram once the real components are wired and verified — do not draw
from assumption. Known pieces so far, to confirm against what's actually deployed:
- Vector Search (doc corpus — Databricks' own docs, self-referential like OpenSearch docs
  were for openrag-twin)
- Unity Catalog (structured ticket-like table)
- Genie Space over that table, wired as a hosted tool via Supervisor API
- Model Serving (LLM — no Claude in the default pay-per-token roster, verified; final
  model choice + reasoning still open, document it with the same rigor as the
  Opus->Sonnet writeup in openrag-twin once decided)
- agent-langgraph's ResponsesAgent / MLflow serving loop
-->

## Measured, not just claimed

<!-- TODO once there's an eval harness. agent-langgraph ships MLflow-native evaluation
(agent_server/evaluate_agent.py) with ready-made scorers (ToolCallCorrectness,
RelevanceToQuery, Safety, ...) and a persona ConversationSimulator — decide whether to use
that directly (stronger "I know MLflow" signal) or port openrag-twin's golden-set approach
on top of it. Whichever: report a real, re-run number here, not an aspirational one. -->

## What's mine vs. upstream

<!-- TODO: table like openrag-twin's, once real files exist to list. -->

## License

<!-- TODO: this is NOT Apache 2.0 like OpenRAG — Databricks' own proprietary license,
conditioned on active use of Databricks Services, with specific redistribution
requirements (LICENSE + NOTICE retained, modified files marked). Say this plainly and
accurately; see NOTES.md for the full terms as actually read. Do not copy openrag-twin's
license section verbatim — the legal situation is genuinely different. -->
