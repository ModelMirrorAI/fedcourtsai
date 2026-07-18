# Retrieval log — scotus/73500215, evt-petition-disposition, claude-baseline, 20260718T000130Z

Mode: `forward` (pending petition; retrieval unrestricted). Nothing
outcome-revealing was sought or surfaced — the petition is undecided
(response requested July 14, 2026, due August 13, 2026).

## Corpus tooling

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   — sampled recent granted petitions for context; too generic to be
   informative (the query surface has no free-text/subject filter for SCOTUS
   rows).
   stderr: `ranged corpus reads: 149 GET(s), 39059456 byte(s)`

## Committed base rates

2. `metrics/statpack.md` and `metrics/statpack.json` — modern
   discretionary-cert disposition split, paid-vs-IFP per-Term grant rates
   (OT2025 paid ≈ 5.4%), CA9 originating-circuit rate, relist-count table.
   The salience-band section named in the prompt is not present in the
   committed statpack, so no band anchor was available.

## CourtListener MCP

3. `search` (type=o, court=scotus, q="Zorn" "qualified immunity",
   filed_after 2025-10-01) — HTTP 429 (rate limit), retried.
4. `search` (type=o, court=scotus, q=Zorn v. Linton) — confirmed *Zorn v.
   Linton*, SCOTUS, filed 2026-03-23, Published.
5. `search` (type=o, court=scotus, q=Zorn v. Linton qualified immunity,
   fields incl. docketNumber/judge) — No. 25-297, "Per Curiam"; confirms the
   petition's characterization of Zorn as a current-Term per curiam
   qualified-immunity decision, and that it postdates the Ninth Circuit panel
   decision (Jan. 15, 2026) and rehearing denial (Feb. 23, 2026) in this case.
6. `get_endpoint_item` (clusters/10813527) — HTTP 429 (rate limit); not
   retried, as the search results above were sufficient. No further detail on
   Zorn (e.g., originating circuit) was pulled.

No web searches were used. All other inputs were the provisioned snapshot,
`questions-presented.txt`, and `petition.txt` (80 pp., includes the Ninth
Circuit memorandum and appendices).
