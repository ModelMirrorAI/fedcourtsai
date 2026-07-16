# AGENTS.md

Canonical instructions for AI coding agents (Claude Code, Codex, Gemini) in
this repository. `CLAUDE.md` points here. Read this fully before doing anything.

## What this project is

fedcourtsai predicts events in US federal courts — currently SCOTUS dockets
only (cert grant/deny, votes, reasoning) — as a label-driven pipeline of GitHub
Actions; see `docs/pipeline.md`. There are two very different kinds of work,
and you are doing exactly one of them in any given run: **pipeline
development** (change the Python package, workflows, docs, schemas, or prompts
— in an interactive session on the branch-and-PR flow below, like any
contributor; do **not** touch `data/`) or **data production** (`run:pull` /
`run:predict` / `run:evaluate` / `run:backtest` — produce or update the corpus
and/or the derived artifacts under `data/`; do **not** change pipeline code to
make your task easier, and never weaken validation, CI, lint, type, or
security checks).

## Where you run: headless in CI

Every `run:*` task runs inside a GitHub Actions runner — a fresh, **ephemeral,
non-interactive** container. Two consequences shape everything you do:

- **No interactive input.** You cannot ask a question and wait for an answer.
  If you are blocked or under-specified, **leave it in writing where a
  maintainer will see it**: a structured **`flags.json`** note alongside your
  output in `run:predict` / `run:evaluate` (the durable channel — the `collect`
  job rolls every cell's flags into the run PR and the Actions summary, so the
  note survives the trigger issue's closure), with `reasoning.md` /
  `evaluation.md` for the detail; a trigger-issue comment is lost when the
  issue closes. In an interactive development session, the PR description is
  the channel. Then make the most conservative reasonable choice and finish —
  never stall waiting for a reply that cannot come.
- **The runner is thrown away.** Work survives **only if it is pushed off the
  runner** before you finish. Code, docs, config, and schemas go to GitHub via
  a branch + PR (in `run:predict` / `run:evaluate` you only *write files* — the
  workflow commits, pushes, and opens the PR; do **not** push yourself).
  Corpus / bulk data goes to the remote stores (the corpus remote and the per-case
  content store; the run-pull and run-seed writer jobs own this) — a data file never pushed
  to a remote is lost with the runner. See `docs/data-pipeline.md`.

## The golden rules

- **Branch and PR.** Never commit to `main`. Create a branch off `main`
  (`git switch -c <type>/<short-description>`), do the work, open one focused
  PR against `main` with a conventional-commit title and a description of what
  changed and why; prefer a small, correct, well-tested change over a large
  speculative one. (For `run:predict`/`run:evaluate` the *workflow* commits and
  opens the PR — you only write files; the task prompt says which mode you are
  in.)
- **The maintainer merges.** Open the PR, get its required checks green, and
  report it ready — do not merge it yourself or enable auto-merge on it. The
  one built-in exception: the data-run `collect` jobs open their per-run PR
  with auto-merge, still gated on the same required checks.
- **Stay in your lane.** A predictor writes only under its own
  `predictions/<predictor_id>/<run_id>/` path; an evaluator only under its own
  `evaluations/<evaluator_id>/...` path. Never edit another agent's output, the
  docket record, or snapshots.
- **Keep the artifact in view.** Progress is measured by what the pipeline
  produces — predictions, events, provisioned cells, reports — not by merged
  PRs. Know which produced artifact a change serves and say so briefly in the
  PR description; where it directly affects output, show a produced example.
- **The schema is law.** Every artifact must validate. Run
  `uv run fedcourts validate data` before you finish; if it fails, fix it.
- **The snapshot is the baseline; timing is the leakage control.** The
  provisioned snapshot is every predictor's guaranteed-common input, not a
  ceiling; what else a cell may retrieve is keyed on its **mode**
  (`record/context.json`). A `forward` cell (pending case — the outcome does
  not exist yet) may retrieve without restriction; a `replay` cell has the same
  tools but must not seek information about *its case* postdating the event
  date, and discloses any outcome-revealing material it surfaces in
  `flags.json`. Never invent facts. The prompt template carries the full
  contract; all tool calls are logged harness-side.
- **No secrets in code or data.** Never print or log API tokens; they arrive
  as environment variables. In the cell workflows no config file carries one
  either: the MCP client configs name only a localhost sidecar URL, and the
  sidecar's own launch step holds the CourtListener token. (A local stdio
  `mcp-config` run — dev's own token — still injects it into the runner-local,
  gitignored client-config file; that is the one sanctioned file, off-CI
  only.) Never write a token into `data/`, a commit, or an artifact; do not
  copy tokens anywhere else.

## Local gate

The gate that actually blocks a merge is the **required status checks on your
PR** — CI runs the full suite below; locally you have **discretion** to run
the subset that fits what you changed, enough for honest confidence (a
docs-only change needs none of the Python checks).

