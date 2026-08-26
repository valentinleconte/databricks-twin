"""Tests for the golden-set scoring logic in eval/run_eval.py.

score_case() decides whether the agent passed. If it is wrong, the headline number
("13/15") is wrong — a scorer that cannot fail is a scorer that proves nothing.
These tests attack it from the direction that matters: responses that look right
but are not, mirroring openrag-twin's test_eval_scoring.py (same shape, same
philosophy, different transport/citation format — see eval/README.md).
"""

from __future__ import annotations

from typing import Any, ClassVar

import pytest

CITED = (
    "A data lakehouse combines a data lake and a data warehouse.\n\n"
    "Source URL: https://docs.databricks.com/aws/en/lakehouse"
)


class TestKnowledgeScoring:
    case: ClassVar[dict[str, Any]] = {
        "category": "knowledge",
        "expected_source_substrings": ["/lakehouse"],
        "expected_keywords": ["data lake", "data warehouse"],
    }

    def test_correct_citation_and_keyword_passes(self, run_eval):
        passed, _ = run_eval.score_case(self.case, CITED)
        assert passed

    def test_uncited_answer_fails_even_if_factually_right(self, run_eval):
        """The whole grounding claim rests on the citation being present."""
        response = "A data lakehouse combines a data lake and a data warehouse."
        passed, reason = run_eval.score_case(self.case, response)
        assert not passed
        assert "citation" in reason

    def test_citing_the_wrong_page_fails(self, run_eval):
        response = (
            "A data lakehouse combines a data lake and a data warehouse.\n\n"
            "Source URL: https://docs.databricks.com/aws/en/oltp/projects"
        )
        passed, reason = run_eval.score_case(self.case, response)
        assert not passed
        assert "expected one containing" in reason

    def test_right_citation_but_missing_content_fails(self, run_eval):
        """Guards against a citation pasted onto an answer that doesn't say anything."""
        response = "I looked into it.\n\nSource URL: https://docs.databricks.com/aws/en/lakehouse"
        passed, reason = run_eval.score_case(self.case, response)
        assert not passed
        assert "keywords" in reason

    def test_a_non_databricks_link_does_not_count_as_a_citation(self, run_eval):
        response = (
            "A data lakehouse combines a data lake and a data warehouse.\n\n"
            "Source URL: https://example.com/lakehouse"
        )
        passed, _ = run_eval.score_case(self.case, response)
        assert not passed

    def test_citation_with_hallucinated_suffix_still_matches_by_substring(self, run_eval):
        """The regression this project actually hit: the model appended a fabricated
        .html suffix. cited_sources() should still extract the URL — the prompt fix
        (AGENT_INSTRUCTIONS, not the scorer) is what stops the fabrication itself."""
        response = (
            "A data lakehouse combines a data lake and a data warehouse.\n\n"
            "Source URL: https://docs.databricks.com/aws/en/lakehouse.html"
        )
        passed, _ = run_eval.score_case(self.case, response)
        assert passed  # substring match tolerates it; this is why the prompt fix mattered


class TestTicketScoring:
    case: ClassVar[dict[str, Any]] = {"category": "ticket_known", "expected_keywords": ["Open", "Alice Martin"]}

    def test_ticket_data_without_a_doc_citation_passes(self, run_eval):
        passed, _ = run_eval.score_case(self.case, "Ticket 101 is Open, assigned to Alice Martin.")
        assert passed

    def test_citing_the_docs_on_a_ticket_question_fails(self, run_eval):
        """This is the routing failure the whole project exists to catch: the agent
        answered the ticket but cited the doc-search tool to do it."""
        response = (
            "Ticket 101 is Open, assigned to Alice Martin.\n\n"
            "Source URL: https://docs.databricks.com/aws/en/lakehouse"
        )
        passed, reason = run_eval.score_case(self.case, response)
        assert not passed
        assert "ticket tool" in reason

    def test_partial_ticket_data_fails(self, run_eval):
        """all_kw, not any_kw: half the ticket is not the ticket."""
        passed, _ = run_eval.score_case(self.case, "Ticket 101 is Open.")
        assert not passed

    def test_unknown_ticket_must_admit_it(self, run_eval):
        case = {"category": "ticket_unknown", "expected_keywords": ["not found", "no record"]}
        assert run_eval.score_case(case, "No record of ticket 999 was found.")[0]
        assert not run_eval.score_case(case, "Ticket 999 is Open, assigned to Bob.")[0]


