# Retrieval log

## Provisioned inputs
- `record/snapshots/2026-10-05.json`, `record/context.json`, `events/evt-petition-disposition/event.yaml`. No `record/documents/` directory was provisioned.
- `metrics/statpack.md`: modern discretionary-cert by disposition, by originating circuit, relist-count cut, CVSG cut, salience-band cut, per-Term table, and the "Segment base rate by salience band (sal-v4)" table (baseline bracketed `reached` pooled over OT2017–OT2025 ≈ 5.0%).

## Corpus lookups (`fedcourts`)
- `uv run fedcourts paths --court scotus --docket 9026000043 --event evt-petition-disposition --role predictor`
- `uv run fedcourts query --court scotus --era 2020s --disposition granted`
  - stderr: `ranged corpus reads: 48 GET(s), 12451840 byte(s)`
  - Returned 11 recently granted OT2025/OT2026 rows, including No. 26-104 *Rhoney v. Barbosa da Cunha* (CA2 25-3141, docketed 2026-07-23, distributed for 2026-09-28, `date_cert_granted` 2026-10-01). That companion grant is the decisive signal; see `reasoning.md` and `flags.json`.

## CourtListener MCP lookups
1. `search` (opinions, court ca5, q "Buenrostro-Mendez"): 3 hits, all citing opinions (*K Alain v. CIR*, *Sosnava Rodriguez v. Ortega*, an unrelated 1990 case); the February 6, 2026 *Buenrostro-Mendez v. Bondi* opinion itself was not found.
2. `search` (opinions, all circuits, filed after 2025-06-01, q on 1225(b)(2)(A) / applicant for admission / 1226(a)): 0 hits.
3. `search` (opinions, ca5, docket_number 25-20496): 0 hits.
4. `search` (opinions, all circuits, filed after 2025-09-01, q "applicants for admission" "1225(b)(2)" mandatory detention habeas): 0 hits.
5. `search` (opinions, filed after 2025-06-01, q "Buenrostro"): 34 hits, used to map the circuit decisions citing the Fifth Circuit case (CA2, CA7 ×2, CA9, CA1, CA3, CA4, CA6, CA8, CA10, CA11, CA5).
6. `search` (dockets, CA5 and Fifth Circuit district courts, q "Buenrostro-Mendez"): 0 hits.
7. `search` (opinions, all circuits, filed after 2025-09-01, q "Yajure Hurtado"): 0 hits.
8. `search` (opinions, case_name "Buenrostro", filed after 2025-06-01): 0 hits.
9. `search` (opinions, ca2, q "Barbosa Da Cunha"): 2 hits; identified the September 25, 2026 en banc order (cluster 10983473, opinion 11451136).
10. `read_document` (opinion 11451136, Second Circuit en banc order): no text available.
11. `read_document` (opinion 11356093, *Sosnava Rodriguez v. Ortega*, CA5): no text available.
12. `get_endpoint_item` (opinions, 11451136, fields id/type/plain_text/download_url): returned the en banc order's plain text (about 135k characters). Read the order, the Bianco/Nathan concurrence opening, and Judge Menashi's dissent passages describing the circuit split (Fifth and Eighth Circuits for the government; Second, Seventh, Sixth, Eleventh, Tenth, Ninth, First and Third against) and noting *Genalo v. Black*'s grant and dismissal.
13. `search` (opinions, nine circuits, filed after 2026-03-01, q "Buenrostro-Mendez" "1225(b)(2)(A)"): 1 hit (*Avila v. Bondi*, CA8); not read.

No web searches. I did not retrieve this docket's own current state or any order list after the snapshot.
