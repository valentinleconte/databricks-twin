# Golden set

A structured evaluation set for the routing agent, replacing "I asked it a few questions and it
seemed fine" with a measured pass rate. Same shape and scoring philosophy as
[openrag-twin's golden set](https://github.com/valentinleconte/openrag-twin/tree/main/eval) — the
point of building both was to reuse the same measurement discipline on a second stack, not just
the same agent pattern.

## What it checks

[`golden_set.yaml`](golden_set.yaml) has 15 cases across 6 categories:

| Category | Count | What passing means |
|---|---|---|
| `knowledge` | 8 | Cites a `source_url` that actually supports the claim, copied verbatim, and the answer contains the expected fact |
| `ticket_known` | 3 | Returns the correct ticket data from the Genie space, with **no** documentation citation |
| `ticket_unknown` | 1 | Honestly reports the ticket doesn't exist, instead of inventing one |
| `mixed` | 1 | A single question needing both tools gets both — ticket data *and* a cited answer |
| `off_topic` | 1 | A non-question ("Hi, how are you?") doesn't force either tool |
| `out_of_corpus` | 1 | A real Databricks question the corpus doesn't cover gets an honest "no relevant sources," not a hallucination |

Ground truth (expected source pages, expected ticket data, expected keywords) is hand-verified
against [`databricks-docs-md/`](../databricks-docs-md/) and
[`scripts/twin/create_tickets.sql`](../scripts/twin/create_tickets.sql) — nothing here is guessed.

## Running it

```bash
# The real number: replay the whole set 3x and report per-case stability
uv run --with pyyaml python3 eval/run_eval.py --runs 3 --allow-flaky --save eval/last_results.json

# a single pass, when you just want a quick signal
uv run --with pyyaml python3 eval/run_eval.py

# or a quick subset, e.g. for a time-boxed demo:
uv run --with pyyaml python3 eval/run_eval.py --ids know-04,ticket-04,edge-02
uv run --with pyyaml python3 eval/run_eval.py --category knowledge
```

Requires the local server up (`uv run start-app`) — it calls the real `POST /invocations`
endpoint for each case, the same MLflow Responses API path the deployed app uses, and scores the
actual response text.

### Why `--runs`, and why a flaky case fails the gate

The agent is stochastic — and on this project that's not a theoretical caveat, it's the whole
reason a real bug got found (see [README § Bugs found & fixed](../README.md#bugs-found--fixed)).
Averaging several runs would hide exactly the thing worth seeing: a case that passes 2 times out
of 3 is a *reliability weakness*, and a mean percentage alone reads like noise rather than the
warning it is.

`--runs N` reports per-case stability (k/N) and names the flaky cases, and **exits non-zero unless
every case passes every run**. `--allow-flaky` downgrades flakiness to a warning (a case that
never passes still fails the gate). The strict default is deliberate: this harness exists to stop
an unverified claim from becoming a headline number.

One pass of 15 cases costs $0 in model spend — Free Edition, pay-per-token Foundation Model API,
no card on file — and takes roughly 6 minutes (ticket/Genie questions run noticeably slower than
doc-search ones, ~30s vs ~20s per case, because Genie's NL-to-SQL round trip is genuinely slower
than a plain vector search).

## Latest run

**13/15, 11/15, 13/15 across 3 runs — mean 82%, 10/15 cases stable across all three**
([`last_results.json`](last_results.json) has the full question/answer/citation record for every
case in every run). Reported as the honest number, not the best of the three.

The gap from 100% isn't scoring noise or a golden-set bug — it traces to two real, diagnosed
issues, both written up in full in the main README:

- **Tool-calling reliability of Llama 3.3 70B Instruct** — the model used, since no Claude endpoint
  is enabled on this workspace's Free Edition tier. On ~10-20% of individual tool calls it emits
  its function-call syntax as literal text instead of a structured call. The `mixed` case (needs
  two tool calls in one turn) failed **5 out of 5** times across every run performed — the single
  worst-affected case in the set.
- **Occasional hallucination on the out-of-corpus case** — asked something real but genuinely
  absent from the 11-page corpus, the agent admitted the gap honestly in 4 of 6 observed runs, and
  fabricated a plausible-sounding answer in the other 2.

One pass is a snapshot, not a guarantee — re-run it rather than trusting a stale number, especially
after any prompt or model change.

## Known limitation: this scores text, not the raw trajectory

Routing is inferred from the *final answer* — a ticket answer with no `docs.databricks.com`
citation is treated as evidence the doc-search tool wasn't used. That's a proxy, not a proof: an
agent that searched the docs, found nothing useful, and answered from Genie anyway would still
pass. Worth naming precisely, because it's *not* a hard platform limitation here the way it was on
openrag-twin: the raw `/invocations` response actually **does** include every `function_call` and
`function_call_output` item — `run_eval.py`'s `ask()` just discards everything except the final
`message` text, to keep the scoring logic short and readable for 15 cases. Scoring the real
trajectory instead of the final text would be a small, well-scoped change if this set grew enough
to need it.

## Why this scoring approach, not a framework like RAGAS

The checks are plain regex/substring matching on the final answer text — short enough to read end
to end, which matters more here than generality. For a 15-case set demonstrating a specific
routing behavior, a framework built for large, statistically-evaluated RAG pipelines would be more
machinery than the thing being tested.

## MLflow-native evaluation — the complementary, lighter-weight path

[`agent_server/evaluate_agent.py`](../agent_server/evaluate_agent.py) runs this same golden set
through `mlflow.genai.evaluate()` with two built-in scorers, `RelevanceToQuery` and
`ToolCallCorrectness` — deliberately not the template's default full 9-scorer +
`ConversationSimulator` setup (see the file's own docstring for why). Run it with:

```bash
uv run agent-evaluate
```

Latest scores on the rows that scored successfully: `relevance_to_query` 0.70,
`tool_call_correctness` 0.27 — a real gap against this golden set's 82%, left as an open question
rather than reconciled (two different measurement methodologies aren't expected to agree exactly,
but a gap that size is worth flagging). Running it locally also surfaced a third, separate bug —
the local CLI's OAuth token cache choking under concurrent scorer calls — written up in the main
README alongside the other three.
