"""Lightweight MLflow-native evaluation, layered on top of the same golden set used by
eval/run_eval.py (eval/golden_set.yaml) rather than the template's placeholder
Vietnamese-cuisine/Fibonacci ConversationSimulator test cases.

Deliberately NOT the full 9-scorer + ConversationSimulator setup the template ships:
a persona-driven multi-turn simulation plus 9 LLM-judge scorers is a lot of extra LLM
calls (judge calls on top of simulated conversation turns) for a demo project. The
golden set (eval/run_eval.py) is the primary evaluation — deterministic, cheap,
content-based scoring, one call per question, run three times to measure stability
(see NOTES.md for the ~82% mean / two diagnosed failure modes it found).

This script exists to demonstrate the *other* half honestly: that mlflow.genai.evaluate()
and its built-in LLM-judge scorers are usable against this same agent, without paying for
a full simulator run. Two scorers, chosen for what they actually check here:
  - RelevanceToQuery: does the answer address what was asked (single-turn, cheap).
  - ToolCallCorrectness: were the *right* tools called for each question, judged
    against the trace MLflow already captures via mlflow.langchain.autolog() in
    agent_server/agent.py — this is the one score.py's regex approach cannot give you
    directly (it infers routing correctness indirectly, from citation shape).

Usage:
    uv run agent-evaluate
"""

import asyncio
import logging
from pathlib import Path

import mlflow
import yaml
from dotenv import load_dotenv
from mlflow.genai.agent_server import get_invoke_function
from mlflow.genai.scorers import RelevanceToQuery, ToolCallCorrectness
from mlflow.types.responses import ResponsesAgentRequest

load_dotenv(dotenv_path=".env", override=True)
logging.getLogger("mlflow.utils.autologging_utils").setLevel(logging.ERROR)

# need to import agent for our @invoke-registered function to be found
from agent_server import agent  # noqa: F401

GOLDEN_SET_PATH = Path(__file__).resolve().parent.parent / "eval" / "golden_set.yaml"

golden_set = yaml.safe_load(GOLDEN_SET_PATH.read_text())
# mlflow.genai.evaluate(data=..., predict_fn=...) passes each row's "inputs" dict to
# predict_fn as keyword arguments — predict_fn below takes `input`, so each row's
# "inputs" key must be named "input" too.
eval_data = [
    {"inputs": {"input": [{"role": "user", "content": case["question"]}]}}
    for case in golden_set["cases"]
]

invoke_fn = get_invoke_function()
assert invoke_fn is not None, (
    "No function registered with the `@invoke` decorator found."
    "Ensure you have a function decorated with `@invoke()`."
)

if asyncio.iscoroutinefunction(invoke_fn):
    import nest_asyncio

    nest_asyncio.apply()

    def predict_fn(input: list[dict], **kwargs) -> dict:
        req = ResponsesAgentRequest(input=input)
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(invoke_fn(req))
        return response.model_dump()
else:

    def predict_fn(input: list[dict], **kwargs) -> dict:
        req = ResponsesAgentRequest(input=input)
        response = invoke_fn(req)
        return response.model_dump()


def evaluate():
    mlflow.genai.evaluate(
        data=eval_data,
        predict_fn=predict_fn,
        scorers=[
            RelevanceToQuery(),
            ToolCallCorrectness(),
        ],
    )


if __name__ == "__main__":
    evaluate()
