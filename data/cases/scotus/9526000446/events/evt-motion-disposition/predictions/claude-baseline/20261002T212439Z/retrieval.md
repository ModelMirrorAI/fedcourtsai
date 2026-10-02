# Retrieval log

Provisioned inputs read: `record/context.json`, `record/snapshots/2026-09-30.json`,
`record/documents/documents.json`, `record/documents/application.txt` (full text),
`events/evt-motion-disposition/event.yaml`; stable inputs `AGENTS.md`,
`.github/prompts/predict.md`, `schemas/prediction.schema.json`,
`schemas/agent_tooling.schema.json`, `metrics/statpack.md` (interim-docket section).

## Corpus tooling

- `uv run fedcourts paths --court scotus --docket 9526000446 --event evt-motion-disposition --role predictor`
- `uv run fedcourts query --court scotus --include-applications --disposition granted --limit 15`
  — `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
- `uv run fedcourts query --court scotus --include-applications --limit 400`
  — `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
- `uv run fedcourts query --court scotus --include-applications --limit 1500`
  — refused by the corpus service (limit must be ≤ 500); no transfer line.
- `uv run fedcourts query --court scotus --include-applications --limit 500`
  — `ranged corpus reads: 16 GET(s), 4194304 byte(s)`; 86 substantive resolved rows
  tallied locally by `response_requested`, `referred_to_court`, `amicus_briefs`, and
  applicant/respondent class.

## CourtListener MCP

- `search` (type `d`, court `scotus`, q "Wagner v. United States", filed after
  2026-09-01) — 0 results.

## Web (forward mode, unrestricted)

- WebSearch: "Kyle Wagner stay application Supreme Court Kavanaugh Sixth Circuit
  pretrial detention 26A446".
- WebSearch: "Supreme Court application stay pretrial detention order criminal
  defendant Bail Reform Act denied Justice release pending certiorari" — background
  only, nothing case-specific.
- WebFetch supremecourt.gov docket 26A446 (twice, second with a cache-busting query
  string) — single entry, Sep 29 2026 submission; no Oct 2 entry shown.
- WebFetch supremecourt.gov docket 26-391 (twice) — entries through Oct 02 2026:
  response to application 26A446 requested by Justice Kavanaugh, due Oct 8; waiver of
  the United States' right to respond to the petition; motion to expedite filed Sep 29.
- WebFetch Washington Times article of 2026-10-02 — HTTP 403, not read.
- WebFetch Reason/Volokh post of 2026-08-14 on the Sixth Circuit decision — panel,
  majority's description of conduct, dissent.
- WebFetch emptywheel post of 2026-09-25 — petition's question presented and trial
  schedule.

No disposition of this application surfaced in any of the above.
