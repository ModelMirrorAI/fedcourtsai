# Contributing

Thanks for your interest in FedCourtsAI. This is an experimental research project
with an unusual shape: most feature work is done by AI coding agents driven by a
**label-driven pipeline of GitHub Actions**, and the data is produced by the
pipeline rather than by hand.

The canonical, complete instructions — the branch-and-PR workflow, the local
gate, the golden rules, and every convention — live in **[AGENTS.md](AGENTS.md)**,
the single source of truth for both human and AI contributors. Read it before
opening a PR; this page only covers what is specific to outside contributors.

## The model in one minute

- Work is represented as **GitHub issues**. Applying a `run:*` label triggers
  the matching workflow (see the table in the [README](README.md) and
  [`docs/pipeline.md`](docs/pipeline.md)). Applying those labels is
  **maintainer-gated** and is the pipeline's trust boundary (see
  [SECURITY.md](SECURITY.md)).
- **Never commit to `main`.** Every change lands through a focused pull request
  that must pass the `gate` check before merge — see the branch-and-PR flow and
  local gate in [AGENTS.md](AGENTS.md).
- **Stay in your lane.** Pipeline-code changes don't touch `data/`;
  data-production runs don't change pipeline code to make a task easier.

## Opening an issue

- **Found a bug or have an idea?** Use the *Bug report* or *Feature / idea* form on
  the [new-issue page](../../issues/new/choose).
- **Want a data run** (e.g. refresh a case)? Open a regular issue describing it.
  Triggering the run is maintainer-only — a maintainer applies the `run:*`
  label, the trust boundary for anything that spends compute or writes the
  corpus.

## Ground rules

- Be respectful — see the [Code of Conduct](CODE_OF_CONDUCT.md).
- Don't weaken validation, CI, lint, type, or security checks to make a change pass.
- **No secrets in code, data, or logs.** Tokens arrive only as environment
  variables and never get printed, logged, or committed.
- These are experimental predictions, **not legal advice**. Do not feed privileged
  or sealed material into the pipeline.

Questions that aren't a bug or feature? Open a blank issue or start a discussion.
