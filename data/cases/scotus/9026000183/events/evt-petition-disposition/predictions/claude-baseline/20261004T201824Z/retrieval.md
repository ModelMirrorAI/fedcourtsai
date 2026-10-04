# Retrieval log

## Corpus (`fedcourts`)

- `uv run fedcourts paths --court scotus --docket 9026000183 --event evt-petition-disposition --role predictor`
  — path resolution only; no transfer line.
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  — recent granted 2020s SCOTUS rows for shape/context (several were petitions
  distributed for the 2026-09-28 conference with grants dated 2026-10-01, and
  substantive applications). Used only as context on long-conference grant
  timing; none is a doctrinal comparator. stderr:
  `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
- Base rates: committed `metrics/statpack.md` — modern discretionary-cert
  disposition table, originating-circuit cut (ca5), relist-count and CVSG cuts
  (paid scored segment), and the per-Term "Segment base rate by salience band
  (sal-v4)" table (baseline column, bracketed `reached` figures, Terms 2017–2025).

## CourtListener MCP

1. `search` type=d, court=scotus, case_name="Detwiler Mid-Columbia" — 0 results.
2. `search` type=d, court=scotus, docket_number="26-183" — 0 results (SCOTUS
   2026 dockets do not appear to be indexed).
3. `search` type=d, court=scotus, q="Detwiler" — 0 results.
4. `search` type=d, q='"United Airlines" Kincannon' — 17 results, all lower-court
   dockets (N.D. Tex. 4:21-cv-01074; CA5 21-11159, 24-90016, 24-10656, 24-10708;
   unrelated matters). No SCOTUS docket returned; nothing read further.
5. `search` type=o, q='Detwiler "Mid-Columbia"' — Ninth Circuit opinions
   (2025-09-23 panel; 2026-04-15 en banc denial) and related cases; confirmed the
   citations in the petition, did not open the opinions.
6. `call_endpoint` dockets, court=scotus, case_name__icontains=Detwiler — rejected
   by the tool's parameter validation; not retried.

No web searches. I did not look up this docket's own post-conference state or
disposition anywhere.
