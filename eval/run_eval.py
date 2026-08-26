#!/usr/bin/env python3
"""Run the golden set against the live databricks-twin agent and score it.

Usage:
    uv run --with pyyaml python3 eval/run_eval.py [--save results.json]

Same shape as openrag-twin's eval/run_eval.py (see that file's docstring for the full
rationale) — a lightweight, content-based harness (regex/substring checks on the final
answer text), not a framework like RAGAS. What's different here: the transport. This
template's local server speaks the MLflow Responses API directly on
POST http://localhost:8000/invocations (no API key — local dev runs as the
CLI-authenticated user, not behind the app's own auth), and citations come back as a
plain "Source URL: https://..." line rather than markdown [source](...) links.

The agent is stochastic, so a single N/N run is a sample, not a property. `--runs N`
replays the whole set N times and reports per-case stability, same as openrag-twin.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
GOLDEN_SET_PATH = REPO_ROOT / "eval" / "golden_set.yaml"
INVOKE_URL = "http://localhost:8000/invocations"

# ask() returns this prefix instead of an answer when the backend itself failed
# (HTTP 5xx / connection error). That is an infrastructure fault, not a wrong answer,
# and the two must never be added together — see `errored()` and the ERROR handling below.
HTTP_ERROR_PREFIX = "__HTTP_ERROR_"

SOURCE_URL_RE = re.compile(r"https://docs\.databricks\.com/[^\s,)]+")
TICKET_MARKER_RE = re.compile(r"\bticket[- ]?\d+\b", re.IGNORECASE)


def ask(question: str) -> str:
    body = json.dumps({"input": [{"role": "user", "content": question}]}).encode()
    req = urllib.request.Request(INVOKE_URL, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = json.loads(resp.read())
            for item in payload.get("output", []):
                if item.get("type") == "message":
                    texts = [c.get("text", "") for c in item.get("content", []) if c.get("type") == "output_text"]
                    if texts:
                        return "\n".join(texts)
            return "__NO_MESSAGE_OUTPUT__"
    except urllib.error.HTTPError as e:
        return f"__HTTP_ERROR_{e.code}__: {e.read().decode(errors='replace')[:300]}"
    except urllib.error.URLError as e:
        sys.exit(f"Could not reach {INVOKE_URL}: {e}\nIs the local server up? Try `uv run start-app`.")


def errored(response: str) -> bool:
    """True when the backend failed rather than the agent answering badly.

    Same lesson as openrag-twin: an eval that cannot tell "the model was wrong" from
    "the service was down" produces numbers that are worse than no numbers.
    """
    return response.startswith(HTTP_ERROR_PREFIX)


def any_kw(text: str, keywords: list[str]) -> bool:
    low = text.lower()
    return any(kw.lower() in low for kw in keywords)


def all_kw(text: str, keywords: list[str]) -> bool:
    low = text.lower()
    return all(kw.lower() in low for kw in keywords)


def cited_sources(text: str) -> list[str]:
    return [u.rstrip(".,") for u in SOURCE_URL_RE.findall(text)]


def score_case(case: dict[str, Any], response: str) -> tuple[bool, str]:
    if errored(response):
        return False, f"backend error, not scored: {response[:120]}"

    category = case["category"]
    sources = cited_sources(response)
    has_ticket_marker = bool(TICKET_MARKER_RE.search(response))

    if category == "knowledge":
        cited_ok = any(
            any(sub in src for sub in case["expected_source_substrings"]) for src in sources
        )
        kw_ok = any_kw(response, case["expected_keywords"])
        if not sources:
            return False, "no 'Source URL:' citation found"
        if not cited_ok:
            return (
                False,
                f"cited {sources}, expected one containing {case['expected_source_substrings']}",
            )
        if not kw_ok:
            return False, f"missing all expected keywords {case['expected_keywords']}"
        return True, f"cited {sources}"

    if category == "ticket_known":
        if sources:
            return False, f"cited docs sources {sources}, should have used the ticket tool instead"
        if not all_kw(response, case["expected_keywords"]):
            return False, f"missing one of {case['expected_keywords']}"
        return True, "ticket data present, no doc citation"

    if category == "ticket_unknown":
        if not any_kw(response, case["expected_keywords"]):
            return False, f"missing a 'not found' style admission {case['expected_keywords']}"
        return True, "correctly reported unknown ticket"

    if category == "mixed":
        ticket_ok = all_kw(response, case["expected_keywords"])
        cited_ok = any(
            any(sub in src for sub in case["expected_source_substrings"]) for src in sources
        )
        if not ticket_ok:
            return False, f"missing ticket keywords {case['expected_keywords']}"
        if not cited_ok:
            return (
                False,
                f"missing expected knowledge citation {case['expected_source_substrings']}",
            )
        return True, f"both tools reflected in the answer, cited {sources}"

    if category == "off_topic":
        if sources or has_ticket_marker:
            return False, "forced a tool on a non-question"
        return True, "answered without forcing a tool"

    if category == "out_of_corpus":
        if not any_kw(response, case["expected_keywords"]):
            return False, f"did not admit the gap; response: {response[:200]!r}"
        return True, "honestly reported no relevant sources"

    return False, f"unknown category {category!r}"


class BackendUnavailable(RuntimeError):
    """Raised when the backend fails repeatedly — the run is not a measurement."""


def run_once(cases: list[dict[str, Any]], *, abort_after: int = 3) -> list[dict[str, Any]]:
    """Ask every case once and score it. One entry per case, in order.

    Aborts after `abort_after` consecutive backend errors: once the service is down,
    continuing only burns time and produces a score-shaped number that measures nothing.
    """
    results = []
    consecutive_errors = 0
    for case in cases:
        t0 = time.monotonic()
        response = ask(case["question"])
        elapsed = time.monotonic() - t0
        passed, reason = score_case(case, response)
        is_error = errored(response)

        results.append(
            {
                "id": case["id"],
                "category": case["category"],
                "question": case["question"],
                "passed": passed,
                "errored": is_error,
                "reason": reason,
                "response": response,
                "elapsed_s": round(elapsed, 1),
            }
        )

        mark = "ERROR" if is_error else ("PASS" if passed else "FAIL")
        print(f"[{mark:<5}] {case['id']:<12} ({case['category']:<14} {elapsed:>4.1f}s)  {reason}")
        if not passed and not is_error:
            print(f"         Q: {case['question']}")
            print(f"         A: {response[:220]}{'...' if len(response) > 220 else ''}")

        consecutive_errors = consecutive_errors + 1 if is_error else 0
        if consecutive_errors >= abort_after:
            raise BackendUnavailable(
                f"{consecutive_errors} consecutive backend errors — aborting.\n"
                f"Last: {response[:200]}\n"
                "Fix the local server and re-run; a partial run is not a score."
            )

    return results


def report(
    cases: list[dict[str, Any]], runs: list[list[dict[str, Any]]], *, allow_flaky: bool = False
) -> bool:
    """Print the summary and return whether the suite should be considered green."""
    run_count = len(runs)
    passes_by_id: dict[str, int] = {c["id"]: 0 for c in cases}
    errors_by_id: dict[str, int] = {c["id"]: 0 for c in cases}
    category_by_id = {c["id"]: c["category"] for c in cases}
    for run in runs:
        for result in run:
            passes_by_id[result["id"]] += bool(result["passed"])
            errors_by_id[result["id"]] += bool(result.get("errored"))

    total_errors = sum(errors_by_id.values())
    per_run_totals = [sum(r["passed"] for r in run) for run in runs]
    total_cases = len(cases)

    print(f"\n{'=' * 60}")
    if run_count == 1:
        passed_total = per_run_totals[0]
        print(
            f"TOTAL: {passed_total}/{total_cases} passed ({100 * passed_total / total_cases:.0f}%)"
        )
    else:
        rates = [100 * t / total_cases for t in per_run_totals]
        mean = sum(rates) / run_count
        print(
            f"TOTAL over {run_count} runs: "
            + ", ".join(f"{t}/{total_cases}" for t in per_run_totals)
            + f"  (mean {mean:.0f}%, min {min(rates):.0f}%, max {max(rates):.0f}%)"
        )

    by_category: dict[str, list[int]] = {}
    for case_id, count in passes_by_id.items():
        by_category.setdefault(category_by_id[case_id], []).append(count)

    print("By category (cases passing every run):")
    for category, counts in by_category.items():
        stable = sum(1 for c in counts if c == run_count)
        print(f"  {category:<14} {stable}/{len(counts)}")

    always = [i for i, c in passes_by_id.items() if c == run_count]
    never = [i for i, c in passes_by_id.items() if c == 0]
    flaky = {i: c for i, c in passes_by_id.items() if 0 < c < run_count}

    if total_errors:
        errored_ids = sorted(i for i, c in errors_by_id.items() if c)
        print(
            f"\n!! {total_errors} case-run(s) hit a backend error and were NOT scored: "
            + ", ".join(errored_ids)
            + "\n   These are infrastructure faults (service down, timeout), not routing"
            "\n   failures. The numbers above are not a valid measurement — fix the"
            "\n   stack and re-run rather than reporting them."
        )

    if run_count > 1:
        print(f"\nStability: {len(always)}/{total_cases} cases passed all {run_count} runs.")
        if flaky:
            print("  Flaky (the cases worth looking at):")
            for case_id, count in sorted(flaky.items(), key=lambda kv: kv[1]):
                print(f"    {case_id:<12} {count}/{run_count}")
        if never:
            print(f"  Never passed: {', '.join(sorted(never))}")

    if total_errors:
        return False
    if never:
        return False
    return True if allow_flaky else not flaky


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--save", type=Path, default=None, help="Save full results as JSON to this path"
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Replay the whole set N times and report per-case stability (default: 1)",
    )
    parser.add_argument(
        "--allow-flaky",
        action="store_true",
        help="With --runs, exit 0 if every case passed at least once (default: require N/N)",
    )
    parser.add_argument(
        "--ids",
        type=str,
        default=None,
        help="Comma-separated case ids to run instead of the full set, e.g. know-01,ticket-04,edge-02",
    )
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="Run only cases in this category (knowledge, ticket_known, ticket_unknown, mixed, off_topic, out_of_corpus)",
    )
    args = parser.parse_args()

    golden_set = yaml.safe_load(GOLDEN_SET_PATH.read_text())
    cases = golden_set["cases"]

    if args.ids:
        wanted = {i.strip() for i in args.ids.split(",")}
        cases = [c for c in cases if c["id"] in wanted]
        missing = wanted - {c["id"] for c in cases}
        if missing:
            sys.exit(f"Unknown case id(s): {', '.join(sorted(missing))}")
    elif args.category:
        cases = [c for c in cases if c["category"] == args.category]
        if not cases:
            sys.exit(f"No cases in category {args.category!r}")

    if args.runs < 1:
        sys.exit("--runs must be >= 1")

    print(f"Running {len(cases)} cases x {args.runs} run(s) against {INVOKE_URL}\n")

    runs: list[list[dict[str, Any]]] = []
    for run_index in range(args.runs):
        if args.runs > 1:
            print(f"--- run {run_index + 1}/{args.runs} ---")
        try:
            runs.append(run_once(cases))
        except BackendUnavailable as e:
            print(f"\n{e}", file=sys.stderr)
            sys.exit(2)
        if args.runs > 1:
            passed = sum(r["passed"] for r in runs[-1])
            print(f"    run {run_index + 1}: {passed}/{len(cases)}\n")

    ok = report(cases, runs, allow_flaky=args.allow_flaky)

    if args.save:
        payload: Any = runs[0] if args.runs == 1 else {"runs": runs, "run_count": args.runs}
        args.save.write_text(json.dumps(payload, indent=2))
        print(f"\nFull results saved to {args.save}")

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
