# Retrieval log

- Read committed metrics/statpack.md: modern discretionary-cert dispositions; circuit coverage; paid-segment relist and CVSG cuts; and the sal-v4 segment table. Read metrics/statpack.json for exact elevated reached denominators and rates over displayed Terms 2017–2024. Used jq to compute 484 / 2810 = 0.17224199288256228. Inspected its latest commit metadata with `git log -1 --format='%h %cI' -- metrics/statpack.json`: 55121cdb8, September 14, 2026. No individual corpus case was queried.
- Web search: `site.supremecourt.gov opinions 2025 Case Montana 24-624 January 14 2026`. No usable content returned; the query's date was a search hypothesis, not a verified fact.
- Web search in the same call: `site.supremecourt.gov opinions Florida Thomas 532 774 final judgment suppression`. No usable content returned.
- Attempted web open of an unverified candidate official opinion location: `https://www.supremecourt.gov/opinions/25pdf/24-624_b07d.pdf`. No usable content returned; no contents or URL validity inferred.
- CourtListener MCP search: type `o`, case_name `Case v. Montana`, court `scotus`, filed_before `2026-02-24`, num_results `3`. Returned HTTP 429, with an 88-second suggested wait. No case text was returned. Did not retry or use a REST fallback.
- No `fedcourts query` or `open-events` lookup; no ranged-corpus transfer line was emitted. No external case-specific research on Cummins, subsequent history, or disposition.

Administrative reads included the task instructions, output schemas, and the case's provisioned record. `fedcourts paths --court scotus --docket 73281318 --event evt-petition-disposition --role predictor` resolved the supplied cell paths. Its initial uv launch failed because the default cache location was read-only; rerunning with a writable temporary cache and `--no-sync` succeeded. These commands did not retrieve legal facts.
