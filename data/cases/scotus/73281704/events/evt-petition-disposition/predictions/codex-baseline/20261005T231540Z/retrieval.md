# Retrieval record

## Provisioned inputs

Read the event definition and case-level `record/context.json`, `record/snapshots/2026-10-05.json`, and `record/documents/{documents.json,questions-presented.txt,petition.txt,brief-in-opposition.txt}`. Read the task instructions and output schemas. Did not read another prediction, an outcome artifact, or any QP-topic labeling artifact.

## Local context beyond the provisioned inputs

- Read `metrics/statpack.md`: modern-cert dispositions, originating circuits, paid-segment relist/CVSG cuts, and the sal-v4 per-Term band table. A heading/Term-row search also displayed interim and merits table rows; these were not used for this cert prediction.
- Read `metrics/statpack.json` metadata/structure and the sal-v4 elevated risk-set fields for Terms 2017-2024. Used jq to pool 484 grants over 2,810 weighted resolved petitions. No current-Term rate entered the anchor.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md` to identify the committed pack revision: `808f812e9`, September 28, 2026, 12:02:50 UTC. This is commit vintage, not a substitute for corpus-wide freshness.
- Ran `uv run fedcourts paths --court scotus --docket 73281704 --event evt-petition-disposition --role predictor`. The first attempt failed because the default uv cache was read-only; the same command succeeded with the cache redirected to `/tmp/fedcourts-uv-cache`.
- No `fedcourts query` or `open-events` calls; no ranged-corpus transfer lines were produced.

## Web attempts

- One `web.run` search call with queries `"Slack v. McDaniel" "529" "484" opinion 2000` and `"United States v. Rutigliano" "887" "custody" 2018`. The tool returned no visible results or source content.
- One `web.run` open attempt for `https://supreme.justia.com/cases/federal/us/529/473/`. The tool returned no visible content. Nothing from these attempts informed the forecast.

## CourtListener MCP

1. `search(type="o", citation="887 F.3d 98", num_results=1)`: returned *United States v. Rutigliano*, April 4, 2018, cluster 8439875, opinion 8410694. Historical precedent, not the target case.
2. `search_document(opinion_id=8410694, query="custodial", snippet_size=550)`: consulted the historical opinion's discussion and conclusion concerning section 2255, restitution, and custody. The displayed conclusion distinguishes payment terms from the monetary amount alone and rejects relief on that record. Some intermediate excerpts were truncated in tool display; I relied on the visible passages, not presumed omitted text.

No target-case live docket lookup, subsequent-history search, or outcome search was made. Berry's relevance comes only from the provisioned petition and opposition; no current Berry docket was retrieved.
