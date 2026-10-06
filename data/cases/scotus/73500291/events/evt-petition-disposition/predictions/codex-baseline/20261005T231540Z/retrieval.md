# Retrieval record

## Provisioned inputs

Read the event definition and case-level `record/context.json`, `record/snapshots/2026-10-05.json`, and `record/documents/{documents.json,questions-presented.txt,petition.txt,brief-in-opposition.txt}`. Petition and BIO reading concentrated on the question, reasons for review or denial, procedural history, split, and vehicle sections. No reply text was provisioned.

## Committed context and local tools

- Read the task contract, AGENTS instructions, prediction/flags/tooling schemas, and path/serialization helper definitions to produce contract-compliant files.
- Read `metrics/statpack.md`: modern discretionary-cert disposition section, originating-circuit material, paid-segment relist and CVSG cuts, and sal-v4 per-Term reached-band table. Used only Terms 2017–2024 for the elevated grant-rate anchor.
- Read `metrics/statpack.json` structure and relevant Term segment fields; computed the exact prior-Term reached-band pool locally: 484 / 2810 = 0.17224199288256228. No individual corpus case rows were retrieved.
- Ran `uv run fedcourts paths --court scotus --docket 73500291 --event evt-petition-disposition --role predictor`. The initial call failed on an unwritable uv cache; it succeeded with the cache redirected to `/tmp/uv-cache`. No evaluator-only file was opened.
- No `fedcourts query` or `open-events` call was made, so there is no ranged-corpus transfer line to report. No live corpus freshness claim is made.

## Web attempts: general precedent only

1. Search query: `site.supremecourt.gov opinions Taylor Riojas 2020 Hope obvious qualified immunity 19-1261`. The web tool returned no usable content.
2. Attempted opening the historical official opinion path `https://www.supremecourt.gov/opinions/20pdf/19-1261_g3bh.pdf`. The web tool returned no usable content. Nothing from these two attempts informed the forecast.

## CourtListener MCP

1. `search(type="o", citation="536 U.S. 730", num_results=1)`: returned an unrelated Seventh Circuit case, Freedom From Religion Foundation v. Nicholson, 536 F.3d 730 (2008). Disregarded; no substantive inference from that result.
2. `search(type="o", court="scotus", case_name="Hope v. Pelzer", filed_before="2003-01-01", num_results=1)`: returned Hope v. Pelzer, 536 U.S. 730 (2002), cluster 121169, including lead opinion 9434318.
3. `search_document(opinion_id=9434318, query="obvious clarity", snippet_size=1100)`: read the majority passage at page 741 concerning fair warning without materially identical facts. Used only to verify the general legal proposition contested in its application here.

No search sought Hershey's disposition, subsequent history, the outcome of the City's companion petition, or post-decision commentary. No outcome material concerning this petition surfaced.
