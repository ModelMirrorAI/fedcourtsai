"""Keep the CI lanes' test selections whole, by watching what each test opens.

In the ``data`` and ``docs`` lanes (`scripts/ci_lane.py`) the gate runs only
the tests marked ``reads_data`` / ``reads_docs`` — the ones that read the
committed files that lane lets change. A test that read such a file without
the mark would be skipped in exactly the lane that can break it, and a skipped
test reports nothing. So the full suite, which every code change runs, fails
any test that opens a lane file without the matching mark, and fails collection
when a test module reads one at import time without every test in it marked.

The watch is an audit hook (:func:`sys.addaudithook`): it sees every ``open``
and directory listing this process makes, including those deep in library code
a test calls. It does not see a subprocess's reads; a test that shells out to
something reading a lane file marks itself by hand.

Which files belong to which lane is `scripts/ci_lane.py`'s own classification,
imported here, so the lanes and this guard cannot disagree. `tests/conftest.py`
registers the hooks below.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
_ROOT_PREFIX = str(ROOT) + os.sep

MARKS = {"data": "reads_data", "docs": "reads_docs"}


def _load_ci_lane() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "_ci_lane_for_guard", ROOT / "scripts" / "ci_lane.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ci_lane = _load_ci_lane()

_EVENTS = frozenset({"open", "os.listdir", "os.scandir"})
# Top-level entries a lane file can live under; everything else (src/, tests/,
# the virtualenv, …) is dismissed before classification, which keeps the hook
# cheap on the import-heavy paths it sees most.
_LANE_TOPS = frozenset({"data", "docs", "corpus", "metrics"})

_seen: dict[str, set[str]] = {}
_module_reads: dict[str, dict[str, set[str]]] = {}


def lane_of(rel: str) -> str | None:
    """The lane a repository-relative path belongs to, or None."""
    lane: str = ci_lane.classify([rel])[0]
    return lane if lane in MARKS else None


def _record(event: str, args: tuple[Any, ...]) -> None:
    if event not in _EVENTS or not args:
        return
    target = args[0]
    if target is None or isinstance(target, int):
        return
    try:
        path = os.path.abspath(os.fsdecode(target))
    except (TypeError, ValueError):
        return
    if not path.startswith(_ROOT_PREFIX):
        return
    rel = path[len(_ROOT_PREFIX) :].replace(os.sep, "/")
    top, sep, _ = rel.partition("/")
    if sep and top not in _LANE_TOPS:
        return
    # Listing a lane's own directory is reading the lane.
    lane = rel if (rel in MARKS and event != "open") else lane_of(rel)
    if lane is not None:
        _seen.setdefault(lane, set()).add(rel)


def install() -> None:
    """Install the hook once per process (an audit hook cannot be removed)."""
    if not getattr(sys, "_fedcourts_lane_guard", False):
        sys.addaudithook(_record)
        sys._fedcourts_lane_guard = True  # type: ignore[attr-defined]


def _take() -> dict[str, set[str]]:
    seen = dict(_seen)
    _seen.clear()
    return seen


def _describe(seen: dict[str, set[str]], lanes: list[str]) -> str:
    lines = []
    for lane in lanes:
        files = sorted(seen[lane])
        shown = ", ".join(files[:5]) + (" …" if len(files) > 5 else "")
        lines.append(f"  needs @pytest.mark.{MARKS[lane]} — read {shown}")
    return "\n".join(lines)


# --- pytest hooks (re-exported by tests/conftest.py) --------------------------


def pytest_collectstart(collector: pytest.Collector) -> None:
    if isinstance(collector, pytest.Module):
        _take()


def pytest_collectreport(report: pytest.CollectReport) -> None:
    if report.nodeid.endswith(".py"):
        seen = _take()
        if seen:
            merged = _module_reads.setdefault(report.nodeid, {})
            for lane, files in seen.items():
                merged.setdefault(lane, set()).update(files)


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    problems = []
    for module, seen in sorted(_module_reads.items()):
        mine = [i for i in items if i.nodeid.split("::", 1)[0] == module]
        lanes = [
            lane for lane in seen if any(i.get_closest_marker(MARKS[lane]) is None for i in mine)
        ]
        if lanes:
            problems.append(
                f"{module} reads committed files a CI lane lets change at import "
                "time, so every test in it needs the lane's mark (a module-level "
                "`pytestmark`):\n" + _describe(seen, lanes)
            )
    if problems:
        raise pytest.UsageError("\n".join(problems))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item: pytest.Item) -> Iterator[None]:
    _take()
    yield


@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item: pytest.Item) -> None:
    seen = _take()
    missing = [lane for lane in sorted(seen) if item.get_closest_marker(MARKS[lane]) is None]
    if missing:
        pytest.fail(
            f"{item.nodeid} opened committed files that a CI lane lets change, "
            "without that lane's mark, so the lane would skip it:\n" + _describe(seen, missing),
            pytrace=False,
        )