class TestMixedScoring:
    case: ClassVar[dict[str, Any]] = {
        "category": "mixed",
        "expected_keywords": ["Open", "Alice Martin"],
        "expected_source_substrings": ["/lakehouse"],
    }

    def test_both_tools_reflected_passes(self, run_eval):
        response = (
            "Ticket 104 is Open, assigned to Alice Martin.\n\n"
            "A data lakehouse combines a data lake and a data warehouse.\n\n"
            "Source URL: https://docs.databricks.com/aws/en/lakehouse"
        )
        assert run_eval.score_case(self.case, response)[0]

    def test_missing_the_ticket_half_fails(self, run_eval):
        response = "A data lakehouse combines a data lake and a data warehouse.\n\nSource URL: https://docs.databricks.com/aws/en/lakehouse"
        passed, reason = run_eval.score_case(self.case, response)
        assert not passed
        assert "ticket keywords" in reason

    def test_missing_the_doc_citation_half_fails(self, run_eval):
        """This is exactly the failure mode the project actually measured: the
        real regression is a second tool call silently never happening."""
        response = "Ticket 104 is Open, assigned to Alice Martin."
        passed, reason = run_eval.score_case(self.case, response)
        assert not passed
        assert "knowledge citation" in reason


class TestEdgeCategories:
    def test_off_topic_must_not_force_a_tool(self, run_eval):
        case = {"category": "off_topic", "expected_keywords": []}
        assert run_eval.score_case(case, "I'm doing well, thanks! How can I help?")[0]
        assert not run_eval.score_case(case, "Hi! Ticket 101 is Open.")[0]
        assert not run_eval.score_case(
            case, "Hello.\n\nSource URL: https://docs.databricks.com/aws/en/lakehouse"
        )[0]

    def test_out_of_corpus_must_admit_the_gap(self, run_eval):
        case = {"category": "out_of_corpus", "expected_keywords": ["no relevant"]}
        assert run_eval.score_case(case, "No relevant information was found.")[0]
        # A confident, plausible, ungrounded answer — the failure mode that matters,
        # and one this project actually hit (see README > Bugs found & fixed).
        assert not run_eval.score_case(
            case, "Go to the Clusters page and enable autoscaling under Settings."
        )[0]

    def test_unknown_category_fails_loudly(self, run_eval):
        """A typo'd category must not silently count as a pass."""
        passed, reason = run_eval.score_case({"category": "typo"}, "anything")
        assert not passed
        assert "unknown category" in reason


class TestHelpers:
    def test_keyword_matching_is_case_insensitive(self, run_eval):
        assert run_eval.any_kw("The status is OPEN", ["open"])
        assert run_eval.all_kw("Open, Alice Martin", ["OPEN", "alice martin"])

    def test_cited_sources_extracts_every_url(self, run_eval):
        text = (
            "See Source URL: https://docs.databricks.com/aws/en/lakehouse and "
            "Source URL: https://docs.databricks.com/aws/en/oltp/projects"
        )
        assert run_eval.cited_sources(text) == [
            "https://docs.databricks.com/aws/en/lakehouse",
            "https://docs.databricks.com/aws/en/oltp/projects",
        ]

    def test_cited_sources_strips_trailing_punctuation(self, run_eval):
        """Guards the exact fix for the .html-hallucination-adjacent case: a URL
        embedded in prose often picks up a trailing comma or period."""
        text = "Source URL: https://docs.databricks.com/aws/en/lakehouse, and that's it."
        assert run_eval.cited_sources(text) == ["https://docs.databricks.com/aws/en/lakehouse"]

    def test_http_error_response_never_scores_as_a_pass(self, run_eval):
        """errored() sentinel must never be scored as an honest answer."""
        cases = [
            {"category": "knowledge", "expected_source_substrings": ["x"], "expected_keywords": ["y"]},
            {"category": "ticket_known", "expected_keywords": ["Open"]},
            {"category": "ticket_unknown", "expected_keywords": ["not found"]},
            {"category": "off_topic", "expected_keywords": []},
            {"category": "out_of_corpus", "expected_keywords": ["no relevant"]},
        ]
        for case in cases:
            passed, reason = run_eval.score_case(case, "__HTTP_ERROR_500__: boom")
            assert not passed
            assert "not scored" in reason


