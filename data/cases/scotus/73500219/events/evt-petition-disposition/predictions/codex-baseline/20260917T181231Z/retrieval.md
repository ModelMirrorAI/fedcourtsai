# Retrieval log

## Local context beyond the provisioned case record

- Read `metrics/statpack.md`: modern discretionary-cert dispositions; originating-circuit cut; paid-segment relist and CVSG cuts; per-Term cert and `sal-v4` segment tables.
- Read aggregate structure and baseline segment rows in `metrics/statpack.json`. Pooled OT2017–OT2024 `baseline` risk sets as the sum of `prefix_weighted_resolved * prefix_est_grant_rate` divided by the sum of `prefix_weighted_resolved`: 593 / 11,580 = 0.051208981. No case-level corpus rows were retrieved.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md metrics/statpack.json` for artifact vintage: `55121cdb8 2026-09-14T11:02:00Z`. This does not establish blob-level freshness.
- Read task/schema contracts and the path/serialization helpers for output construction. Ran `uv run fedcourts paths --court scotus --docket 73500219 --event evt-petition-disposition --role predictor`. The initial invocation failed because the default uv cache was read-only; rerunning with a writable temporary cache succeeded.
- No `fedcourts query` or `open-events` call; no ranged-corpus transfer line was produced. No outcome file or labeling artifact was read.

## Web searches

Two `web.run` calls, each containing two queries, returned no usable result content:

1. `site.law.cornell.edu/supct/html/91-1306 United States Olano intrusion jury deliberations verdict`
2. `site.supremecourt.gov Rule 10 certiorari judicial discretion accepted usual course`
3. `United States Olano 507 U.S. 725 739 jury intrusion`
4. `Supreme Court Rule 10 considerations governing review certiorari`

No web result informed the forecast and no query named the target case.

## CourtListener MCP

1. `search(type="o", citation="192 F.3d 893", num_results=1)` returned United States v. Michael Vernon Dutkel, Ninth Circuit, September 17, 1999; cluster 766293; lead opinion 9492531. Purpose: verify the petition's principal contrasting authority without searching the target case.
2. `search_document(opinion_id=9492531, query="different", snippet_size=1100)` returned four excerpts. Relevant passages distinguish tampering from other misconduct and explain the deliberation-focused prejudice inquiry at 192 F.3d 899. Only this historical precedent was retrieved; its discussion informed both the split signal and the factual-distinction discount.

The provisioned target-case petition and appended pre-cert lower-court analysis were the sole sources for this case's substance. The Supreme Court disposition was neither requested nor encountered.
