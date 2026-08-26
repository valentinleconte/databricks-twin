"""Tests that fail when the repo contradicts itself.

Each one guards a coupling that is real but invisible: two files that must agree,
where nothing but a human noticing would otherwise catch the drift. Same spirit as
openrag-twin's test_repo_invariants.py — that project's ENGINEERING_LOG bug #4 (a
version coupling that stayed silent until execution) is the cautionary tale for why
these are worth writing at all.

Note: `agent_server/agent.py` is read as text here, not imported. It builds a real
`WorkspaceClient()` at module level (see `sp_workspace_client = WorkspaceClient()`),
so importing it needs live Databricks credentials — exactly the "no live workspace"
constraint this test suite exists to respect. Regex-scanning the source is the
honest tradeoff: it can't catch a syntax error (py_compile in CI already does that),
but it can catch the specific drift these tests are about.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


class TestVectorSearchIndexNameAgrees:
    """agent.py's DOC_SEARCH_INDEX and databricks.yml's granted uc_securable must
    name the same index — otherwise the app gets SELECT on one index while the
    agent code queries a different one, and the failure only shows up as a
    permission error at query time, not at deploy time."""

    def test_agent_py_and_databricks_yml_name_the_same_index(self):
        agent_source = (REPO_ROOT / "agent_server" / "agent.py").read_text()
        match = re.search(r'DOC_SEARCH_INDEX\s*=\s*"([^"]+)"', agent_source)
        assert match, "agent.py: could not find DOC_SEARCH_INDEX"
        agent_index = match.group(1)

        bundle = yaml.safe_load((REPO_ROOT / "databricks.yml").read_text())
        resources = bundle["resources"]["apps"]["agent_langgraph"]["resources"]
        vs_resource = next(r for r in resources if r["name"] == "doc_search_index")

        assert vs_resource["uc_securable"]["securable_full_name"] == agent_index


class TestGenieSpaceIdAgrees:
    """databricks.yml declares the Genie space_id in two places — as the
    GENIE_SPACE_ID env var the app actually reads, and as the genie_space
    resource the bundle grants CAN_RUN on. If they drift, the app either talks
    to a space it has no permission on, or has permission on a space it never
    calls — both fail silently until someone asks a ticket question."""

    def test_env_var_and_granted_resource_name_the_same_space(self):
        bundle = yaml.safe_load((REPO_ROOT / "databricks.yml").read_text())
        app = bundle["resources"]["apps"]["agent_langgraph"]

        env_entry = next(e for e in app["config"]["env"] if e["name"] == "GENIE_SPACE_ID")
        resources = app["resources"]
        genie_resource = next(r for r in resources if r["name"] == "support_tickets_genie")

        assert env_entry["value"] == genie_resource["genie_space"]["space_id"]


class TestTicketTableNameAgrees:
    """create_tickets.sql creates the table; databricks.yml grants SELECT on it.
    If the table name in one drifts from the other, the deploy succeeds and the
    grant silently applies to the wrong (or a nonexistent) table."""

    def test_databricks_yml_grants_the_table_create_tickets_sql_creates(self):
        sql = (REPO_ROOT / "scripts" / "twin" / "create_tickets.sql").read_text()
        match = re.search(r"CREATE OR REPLACE TABLE (\S+)", sql)
        assert match, "create_tickets.sql: could not find the CREATE TABLE statement"
        created_table = match.group(1)

        bundle = yaml.safe_load((REPO_ROOT / "databricks.yml").read_text())
        resources = bundle["resources"]["apps"]["agent_langgraph"]["resources"]
        table_resource = next(r for r in resources if r["name"] == "support_tickets_table")

        assert table_resource["uc_securable"]["securable_full_name"] == created_table


class TestUnknownTicketCaseIsActuallyUnknown:
    """golden_set.yaml's ticket_unknown case is only a real test of "honestly
    report not found" if the ticket id it asks about genuinely isn't in the mock
    data — otherwise a passing test would prove nothing."""

    def test_ticket_999_is_not_in_the_mock_data(self):
        sql = (REPO_ROOT / "scripts" / "twin" / "create_tickets.sql").read_text()
        cases = yaml.safe_load((REPO_ROOT / "eval" / "golden_set.yaml").read_text())["cases"]
        unknown_case = next(c for c in cases if c["category"] == "ticket_unknown")

        ticket_id = re.search(r"ticket (\d+)", unknown_case["question"]).group(1)
        assert f"'{ticket_id}'" not in sql, (
            f"{unknown_case['id']} expects ticket {ticket_id} to not exist, but it's in create_tickets.sql"
        )
