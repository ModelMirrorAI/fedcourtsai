<!--
Conventional-commit-style title, e.g. `fix(pull): handle empty docket page`.
See AGENTS.md for the full workflow and CONTRIBUTING.md for the short version.
-->

## What & why

<!-- A sentence or two: what changes, and the problem it solves. -->

## Linked issue

<!-- `Closes #<n>` if this completes an issue; otherwise remove this section. -->

## Checklist

- [ ] Branched off `main`; this PR is focused on one thing.
- [ ] Ran the relevant parts of the local gate (`ruff`, `mypy`, `pytest`,
      `fedcourts validate data`) — enough for honest confidence in what changed.
- [ ] Regenerated `schemas/` if a pydantic model changed (`fedcourts export-schemas schemas`).
- [ ] Updated any docs the change makes stale (`README`, `AGENTS.md`, `docs/`, prompts, docstrings).
- [ ] No secrets, tokens, or credentials in code, data, or logs.
