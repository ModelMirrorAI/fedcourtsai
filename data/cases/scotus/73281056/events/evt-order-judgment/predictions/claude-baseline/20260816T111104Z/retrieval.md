# Retrieval log

Beyond the provisioned inputs (snapshot `2026-08-16.json`, `event.yaml`,
`record/context.json`, and the provisioned document texts: `petition.txt`,
`brief-in-opposition.txt`, `questions-presented.txt`, `documents.json`) and
the committed `metrics/statpack.md`:

## Corpus lookups

- `uv run fedcourts query --court scotus --citation "570 U.S. 1" --limit 5`
  (looking for the Arizona v. Inter Tribal Council prior) — returned no rows.
  Stderr transfer line:
  `ranged corpus reads: 1329 GET(s), 348389376 byte(s)`
  followed by the coverage note that only 161 of 590,339 in-scope SCOTUS rows
  carry citation data. Per the sparse-filter guidance I did not retry.

## CourtListener MCP

None. This is a forward merits cell at the grant moment: the merits briefs do
not exist yet (petitioner's brief due 2026-08-28, after the snapshot date),
and the cert-stage filings were already provisioned as text, so there was
nothing case-specific worth a live fetch.

## Web searches

None.
