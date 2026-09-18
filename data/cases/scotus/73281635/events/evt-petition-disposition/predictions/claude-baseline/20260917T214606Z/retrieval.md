# Retrieval log

## Corpus tooling

- `uv run fedcourts query --court scotus --disposition granted --text "prejudgment interest" --limit 8` — rejected: the command takes no free-text argument (structured filters only). No corpus read.
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 6` — `ranged corpus reads: 23 GET(s), 6029312 byte(s)`. Returned six recent granted SCOTUS rows (mostly substantive applications and Term-2025 petitions); general context only, no topical prior on prejudgment interest.
- `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 4` — `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm service cache). Returned four recent denied rows; general context only.
- `metrics/statpack.md` (committed): "Modern discretionary-cert petitions by disposition", "Cert petitions by relist count (paid scored segment)", "Cert petitions by CVSG status (paid scored segment)", "Cert petitions by salience band", "SCOTUS cert petitions by Term", and "Segment base rate by salience band (sal-v4)".

## CourtListener MCP

- `search` (type opinion, court ca7, q "Bolden Pesavento prejudgment interest", filed after 2025-10-01) — found the Seventh Circuit opinion, cluster 10732093, opinion 11198678, No. 24-1674, decided 2025-11-06, Kolar, J.
- `search` (type opinion, court scotus, q `"prejudgment interest" "noneconomic" certiorari`, filed after 2015-01-01) — 0 results.
- `read_document` (opinion 11198678, chunks 0–4 of 6) — read the Seventh Circuit opinion's discussion of Hillier, the circuit-split footnote, and the apportionment remand.
- `search` (type docket, court scotus, docket_number 25-1146) — 0 results; nothing about this petition's disposition surfaced.

## Web

None.