class TestGoldenSetIntegrity:
    """The ground truth is hand-written YAML; nothing else validates it."""

    @staticmethod
    @pytest.fixture(scope="class")
    def cases(run_eval):
        import yaml

        return yaml.safe_load(run_eval.GOLDEN_SET_PATH.read_text())["cases"]

    def test_ids_are_unique(self, cases):
        ids = [c["id"] for c in cases]
        assert len(ids) == len(set(ids))

    def test_every_case_declares_a_category_the_scorer_knows(self, cases):
        known = {"knowledge", "ticket_known", "ticket_unknown", "mixed", "off_topic", "out_of_corpus"}
        assert {c["category"] for c in cases} <= known

    def test_every_case_has_the_fields_its_category_is_scored_on(self, cases):
        for case in cases:
            if case["category"] in {"knowledge", "mixed"}:
                assert case.get("expected_source_substrings"), case["id"]
            if case["category"] != "off_topic":
                assert case.get("expected_keywords"), case["id"]

    def test_expected_sources_point_at_pages_actually_in_the_corpus(self, run_eval, cases):
        """A case expecting a page the corpus never ingested can only ever fail —
        or, worse, pass by citing something else that happens to match."""
        corpus_dir = run_eval.REPO_ROOT / "databricks-docs-md"
        source_urls = "\n".join(
            line
            for p in corpus_dir.glob("*.md")
            for line in p.read_text().splitlines()
            if line.startswith("source_url:")
        )
        for case in cases:
            for substring in case.get("expected_source_substrings", []):
                assert substring in source_urls, f"{case['id']}: {substring!r} not in the corpus"

    def test_ticket_cases_match_the_actual_mock_data(self, cases):
        """Ground truth for ticket cases lives in create_tickets.sql; keep the two
        agreeing rather than trusting the YAML was hand-copied correctly."""
        import re

        sql = (
            (
                __import__("pathlib").Path(__file__).resolve().parents[1]
                / "scripts"
                / "twin"
                / "create_tickets.sql"
            )
            .read_text()
            .lower()
        )
        for case in cases:
            if case["category"] != "ticket_known":
                continue
            ticket_id_match = re.search(r"ticket (\d+)", case["question"])
            if ticket_id_match:
                # A single-ticket lookup: the id and every expected field must
                # actually appear in the mock data.
                assert f"'{ticket_id_match.group(1)}'" in sql, (
                    f"{case['id']}: ticket {ticket_id_match.group(1)} not in create_tickets.sql"
                )
                for kw in case["expected_keywords"]:
                    assert kw.lower() in sql, f"{case['id']}: expected keyword {kw!r} not in create_tickets.sql"
                continue

            # An aggregate question (e.g. "how many tickets are Open?") — verify the
            # expected count actually matches the mock data rather than trusting it
            # was hand-counted correctly.
            status_match = re.search(r"currently (\w+)", case["question"], re.IGNORECASE)
            assert status_match, f"{case['id']}: not a single-ticket lookup and no aggregate pattern found"
            status = status_match.group(1).lower()
            actual_count = len(re.findall(rf"'{status}'", sql))
            assert case["expected_keywords"] == [str(actual_count)], (
                f"{case['id']}: expects {case['expected_keywords']}, "
                f"but create_tickets.sql actually has {actual_count} '{status}' ticket(s)"
            )


