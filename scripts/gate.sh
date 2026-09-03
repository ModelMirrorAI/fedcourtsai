#!/usr/bin/env bash
#
# The single definition of the local gate — the checks CI enforces on every PR.
# AGENTS.md, README.md, and ci.yml all invoke this script, so "green CI" and
# "passes the local gate" cannot silently drift apart.
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
#                            coverage, as CI does; GATE_TEST_WORKERS=1 for a
#                            serial run when debugging)
#   scripts/gate.sh data     validate data + corpus-status
#   scripts/gate.sh schemas  export-schemas + schema-drift check
#
# Named stages preserve the discretion AGENTS.md grants — run the subset that
# fits the change (a docs-only change needs none of the Python stages). With no
# argument every stage runs in the order CI runs them.
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
    uv run pytest ${fanout[@]+"${fanout[@]}"} --cov --cov-report=term-missing
  else
    uv run pytest ${fanout[@]+"${fanout[@]}"}
  fi
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

stage="${1:-all}"
case "$stage" in
  lock) lock ;;
  lint) lint ;;
  types) types ;;
  test) test_stage ;;
  data) data ;;
  schemas) schemas ;;
  all) all ;;
  *)
    echo "unknown stage: $stage" >&2
    echo "usage: scripts/gate.sh [lock|lint|types|test|data|schemas]" >&2
    exit 2
    ;;
esac
