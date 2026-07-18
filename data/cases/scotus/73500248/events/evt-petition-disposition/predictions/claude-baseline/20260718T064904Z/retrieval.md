# Retrieval log — scotus/73500248 / evt-petition-disposition / claude-baseline / 20260718T064904Z

Mode: `forward` (record/context.json). Provisioned inputs read: the
2026-07-18 snapshot, `documents/questions-presented.txt`, and
`documents/petition.txt` (53 pp., full text including the Second Circuit
summary order, the N.D.N.Y. fee order, and the rehearing denial as
appendices). Base rates from the committed `metrics/statpack.md`.

## Corpus lookups (`fedcourts query`, service backend)

1. `uv run fedcourts query --court scotus --era modern --limit 8 --corpus-backend service`
   — returned no rows (`modern` is not a populated era value).
   stderr: `ranged corpus reads: 432 GET(s), 113246208 byte(s)`
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5 --corpus-backend service`
   — five recent granted petitions, used as a profile contrast (granted cases
   showed 3–22 conference distributions and specialist counsel; this case has
   one distribution and a waived response).
   stderr: `ranged corpus reads: 133 GET(s), 34865152 byte(s)`

## CourtListener MCP lookups

1. `search(type=o, court=scotus, q="1997e(d)(2)" "fee cap" certiorari denied)`
   — 0 results (no SCOTUS opinion engaging the 150% fee-cap question).
2. `search(type=d, court=scotus, q="1997e(d)(2)" attorney's fees)` — 0 results
   (no indexed companion/pending SCOTUS docket raising the same question).

## Web searches

None.
