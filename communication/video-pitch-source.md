# databricks-twin — Video Pitch Source

> This document is written to be read aloud, not skimmed. It is the primary source for a
> NotebookLM Video Overview pitching this project. Upload this file (and optionally README.md for
> extra detail) as a NotebookLM source, then use the customization prompt in
> `notebooklm-prompt.md` when generating the video.

## What this project is

databricks-twin is a working, hands-on agent built on the real Databricks platform — Unity
Catalog, Vector Search, Genie, Model Serving, MLflow, and Databricks Apps, all actually used, not
described secondhand. It's a companion to an earlier project, openrag-twin, a replica of IBM's own
OpenRAG product built for a different interview. That one proved depth on one stack. This one
proves the same rigor holds on a second, completely different vendor's tools — not a one-stack
fluke, not luck with a particular framework.

The project starts from `agent-langgraph`, an official, actively-maintained Databricks starter
template — a LangGraph agent wired to MLflow's Responses API. On top of that foundation sit the
original pieces: a real document corpus, two Databricks-native tools, a deployed production app,
and a measured, honestly-reported evaluation.

## The architecture, in plain terms

A chat UI talks to a FastAPI backend running an MLflow agent. That agent runs on Llama 3.3 70B
Instruct, served through Databricks Model Serving — the only model actually available on this
workspace's free tier; no Claude endpoint is enabled here, a real platform constraint worth naming
plainly rather than glossing over. The agent has two tools, both Databricks-hosted, not custom
infrastructure: a Vector Search index over a Unity Catalog table holding chunked Databricks
documentation, and a Genie space — Databricks' natural-language-to-SQL service — pointed at a
second Unity Catalog table of mock support tickets. MLflow traces every call and backs the
evaluation.

## The scenario: an agent that decides, not just retrieves

The core problem is the same one openrag-twin solved on a different stack: an agent that has to
*choose* the right tool for each question, not just search a knowledge base and hope. Ask it a
documentation question — how does Vector Search keep an index synced with its source table — and
it searches the indexed docs and cites the exact source URL it used. Ask it about a support
ticket, and it skips the documents entirely and asks Genie in plain English, which generates and
runs the actual SQL against a governed table and returns the real answer.

What's different from the first project isn't the pattern, it's the mechanism. Instead of porting
over a hand-written mock tool, the second tool here is genuinely Databricks-native: Genie doing
real natural-language-to-SQL against real governed data, not a Python dictionary standing in for
one.

## Evidence of understanding, not just usage: the permission bug

Running someone else's platform well enough to hit a real bug, and understanding exactly why it
happened, is the whole point of a project like this. Here's the one worth explaining in detail.

The agent's Genie tool worked perfectly in local testing — every question, every time. Then the
app was actually deployed to Databricks Apps, as a real production application with its own
service principal identity, and the exact same ticket questions started failing with a permissions
error. The cause: granting an app's service principal `CAN_RUN` on a Genie space only grants
permission to *ask* the space a question. Genie then executes the SQL it generates using the
*caller's own* Unity Catalog rights on the underlying table — a completely separate grant chain
that local testing never exercised, because local testing ran under an already-privileged personal
account, not the app's actual identity. The fix was three explicit grants — catalog usage, schema
usage, table select — to the service principal itself, applied and verified after the fact. It's a
small bug with a genuinely instructive shape: a permission that looks sufficient in one context and
silently isn't in the one that actually matters.

## Measured, not just claimed

Every claim here is backed by a number, not a feeling. A fifteen-case golden set, run three times
because a stochastic agent's single pass is a sample, not a property, scores this project at
thirteen out of fifteen, eleven out of fifteen, and thirteen out of fifteen — an honest eighty-two
percent, not a cleaned-up hundred. That gap traces to two real, diagnosed limitations, written up
in full rather than hidden: the model occasionally emits malformed tool-call syntax instead of
actually calling a tool, and it occasionally answers a question the documentation doesn't cover
from its own general knowledge instead of admitting the gap. Both are named, measured, and left as
honest limitations rather than smoothed over.

## The takeaway

This project demonstrates the same comprehension openrag-twin did — the retrieval architecture,
the agent's decision logic, the operational reality of running it in production — but proves it
transfers to a second vendor's stack, with its own governance model, its own failure modes, and its
own constraints. It's built to be defended in detail in a conversation, not to look impressive from
a distance.
