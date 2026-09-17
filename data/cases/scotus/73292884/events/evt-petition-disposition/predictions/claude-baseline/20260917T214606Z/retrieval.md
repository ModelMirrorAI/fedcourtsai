# Retrieval log

## Corpus lookups (`fedcourts query`, via the cell's corpus service)

- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 8`
  — `ranged corpus reads: 28 GET(s), 7340032 byte(s)`. Returned recent granted
  rows (mostly interim applications and unrelated cert grants); no
  campaign-finance disclosure prior surfaced. Not used beyond confirming the
  service.
- `uv run fedcourts query --court scotus --era 2020s --limit 8`
  — `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache). Recency-ranked
  generic rows, not case-relevant. Not used.

## CourtListener MCP lookups

1. `search` (opinions, court ca10, "Rio Grande Foundation" Oliver disclosure,
   filed after 2025-01-01) → one hit: *Rio Grande Foundation v. Oliver*,
   No. 24-2070, filed 2025-09-09, Published, cluster 10668506, opinion 11135093.
2. `read_document` (opinion 11135093, chunk 0 of 21) → confirmed panel
   (Hartz, Eid, Federico; Federico writing), published, and the framing of the
   holding. Did not read further; the petition and BIO already quote the
   opinion at length.
3. `search` (dockets, court scotus, "Wyoming Gun Owners") → 0 results.
4. `search` (dockets, court scotus, "No on E" Chiu) → 0 results.
5. `search` (dockets, court scotus, "Gaspee Project") → 0 results.
   (3–5 were attempts to confirm the disposition of comparable post-AFPF
   disclosure petitions; CourtListener's SCOTUS docket coverage returned
   nothing, so those comparisons in `reasoning.md` rest on memory.)
6. `search` (opinions, court scotus, NRSC v. FEC coordinated, filed after
   2026-01-01) → one hit: No. 24-621, filed 2026-06-30, opinion 11349765.
7. `read_document` (opinion 11349765, chunks 0–1) → "No text is available for
   this document." The BIO's characterization of NRSC is therefore the only
   account of it I used.

No web searches. No lookup touched this case's own disposition; the petition
is set for the September 28, 2026 conference, which post-dates this run.
