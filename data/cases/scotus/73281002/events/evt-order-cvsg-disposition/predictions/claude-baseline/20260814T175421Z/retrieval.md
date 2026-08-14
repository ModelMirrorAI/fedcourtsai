# Retrieval log — claude-baseline / 20260814T175421Z

Beyond the provisioned inputs (snapshot 2026-08-14, `event.yaml`,
`record/context.json`, `record/documents/` — questions-presented, petition,
brief-in-opposition — and the committed `metrics/statpack.md`):

## Corpus lookups

- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
  — stderr: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`. Pulled recent
  granted-petition priors for shape; returned mostly application-track rows
  plus one salience-selected cert grant (Jouppi v. Alaska, 3 distributions),
  consistent with the statpack's relist-signal shape. Not load-bearing.

## Web searches (forward mode — unrestricted)

- `Baxter v. Philadelphia Board of Elections Pennsylvania Supreme Court decision mail ballot date requirement`
  — confirmed the case's posture: allocatur granted January 2025, argued
  September 2025 (ACLU-PA, Democracy Docket, Votebeat, State Court Report
  coverage).
- `Pennsylvania Supreme Court Baxter undated mail ballots ruling 2026`
  — no decision surfaced; the case appears still pending as of today. Used to
  weigh the BIO's mootness/vehicle argument. Incidentally surfaced coverage of
  the Third Circuit's own ruling below (pre-snapshot material, not leakage;
  this petition's disposition does not yet exist).

## CourtListener MCP

None.
