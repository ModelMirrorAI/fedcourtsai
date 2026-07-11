# Contributing

Thanks for your interest in FedCourtsAI. This is an experimental research project
with an unusual shape: most feature work is done by AI coding agents driven by a
**label-driven pipeline of GitHub Actions**, and the data is produced by the
pipeline rather than by hand. A few things are worth knowing before you contribute.

## The model in one minute

- Work is represented as **GitHub issues**. Applying a `run:*` label triggers the
  matching workflow (see the table in the [README](README.md) and
  [`docs/pipeline.md`](docs/pipeline.md)). Applying those labels is **maintainer-
  gated** and is the pipeline's trust boundary — a maintainer applies the label to
  an issue after triage; there is no public form that starts a run (see
  [SECURITY.md](SECURITY.md)).
- **Never commit to `main`.** Every change lands through a focused pull request
  against `main`, which must pass the `gate` check before it can merge.
- **Stay in your lane.** Pipeline-code changes don't touch `data/`; data-production
  runs don't change pipeline code to make a task easier.

The canonical, complete instructions live in **[AGENTS.md](AGENTS.md)** — it is the
single source of truth for both human and AI contributors. Read it before opening a
PR. [`docs/agent-workflow.md`](docs/agent-workflow.md) walks through how an
agent-driven run actually flows.

## Opening an issue

- **Found a bug or have an idea?** Use the *Bug report* or *Feature / idea* form on
  the [new-issue page](../../issues/new/choose).
- **Want a data run** (e.g. refresh a case)? Open a regular
  issue describing it. Triggering the run is maintainer-only — a maintainer applies
  the `run:*` label, the trust boundary for anything that spends compute or writes
  the corpus.

## Submitting a pull request

1. Branch off `main` (`git checkout -b <type>/<short-topic>`).
2. Make a focused change. Match the surrounding code's style; the project is fully
   typed (`mypy --strict`) with tests for new behavior.
3. Run the parts of the local gate that fit your change — CI is the backstop, but
   honest local confidence matters:

   ```bash
   uv sync
   uv run ruff format --check .
   uv run ruff check .
   uv run mypy
   uv run pytest
   uv run fedcourts validate data
   uv run fedcourts export-schemas schemas   # if you changed a pydantic model
   ```

4. Keep the docs in step — if your change makes any doc stale (`README.md`,
   `AGENTS.md`, `docs/`, prompts, docstrings), update it in the same PR. Where
   your change affects pipeline output, a produced example in the PR
   description is appreciated (see AGENTS.md, "Keep the artifact in view").
5. Use a conventional-commit-style title (e.g. `fix(pull): …`). If the PR finishes
   an issue, put `Closes #<n>` in the description.

## Ground rules

- Be respectful — see the [Code of Conduct](CODE_OF_CONDUCT.md).
- Don't weaken validation, CI, lint, type, or security checks to make a change pass.
- **No secrets in code, data, or logs.** Tokens arrive only as environment
  variables and never get printed, logged, or committed.
- These are experimental predictions, **not legal advice**. Do not feed privileged
  or sealed material into the pipeline.

Questions that aren't a bug or feature? Open a blank issue or start a discussion.