```bash
uv sync
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest
uv run fedcourts validate data
uv run fedcourts corpus-status
uv run fedcourts export-schemas schemas
git diff --exit-code schemas   # CI fails if the committed schemas drift
```

`pytest` includes an offline stub-cascade smoke (`uv run pytest -k
cascade_smoke`): provision → predict → evaluate → validate over the fixture
corpus with no network, so a broken cell surfaces in seconds. If you touched
`.github/workflows` or `.github/actions`, also run the workflow linters CI
enforces — `uvx zizmor@<pinned> --persona=regular .github/workflows
.github/actions` and `actionlint`; see `.github/workflows/lint-actions.yml` for
the pinned versions, and *Authoring or changing a workflow* in
`docs/pipeline.md` for the cross-cutting traps these checks do **not** catch.

**Before you push, run the relevant reviewer subagent(s)** (`.claude/agents/`)
on the diff and resolve their blockers; each reviews and runs the relevant
checks — it never edits. Pick by what the diff touches (several may apply):
`.github/workflows/**` or `.github/actions/**` → **`workflow-reviewer`**;
`src/**`, `tests/**`, or `config/**` → **`code-reviewer`**; `docs/**`,
`README.md`, `AGENTS.md`, `SECURITY.md`, `metrics/README.md`,
`.github/prompts/**`, or config comments → **`docs-reviewer`**; anything
touching secrets/tokens, authorization, agent capabilities, or network
fetchers → **`security-reviewer`**. A clean linter/gate run is necessary but
not sufficient; if you cannot invoke a subagent, self-review against its
checklist file. Two things hold no matter what you skip locally: **schema is
law** — any change to a pydantic model's fields *or field descriptions* must
regenerate and commit `schemas/` (CI fails on drift) — and **keep the docs in
step**: if your change makes any documentation stale (`README.md`,
`AGENTS.md`, `docs/`, the prompts, docstrings), update it in the same PR.

## Conventions

- Python ≥ 3.12, managed with `uv`. Source under `src/fedcourtsai/`, tests
  under `tests/`. Fully typed (`mypy --strict`); add tests for new behavior.
- IDs and paths come from `fedcourtsai.ids` / `fedcourtsai.paths` — never
  hand-build them (case = `<court_id>/<docket_id>`, events `evt-<kind>-<slug>`,
  run ids UTC timestamps). Writes go through `fedcourtsai.serialize`.
- Conventional-commit style PR titles, e.g. `predict(claude-baseline): ca9/123 — evt-...`.
- **Be cautious about creating new workflow files.** Prefer a job or mode on
  an existing workflow (e.g. `run-analytics` for anything that reads the
  corpus and answers a question); permissions are scoped per *job*, so a task
  earns its own workflow only for a different trigger class or risk class.
  See `docs/pipeline.md`.
- **Docs and code describe the current design, not its history.** No issue
  numbers, no changelog, no "we used to / now we" — on *every committed
  surface*: docs, docstrings, code/workflow/config comments, and prose that
  code renders. State the reason in place; `git blame` finds the history.
- **Close issues from the PR.** Put `Closes #<n>` in the PR description. PR
  descriptions and commit messages are the only places an issue number belongs.
- **`run:*` labels are triggers, not categories.** Applying one immediately
  starts the matching workflow and its agent. Apply one only when you intend to
  start that job *now*; an issue filed for later pickup, or one you plan to fix
  in your own PR, gets no `run:*` label.
- **Keep environment variables out of PR and issue text.** Refer to a var by
  its role, not its name or value. Secrets never appear anywhere.
- **Don't commit personal or organizational email addresses.** Commit identity
  must be a GitHub `noreply` address; point to GitHub-native channels instead
  of contact emails. A task that seems to need one → stop and confirm first.

## Change review

Beyond the gate, changes get a brief adversarial review against three
questions: (1) **Artifact** — which pipeline output does this change serve, and
is the PR's claim about that plausible from the diff? (2) **Weakening** — does
anything weaken a check, gate, validation, prompt contract, or security
posture, even incidentally? (3) **Cheaper path** — is there a simpler route to
the same artifact? The review is advisory, and "no concerns" is a complete and
preferred answer when true. It is most useful from a session or model that did
not author the change; an authoring agent asked to self-review should answer
honestly rather than defensively, and flag where self-review is a poor
substitute.

## Data model (summary)

Raw facts live in the corpus (a payload-free SQLite index in a private S3
remote plus a per-case S3 content store); derived judgments live in git under
`data/cases/<court_id>/<docket_id>/events/<event_id>/`. Full description: the
*Data model* section of `README.md`; pipeline design: `docs/data-pipeline.md`;
task-specific instructions: the prompt file named in your run
(`.github/prompts/`).
