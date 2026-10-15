# Retrieval log

## Provisioned inputs

Read the event definition, `record/context.json`, `record/snapshots/2026-10-15.json`, the document manifest, questions presented, petition, brief in opposition, relevant appendix passages, and the empty extracted reply. No outcome artifact or other predictor's output was consulted.

## Committed base-rate context

- Read `metrics/statpack.md`: modern discretionary-cert disposition totals, paid-segment relist and CVSG cuts, and the sal-v4 segment table.
- Read matching fields in `metrics/statpack.json`. Restricted the numerical anchor to baseline reached risk sets for Terms 2017–2025. Summed 643 weighted grants and 12,877 weighted resolved petitions, yielding 0.04993399083637493.
- Ran `git log -1 --format='%h %cI %s' -- metrics/statpack.md` to identify the committed pack refresh: cf9ae960e, October 13, 2026 at 19:17:46 UTC.
- Ran `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000249 --event evt-petition-disposition --role predictor` to resolve the cell. The first attempt without the temporary cache override failed because the default cache directory was read-only.
- No `fedcourts query` or `open-events` call was made; there are no ranged-corpus transfer lines to report.

## Web attempts

All three calls returned no usable content and contributed no substantive evidence:

1. Search: `site.supremecourt.gov Rule 10 considerations governing review on certiorari erroneous factual findings misapplication properly stated rule law`.
2. Open: `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`.
3. Open: `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`.

No search named the target case or sought its disposition.

## CourtListener MCP

1. `search(type="o", citation="51 Cal. 3d 202", num_results=2, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])`. Returned Kimmel v. Goland, decided July 12, 1990, opinion id 5452298, and an unrelated 2016 result, Diocese of San Joaquin v. Gunner. Used only Kimmel; did not pursue the unrelated result.
2. `search_document(opinion_id=5452298, query="noncommunicative", snippet_size=1100)`. Read the three returned passages, including the introductory holding and its limitation to illegal recording, and the discussion distinguishing communicative injury from independent conduct. This confirmed the petition's doctrinal premise but did not establish any conflict warranting certiorari.

No live retrieval concerned the target case's outcome or subsequent history.
