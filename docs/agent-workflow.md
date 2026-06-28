# Agent development workflow

Every agent (and human) change lands the same way.

1. **Branch off `main`.** Never commit to `main`.
   `git switch -c <type>/<short-description>`
2. **Do the work**, scoped to the task. Pipeline tasks don't touch `data/`; data
   tasks don't touch pipeline code.
3. **Pass the local gate:**
   ```bash
   uv run ruff format --check . && uv run ruff check . && uv run mypy && uv run pytest
   uv run fedcourts validate data
   ```
   `pytest` includes an offline **stub-cascade smoke** (`tests/test_cascade_smoke.py`)
   that runs provision → predict → evaluate → `validate` over the fixture corpus with
   no network, so a broken predict/evaluate cell surfaces in seconds before you open a
   PR; run just it with `uv run pytest -k cascade_smoke`.
   If you changed the models: `uv run fedcourts export-schemas schemas` and commit.
4. **Open one focused PR** against `main` with a conventional-commit title and a
   description of what changed and why. For `run:predict`/`run:evaluate`, the
   workflow does steps 1 and 4 for you — you only write files.
5. **CI** (`ci.yml`, `lint-actions.yml`) must be green before merge.

Keep PRs small and reviewable. Prefer a correct, tested, conservative change over a
large speculative one.
