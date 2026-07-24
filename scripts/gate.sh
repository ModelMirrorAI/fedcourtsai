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
#   scripts/gate.sh lint     ruff format --check + ruff check
#   scripts/gate.sh types    mypy
#   scripts/gate.sh test     pytest  (set GATE_COV=1 for coverage, as CI does)
#   scripts/gate.sh data     validate data + corpus-status
#   scripts/gate.sh schemas  export-schemas + schema-drift check
#
# Named stages preserve the discretion AGENTS.md grants — run the subset that
# fits the change (a docs-only change needs none of the Python stages). With no
# argument every stage runs in the order CI runs them.
set -euo pipefail

lint() {
  uv run ruff format --check .
  uv run ruff check .
}

types() {
  uv run mypy
}

# Named test_stage, not test: `test` is a shell builtin, and shadowing it is a
# footgun. The CLI stage name stays `test` (see the case below).
test_stage() {
  if [ "${GATE_COV:-0}" = "1" ]; then
    uv run pytest --cov --cov-report=term-missing
  else
    uv run pytest
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
  lint
  types
  test_stage
  data
  schemas
}

stage="${1:-all}"
case "$stage" in
  lint) lint ;;
  types) types ;;
  test) test_stage ;;
  data) data ;;
  schemas) schemas ;;
  all) all ;;
  *)
    echo "unknown stage: $stage" >&2
    echo "usage: scripts/gate.sh [lint|types|test|data|schemas]" >&2
    exit 2
    ;;
esac
