# Retrieval log

## Provisioned material

- Read the event definition; `record/context.json`; `record/snapshots/2026-09-09.json`; `record/documents/documents.json`; `questions-presented.txt`; and relevant petition sections, including the statement, split discussion, conclusion, and reproduced appellate opinion at Pet. App. 20a–28a. Petition metadata marks truncation.

## Additional local context

- Read `metrics/statpack.md`: modern discretionary-cert dispositions, originating-circuit context, paid-segment relist and CVSG cuts, and the sal-v4 per-Term reached-band table.
- Read `metrics/statpack.json` and used jq to pool baseline-band `prefix_est_grant_rate * prefix_weighted_resolved` over Terms 2017–2025, divided by summed `prefix_weighted_resolved`: 638 / 12,720 = 0.05015723270440252. Excluded Term 2026.
- `git log -1 --format='%cI %h' -- metrics/statpack.json` reported September 26, 2026, 12:03:37 UTC, commit 96ebdd342. This dates the artifact commit, not the underlying corpus refresh.
- `uv run fedcourts paths --court scotus --docket 9026000302 --event evt-petition-arrival-disposition --role predictor` initially failed because the default uv cache was read-only. Repeating with the cache redirected to `/tmp/uv-cache` succeeded. No corpus query or open-events lookup was made; there is no ranged-corpus-transfer line.

## Web attempts

1. `web.run` search: `site.supremecourt.gov Rule 10 considerations governing review certiorari conflict courts appeals`. No usable result returned.
2. `web.run` open of the Supreme Court's official filing-and-rules guidance page. No usable content returned.
3. Repeated that open once. No usable content returned. No web-derived substantive facts entered the forecast.

## CourtListener MCP

1. `search(type="o", case_name="Johnson v. NPAS Solutions", filed_before="2026-09-09", num_results=3, q='"incentive"')`: one result, Charles T. Johnson v. NPAS Solutions, LLC, 975 F.3d 1244, Eleventh Circuit, filed September 17, 2020; cluster 4786005, opinion 4566352. This is a prior on the legal question, not this petition's disposition.
2. `search_document(opinion_id=4566352, query="Supreme Court precedent prohibits", snippet_size=1000)`: two excerpts confirming the majority's application of Greenough and Pettus to the incentive award, including PDF pp. 18 and 26.

No current docket lookup for this petition, companion-status search, outcome file, other predictor output, or QP-topic measurement artifact was consulted.
