# Retrieval record

## Local context beyond the provisioned case inputs

- Read `metrics/statpack.md`: modern discretionary-cert dispositions; originating-circuit cut; paid-segment relist and CVSG cuts; sal-v4 reached-band table.
- Read selected fields of `metrics/statpack.json` to compute the elevated-band anchor across displayed Terms 2017–2024: 484 / 2,810 = 0.17224199288256228. Used `prefix_est_grant_rate` and `prefix_weighted_resolved`; excluded Terms 2025 and 2026.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md` to identify artifact vintage: `55121cdb8 2026-09-14T11:02:00Z`. This does not establish remote-corpus freshness.
- Read the prompt, repository instructions, and output schemas; ran `fedcourts paths` to resolve the cell paths. No corpus `query` or `open-events` calls were made, so no ranged-corpus-transfer line exists.

## Web attempts

- Submitted general precedent searches: `site.supremecourt.gov opinions Barnes Felix 2025 23-1239 officer creation dangerous situation` and `site.supremecourt.gov opinions City Tahlequah Bond 2021 20-1668`. The tool returned no visible results or usable source text.
- Attempted to open the Supreme Court opinion PDF path `/opinions/24pdf/23-1239_onjq.pdf` on the Court's official site. The tool again returned no visible content. No factual inference rests on this attempted open.

## CourtListener MCP

1. `search(type="o", citation="595 U.S. 9", num_results=2)`: returned City of Tahlequah v. Bond, decided October 18, 2021, with duplicate report records.
2. `read_document(opinion_id=5120580)`: read the Bond opinion to verify the specific-precedent reasoning, the factual distinction, the timing treatment of Ceballos, and the summary-reversal route.
3. `search(type="o", case_name="Barnes v. Felix", court="scotus", filed_after="2025-05-14", filed_before="2025-05-16", num_results=1)`: returned the May 15, 2025 Supreme Court decision, 605 U.S. 73, opinion 11243439.
4. `search_document(opinion_id=11243439, query="creation", snippet_size=900)`: read the report's syllabus passage confirming the totality-of-circumstances approach and reservation of officer-created danger. This was a targeted excerpt, not a full reading of the Barnes opinion.

No live lookup targeted the petition being predicted, its disposition, subsequent history, or decision coverage. No outcome-revealing material concerning this event was encountered.
