# Retrieval log — scotus/73281703 / evt-petition-disposition / claude-baseline / 20260717T072907Z

Mode: `forward` (retrieval unrestricted; nothing outcome-revealing surfaced —
the petition is pending with the response due Aug. 12, 2026).

## Corpus lookups (`fedcourts`)

1. `uv run fedcourts query --court scotus --citation "29 U.S.C. § 794" --limit 8`
   — returned 0 rows.
   stderr: `ranged corpus reads: 420 GET(s), 110100480 byte(s)`
2. `uv run fedcourts query --court scotus --citation "465 U.S. 624" --citation "536 U.S. 181" --limit 8`
   — returned 0 rows.
   stderr: `ranged corpus reads: 420 GET(s), 110100480 byte(s)`

Neither query surfaced matching priors, so corpus priors did not inform the
estimate; base rates came from the committed `metrics/statpack.md` /
`metrics/statpack.json` (modern discretionary-cert disposition table, relist
and CVSG cuts, per-Term paid/IFP fee-class grant rates).

## CourtListener MCP lookups

1. `search` (type `o`): `"Rehabilitation Act" "independent contractor"
   "section 504"`, filed after 2024-01-01, newest first — 3 results: the
   decision below (*Benton School District v. Greer*, 2026 Ark. 53, Mar. 12,
   2026) and a Texas intermediate-court case (*Ford v. University of Texas at
   Austin*, 2025). Confirmed no companion SCOTUS-bound litigation or
   intervening decision on the question presented; nothing about this
   petition's disposition (none exists).

## Web searches

None.
