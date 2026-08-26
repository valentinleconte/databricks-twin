# Tests for this project's own code

Unit tests covering the parts of databricks-twin that are **mine**, not the upstream
`agent-langgraph` template: the eval scoring logic, the doc-chunking/SQL-escaping helpers, and
the couplings between `databricks.yml`, `agent.py`, and the SQL that sets up the mock data.

## Why `tests_twin/`, not `tests/`?

Unlike openrag-twin — where `tests_twin/` exists because upstream's own `tests/conftest.py`
bootstraps the whole application and can't be imported without the full stack — this template
ships **no `tests/` directory at all**. There's no collision to avoid here; the separate name is
just kept for consistency with the sibling project, and because it still says the same thing:
these are the tests for what *I* added, not a claim about testing the template itself.

## Running

```bash
uv run --with pytest --with pyyaml pytest tests_twin -q
```

52 tests, well under a second, **no Docker, no Databricks workspace, no credentials, no
network** — gated on every push/PR by [`twin-checks.yml`](../.github/workflows/twin-checks.yml).

## What's covered, and one real constraint on what isn't

- **`eval/run_eval.py`'s scoring logic** ([`test_eval_scoring.py`](test_eval_scoring.py)) — every
  category's pass/fail rules, the `--runs`/stability gate, and that a backend error never scores
  as a pass. Includes a regression test for the real `.html`-suffix citation bug this project hit
  (see the main README's bug registry) and a check that the golden set's own ground truth
  (`ticket_known` cases, the aggregate "how many tickets are Open" case, source-URL substrings)
  actually matches the real corpus and `create_tickets.sql` — not just internally consistent YAML.
- **`scripts/twin/setup_resources.py`'s pure logic** ([`test_setup_resources.py`](test_setup_resources.py))
  — chunk boundaries and overlap on a worked example, plus a regression pin on the actual measured
  chunk count (196) from the real corpus, and that `sql_escape()` can't be used to break out of a
  single-quoted SQL literal.
- **Cross-file invariants** ([`test_repo_invariants.py`](test_repo_invariants.py)) — three couplings
  that are real but invisible: `agent.py`'s `DOC_SEARCH_INDEX` must name the same index
  `databricks.yml` grants `SELECT` on; the `GENIE_SPACE_ID` env var and the granted `genie_space`
  resource must name the same space; and `create_tickets.sql`'s table name must match what
  `databricks.yml` grants `SELECT` on. Each of these could drift silently — a typo in one place
  wouldn't fail `bundle deploy`, it would just make a tool call fail at runtime.

**What's deliberately not unit-tested here: `agent_server/agent.py` itself.** It builds a real
`WorkspaceClient()` at module import time (`sp_workspace_client = WorkspaceClient()`), so importing
it — even just to test the `init_mcp_client()` server-list logic — needs live Databricks
credentials, which breaks the "no live workspace" constraint this suite exists to keep. The
`test_repo_invariants.py` checks that touch `agent.py` read it as text (regex on the source) rather
than importing it — a real, named tradeoff, not an oversight. Testing `agent.py`'s logic properly
would need factoring the MCP-server-list construction out from the module-level `WorkspaceClient()`
call first; not done here because the CI value of catching a drifted index/space name doesn't
require it.