class TestVarianceReporting:
    """--runs exists so a lucky run can't be reported as a property. These assert
    the gate is actually a gate — same tests as openrag-twin's, same function shape."""

    cases: ClassVar[list[dict[str, Any]]] = [
        {"id": "know-01", "category": "knowledge"},
        {"id": "ticket-01", "category": "ticket_known"},
    ]

    @staticmethod
    def _runs(*outcomes_per_run):
        return [
            [{"id": c["id"], "passed": p} for c, p in zip(TestVarianceReporting.cases, outcomes, strict=True)]
            for outcomes in outcomes_per_run
        ]

    def test_all_green_across_all_runs_is_green(self, run_eval, capsys):
        runs = self._runs((True, True), (True, True), (True, True))
        assert run_eval.report(self.cases, runs)
        assert "3/2" not in capsys.readouterr().out

    def test_a_flaky_case_fails_the_gate_by_default(self, run_eval):
        """2/3 is not a pass. This is the whole point of measuring variance —
        and this project's real 82% mean is exactly this shape of result."""
        runs = self._runs((True, True), (True, False), (True, True))
        assert not run_eval.report(self.cases, runs)

    def test_allow_flaky_downgrades_flakiness_to_a_warning(self, run_eval):
        runs = self._runs((True, True), (True, False), (True, True))
        assert run_eval.report(self.cases, runs, allow_flaky=True)

    def test_a_case_that_never_passes_fails_even_with_allow_flaky(self, run_eval):
        runs = self._runs((True, False), (True, False), (True, False))
        assert not run_eval.report(self.cases, runs, allow_flaky=True)

    def test_flaky_cases_are_named_in_the_output(self, run_eval, capsys):
        runs = self._runs((True, True), (True, False), (True, True))
        run_eval.report(self.cases, runs)
        out = capsys.readouterr().out
        assert "ticket-01" in out and "2/3" in out
        assert "min 50%" in out and "max 100%" in out

    def test_single_run_keeps_the_familiar_summary(self, run_eval, capsys):
        assert run_eval.report(self.cases, self._runs((True, True)))
        out = capsys.readouterr().out
        assert "TOTAL: 2/2 passed (100%)" in out
        assert "Stability" not in out


class TestBackendErrorsAreNotScores:
    """Same real incident class as openrag-twin's: a run that can't tell 'the
    model was wrong' from 'the service was down' produces numbers worse than none."""

    ERROR = "__HTTP_ERROR_500__: Internal Server Error"

    def test_errored_detects_the_sentinel(self, run_eval):
        assert run_eval.errored(self.ERROR)
        assert not run_eval.errored("A perfectly normal answer.")

    def test_errors_invalidate_the_whole_run(self, run_eval, capsys):
        cases = [
            {"id": "know-01", "category": "knowledge"},
            {"id": "know-02", "category": "knowledge"},
        ]
        runs = [
            [
                {"id": "know-01", "passed": True, "errored": False},
                {"id": "know-02", "passed": False, "errored": True},
            ]
        ]
        assert not run_eval.report(cases, runs)
        out = capsys.readouterr().out
        assert "NOT scored" in out and "know-02" in out
        assert "not a valid measurement" in out

    def test_errors_invalidate_even_with_allow_flaky(self, run_eval):
        cases = [{"id": "know-01", "category": "knowledge"}]
        runs = [[{"id": "know-01", "passed": False, "errored": True}]]
        assert not run_eval.report(cases, runs, allow_flaky=True)

    def test_run_aborts_after_repeated_backend_errors(self, run_eval, monkeypatch):
        """Once the backend is down, continuing burns time to produce a
        score-shaped number that measures nothing."""
        asked = []

        def fake_ask(question):
            asked.append(question)
            return self.ERROR

        monkeypatch.setattr(run_eval, "ask", fake_ask)
        cases = [{"id": f"c{i}", "category": "knowledge", "question": f"q{i}"} for i in range(10)]

        with pytest.raises(run_eval.BackendUnavailable, match="consecutive backend errors"):
            run_eval.run_once(cases, abort_after=3)

        assert len(asked) == 3  # stopped early, did not walk all ten

    def test_a_healthy_run_does_not_abort(self, run_eval, monkeypatch):
        monkeypatch.setattr(run_eval, "ask", lambda _q: "fine")
        cases = [{"id": "c1", "category": "off_topic", "question": "hi"}]
        results = run_eval.run_once(cases)
        assert results[0]["errored"] is False

    def test_isolated_errors_do_not_abort_but_still_invalidate(self, run_eval, monkeypatch):
        """One transient 500 shouldn't kill the run, but it must not be silently
        absorbed into the score either."""
        responses = iter(["fine", self.ERROR, "fine", "fine"])
        monkeypatch.setattr(run_eval, "ask", lambda _q: next(responses))
        cases = [{"id": f"c{i}", "category": "off_topic", "question": "hi"} for i in range(4)]

        results = run_eval.run_once(cases, abort_after=3)
        assert [r["errored"] for r in results] == [False, True, False, False]
        assert not run_eval.report(cases, [results])
