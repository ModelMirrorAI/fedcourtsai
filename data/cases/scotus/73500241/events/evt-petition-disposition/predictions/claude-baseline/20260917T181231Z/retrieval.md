# Retrieval log — scotus/73500241, evt-petition-disposition, claude-baseline, run 20260917T181231Z

Mode: `forward` (context.json). No `DECIDED_BEFORE` clock. Nothing about this case's own disposition was sought or seen; the docket snapshot is dated today (2026-09-17) and shows the petition still awaiting its 2026-09-28 conference.

## Provisioned inputs read

- `record/context.json`, `record/snapshots/2026-09-17.json`
- `record/documents/documents.json`, `petition.txt` (22 pp., text extracted), `questions-presented.txt`
- `events/evt-petition-disposition/event.yaml`
- `metrics/statpack.md` (committed base rates)

## Corpus lookups

```
uv run fedcourts paths --court scotus --docket 73500241 --event evt-petition-disposition --role predictor
uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8
ranged corpus reads: 28 GET(s), 7340032 byte(s)
```

The query returned eight recent granted rows (four substantive applications, four cert petitions on unrelated questions: elections, firearms, a Free Exercise matter). None concerned retention of seized property or a tax-as-taking claim; the rows informed nothing beyond confirming the query surface has no topic filter for SCOTUS rows.

## CourtListener MCP lookups (8 calls, all empty)

1. `search` type=o, court=kanctapp, q="Greene 'Department of Revenue' Fifth Amendment taking Diablo", filed_after 2025-09-01 — 0 results.
2. `search` type=o, case_name="Greene v. Kansas Department of Revenue", filed_after 2025-01-01 — 0 results.
3. `search` type=d, court=scotus, case_name="Asinor" — 0 results (no SCOTUS docket for the D.C. Circuit lead case).
4. `search` type=d, court=scotus, case_name="Malanga" — 0 results (no SCOTUS docket for the Third Circuit lead case).
5. `search` type=o, citation="576 P.3d 320" — 0 results (opinion below not in CourtListener).
6. `search` type=r, court=scotus, q="Asinor 'District of Columbia'" — 0 results.

(Calls 1, 2 and 5 were three attempts at the same opinion below; 3, 4 and 6 three attempts at the split's lead cases.)

## Web searches

None.
