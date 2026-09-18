# Retrieval record

## Provisioned baseline

Read the event definition, case-level `record/context.json`, `record/snapshots/2026-09-18.json`, and `record/documents/documents.json`. Consulted `questions-presented.txt`, and relevant sections of `petition.txt` and `brief-in-opposition.txt`, including introductions, procedural history, split arguments, and vehicle discussions. The reply is recorded on the snapshot but its contents were not read. No current docket lookup, outcome file, other prediction, or labeling artifact was consulted.

## Committed context and local tooling

- Read the prediction prompt, repository instructions, and prediction, flags, and tooling schemas.
- Consulted `metrics/statpack.md`: modern discretionary-cert dispositions, paid-segment relist and CVSG cuts, and the `sal-v4` per-Term segment table. Inspected corresponding aggregate entries in `metrics/statpack.json` and pooled only the 2017–2024 elevated reached-risk sets: 484 / 2,810. No live corpus lookup was used.
- Ran `uv run fedcourts paths --court scotus --docket 73281619 --event evt-petition-disposition --role predictor`. The first attempt failed because the default uv cache was read-only; rerunning with a writable temporary cache succeeded. This was path resolution, not retrieval of corpus rows.
- No `fedcourts query` or `open-events` call was made. Consequently there was no ranged-corpus transfer line to report.

## External retrieval

1. Web search queries `site.justice.gov RLUIPA substantial burden equal terms land use` and `site.supremecourt.gov opinions 2015 Holt Hobbs RLUIPA`. The tool returned no visible content or source identifiers. No evidence was used.
2. Web search query `site.justice.gov "RLUIPA" "Equal Terms"`. Again no visible content or source identifiers; no evidence was used.
3. Attempted web open of the general Justice Department document at `https://www.justice.gov/crt/page/file/1071246/dl`. No visible content was returned; no proposition was attributed to that document.
4. CourtListener MCP `search`, type `o`, citation `858 F.3d 996`, one result, requesting case name, date, opinion metadata, citation, and path. Returned Livingston Christian Schools v. Genoa Charter Township, decided June 2, 2017; cluster 4396792, opinion 4174045.
5. CourtListener MCP `search_document`, opinion 4174045, literal query `Holt`, snippet size 2200. Consulted the returned discussion of the substantial-burden standard and Holt in Livingston, approximately 858 F.3d at 1002. This was an older doctrinal precedent, not this petition's outcome or subsequent history. No full prior opinion or citing-case search was requested.

No external result revealed this petition's disposition. The failed general web requests did not affect the forecast; the provisioned briefs, frozen context, committed aggregate tables, and limited precedent excerpt supplied the evidence used.
