# Retrieval record

## Provisioned inputs

Read the event definition, `record/context.json`, `record/snapshots/2026-06-30.json`, the document manifest, the question presented, and relevant portions of `petition.txt` and the composite `brief-in-opposition.txt`. No later case docket, other predictor output, or realized outcome was consulted.

## Additional local context

- Read `metrics/statpack.md`, especially the modern-cert, paid-segment relist/CVSG, and sal-v4 per-Term segment sections.
- Read matching aggregate fields in `metrics/statpack.json`; pooled reached-high rates for every displayed strictly prior Term, 2017–2024, using `jq`: weighted grants 314, weighted resolved 898, rate 0.34966592427616927.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md` to identify the committed pack's file vintage: `55121cdb8`, September 14, 2026 at 11:02 UTC. This is not a corpus-wide pull timestamp.
- Read task and schema contracts. Ran `uv run fedcourts paths --court scotus --docket 73281009 --event evt-order-cvsg-disposition --role predictor`; the default cache location was read-only, so the command was rerun successfully using a writable temporary cache.
- No `fedcourts query` or `open-events` call was made; consequently there are no ranged-corpus-read transfer lines.

## CourtListener MCP

1. `search(type="o", citation="520 U.S. 893", num_results=2)` returned Lords Landing Village Condominium Council of Unit Owners v. Continental Insurance Co., decided June 2, 1997, cluster 1088005, together with an unrelated result that was disregarded.
2. `read_document(opinion_id=9527092)` read the Lords Landing majority opinion. Used only to assess the general GVR route for a recent state-law development and the significance of an unsuccessful lower-court reconsideration request. No search targeted Eakin or its later history.

## Web attempts

- Searched `site.supremecourt.gov "Rule 10" "compelling reasons" "erroneous factual findings"` for general certiorari standards.
- Attempted to open the Supreme Court's `filingandrules/2023RulesoftheCourt.pdf` and find `compelling reasons` within it.
- All three web calls returned no visible source text or results. No web result informed the forecast, and no case disposition was exposed.
