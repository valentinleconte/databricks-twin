"""Shared fixtures for tests_twin/ — loads this project's own scripts as modules
without needing them importable as a package (they're standalone CLI scripts, not
part of the `agent_server` package).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="session")
def run_eval():
    return _load(REPO_ROOT / "eval" / "run_eval.py", "twin_run_eval")


@pytest.fixture(scope="session")
def setup_resources():
    """setup_resources.py does `sys.path.insert(...); from dbsql import run_sql` at
    module level — dbsql.py itself is side-effect-free at import (just reads env
    vars), so this loads cleanly with no live Databricks connection."""
    return _load(REPO_ROOT / "scripts" / "twin" / "setup_resources.py", "twin_setup_resources")
