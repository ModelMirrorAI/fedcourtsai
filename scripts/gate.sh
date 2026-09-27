#!/usr/bin/env bash
#
# The single definition of the local gate — the checks CI enforces on every PR.
# AGENTS.md, README.md, and ci.yml all invoke this script, so "green CI" and
# "passes the local gate" cannot silently drift apart for a code change; a
# data-only or docs-only change runs a lane subset (*The CI lanes* in
# docs/testing.md).
#
# Assumes a synced environment (`uv sync`); CI's setup step and the devcontainer
# both provide one, so the stages below are pure checks with no setup of their own.
#
# Usage:
#   scripts/gate.sh          every stage, in CI order, failing on first failure
#   scripts/gate.sh lock     uv lock --check (the lockfile matches pyproject)
#   scripts/gate.sh lint     ruff format --check + ruff check
#   scripts/gate.sh types    mypy
#   scripts/gate.sh test     pytest, fanned across cores (set GATE_COV=1 for
#                            coverage, as CI does, measured under Python's
#                            sys.monitoring — COVERAGE_CORE overrides the core
#                            for a comparison run; GATE_TEST_WORKERS=1 for a
#                            serial run when debugging)
#   scripts/gate.sh data     validate data + corpus-status
#   scripts/gate.sh schemas  export-schemas + schema-drift check
#   scripts/gate.sh data-tests  only the tests marked reads_data
#   scripts/gate.sh docs-tests  only the tests marked reads_docs
#
# Several stages may be named at once (`scripts/gate.sh lint types`); they run
# in the order given, failing on the first failure.
#
# Named stages preserve the discretion AGENTS.md grants — run the subset that
# fits the change (a docs-only change needs only docs-tests). With no argument
# every stage runs in the order CI runs them; the two lane test stages are not
# part of that, since `test` already runs every test they select.
set -euo pipefail

# CI installs with `uv sync --locked`, which refuses a lock that has drifted
# from pyproject.toml. Modelled here so that refusal is checkable where AGENTS.md
# tells contributors to check things, rather than only on the PR.
lock() {
  uv lock --check
}

lint() {
  uv run ruff format --check .
  uv run ruff check .
}

types() {
  uv run mypy
}

# Named test_stage, not test: `test` is a shell builtin, and shadowing it is a
# footgun. The CLI stage name stays `test` (see the case below).
#
# The suite is a few thousand offline, independent tests and the gate runs on
# every PR, so it fans out across the machine's CPUs with pytest-xdist. No test
# depends on state another left behind — the process-wide caches are reset per
# test by autouse fixtures in tests/conftest.py, and corpus, data root, cwd and
# environment are built per test under `tmp_path` / `monkeypatch` — so any test
# may land on any worker. `loadgroup` distributes per test as the default `load`
# does, and additionally honours `@pytest.mark.xdist_group`, so tests that ever
# do need to share one worker can say so where they live rather than needing
# this stage changed underneath them. pytest-cov measures per worker and
# combines into the single `.coverage` file CI's summary step reads.
#
# GATE_TEST_WORKERS overrides the count: `auto` (the default) is one worker per
# available CPU, a number pins it, and 1 drops xdist entirely — which is what a
# debugging session wants, since a worker has no terminal for `breakpoint()` and
# output interleaves.
test_stage() {
  local workers="${GATE_TEST_WORKERS:-auto}"
  local fanout=()
  if [ "$workers" != "1" ]; then
    fanout=(-n "$workers" --dist loadgroup)
  fi
  # `${a[@]+"${a[@]}"}` rather than a bare `"${a[@]}"`: under `set -u` the bare
  # form is an unbound-variable error on an empty array before bash 4.4, which
  # would break the serial path — the one this script promises a debugger — on a
  # Mac's system bash while leaving the default path working.
  if [ "${GATE_COV:-0}" = "1" ]; then
    # sys.monitoring rather than coverage.py's default C tracer: about a third of
    # the wall time for the same line-coverage result. What it cannot do on 3.12
    # — branch coverage, dynamic contexts, non-thread concurrency — this
    # project's coverage config does not use; configuring one makes coverage
    # warn and fall back to the C tracer, slower but not failing.
    COVERAGE_CORE="${COVERAGE_CORE:-sysmon}" \
      uv run pytest ${fanout[@]+"${fanout[@]}"} --cov --cov-report=term-missing
  else
    uv run pytest ${fanout[@]+"${fanout[@]}"}
  fi
}

# The CI lanes' narrowed test stage (scripts/ci_lane.py). In the data and docs
# lanes ci.yml runs this in place of `test`: only the tests that open the
# committed files that lane lets change. tests/lane_guard.py keeps the marks
# in step — the full suite fails any test it sees open a lane file without its
# lane's mark (its blind spots: docs/testing.md, *The CI lanes*). pytest exits 5 when
# a mark selects nothing, which here means no test reads that lane's files: a
# pass, not a failure. Fanned out like `test`: the selection is small, but the
# data-reading tests walk the whole committed tree and dominate the stage.
lane_tests() {
  local mark="$1"
  local workers="${GATE_TEST_WORKERS:-auto}"
  local fanout=()
  if [ "$workers" != "1" ]; then
    fanout=(-n "$workers" --dist loadgroup)
  fi
  local rc=0
  uv run pytest ${fanout[@]+"${fanout[@]}"} -m "$mark" --durations=5 || rc=$?
  if [ "$rc" -eq 5 ]; then
    echo "no test carries ${mark}; nothing in this lane to run"
    return 0
  fi
  return "$rc"
}

data() {
  uv run fedcourts validate data
  uv run fedcourts corpus-status
}

schemas() {
  uv run fedcourts export-schemas schemas
  git diff --exit-code schemas
}

all() {
  lock
  lint
  types
  test_stage
  data
  schemas
}

usage="usage: scripts/gate.sh [lock|lint|types|test|data|schemas|data-tests|docs-tests|all] ..."

# Every named stage is checked before any runs, so a typo fails at once rather
# than after the stages ahead of it, and no argument is ever silently ignored.
[ "$#" -eq 0 ] && set -- all
for stage in "$@"; do
  case "$stage" in
    lock | lint | types | test | data | schemas | data-tests | docs-tests | all) ;;
    *)
      echo "unknown stage: $stage" >&2
      echo "$usage" >&2
      exit 2
      ;;
  esac
done

for stage in "$@"; do
  case "$stage" in
    lock) lock ;;
    lint) lint ;;
    types) types ;;
    test) test_stage ;;
    data) data ;;
    schemas) schemas ;;
    data-tests) lane_tests reads_data ;;
    docs-tests) lane_tests reads_docs ;;
    all) all ;;
  esac
done
