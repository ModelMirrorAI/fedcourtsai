# Agent development workflow

Agents run **headless inside GitHub Actions** — no interactive prompts and an
ephemeral runner. If you need input or hit a blocker, surface it in writing in
whatever channel your run grants (the PR description / `gh pr comment` in
`run:dev`; your reasoning/notes doc in `run:predict` / `run:evaluate`) and make a
conservative choice; you can't wait for a live answer. Nothing on the runner
persists unless it is pushed off it: code via a branch + PR, corpus data via
`dvc push`. See AGENTS.md ("Where you run") for the full contract.

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
   If you changed the models: `uv run fedcourts export-schemas schemas` and commit.
4. **Open one focused PR** against `main` with a conventional-commit title and a
   description of what changed and why. For `run:predict`/`run:evaluate`, the
   workflow does steps 1 and 4 for you — you only write files.
5. **CI** (`ci.yml`, `lint-actions.yml`) must be green before merge.

Keep PRs small and reviewable. Prefer a correct, tested, conservative change over a
large speculative one.
