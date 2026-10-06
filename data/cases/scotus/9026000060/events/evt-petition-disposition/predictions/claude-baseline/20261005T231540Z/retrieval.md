# Retrieval log

Base rates: `metrics/statpack.md` (committed), sections "Modern cert petitions by originating circuit", "Cert petitions by relist count (paid scored segment)", "Cert petitions by CVSG status (paid scored segment)", "SCOTUS cert petitions by Term", and "Segment base rate by salience band (sal-v4)". Pooled the `baseline` band's bracketed `reached` rate over OT2017 through OT2025: 637.4 / 12720 = 5.0%.

## Corpus lookups (`fedcourts query`)

1. `uv run fedcourts query --court scotus --citation "605 U.S. 280"` (looking for Smith & Wesson v. Mexico as a comparable prior)
   - stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned no rows; the tool's note said only 200 scotus rows carry any reporter citation, so the empty result reflects column coverage, not absence of the case.
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 8`
   - stderr: `ranged corpus reads: 25 GET(s), 6422528 byte(s)`
   - Returned 8 recently granted scotus rows (mostly federal-party petitions and substantive applications from OT2025/OT2026). Used only for shape; none was a comparable private-party standing petition.

## CourtListener MCP lookups

3. `search` (type opinion, court ca4, q "Lowy Daniel Defense") — found the Fourth Circuit opinion, cluster 10792807, opinion id 11259448, docket 24-1822, filed 2026-02-11, published.
4. `read_document` (opinion_id 11259448, chunk 0 of 39) — confirmed panel King, Wynn, Quattlebaum; opinion by King joined by Wynn, Quattlebaum dissenting; "reversed in part, vacated in part, and remanded"; argued October 21, 2025; amici below on both sides.

## Web searches

5. `Supreme Court certiorari granted 2026 Article III traceability "determinative or coercive effect" third party` — surfaced this petition itself and older related petitions (Turaani v. Wray, No. 21-72); no pending or granted companion case on the standard surfaced.
6. `"Daniel Defense" Lowy certiorari petition 26-60 Supreme Court response requested` — gun-press coverage (NRA-ILA, Ammoland, SAF release) confirming the waiver, the August 26 call for response, and the October 26 BIO date. No disposition surfaced.

Total: 6 retrieval calls. Nothing under `data/qp-topics/` was read.
