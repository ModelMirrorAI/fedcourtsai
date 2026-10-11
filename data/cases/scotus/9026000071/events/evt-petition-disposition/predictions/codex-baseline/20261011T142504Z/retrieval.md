# Retrieval record

## Provisioned inputs

Read the event definition, `record/context.json`, and `record/snapshots/2026-10-11.json`; read the document manifest and questions presented, with substantive excerpts from `petition.txt`, `brief-in-opposition.txt`, and `cert-reply.txt`. These were local provisioned inputs. No evaluator-only outcome, other prediction, or QP-label artifact was read.

## Beyond provisioned inputs

1. Read the committed `metrics/statpack.md` modern-cert, circuit, paid relist/CVSG, and sal-v4 reached-band sections. Read `metrics/statpack.json` to pool exact reached-elevated values for Terms 2017-2025: 524 / 3,113 = 0.1683263733. Other section headings and aggregate rows surfaced during table navigation but were not anchors. Checked the pack's last commit with `git log -1 --format='%h %cI' -- metrics/statpack.md`: `3f3ca14f4 2026-10-08T21:56:24Z`.
2. Web search: `site.supremecourt.gov Rule 10 considerations governing review certiorari judicial discretion`. The tool returned no usable content.
3. Web open of the official rules PDF at `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`. The tool returned no usable content; no material from it informed the forecast.
4. CourtListener MCP `search(type="o", citation="596 U.S. 832", num_results=3)`. Returned United States v. Washington, decided June 21, 2022, cluster 6479294, opinion 6351405. Also returned an unrelated 1987 Federal Circuit case, disregarded.
5. CourtListener MCP `search_document(opinion_id=6351405, query="discriminat", snippet_size=350)`. Read excerpts on intergovernmental immunity and discrimination against federal contractors.
6. CourtListener MCP `search_document(opinion_id=6351405, query="Over time", snippet_size=1700)`. Read section III.A's explanation distinguishing direct regulation/discrimination from mere increased federal costs. This historical precedent, not this petition's outcome, was the only external substantive case material consulted.

No `fedcourts query` or `open-events` call was made, so there is no ranged-corpus transfer line. The Nwauzor discussion relies only on the provisioned petition, opposition, and reply; its live docket and later disposition were not sought.

## Local contract and checks

Read `AGENTS.md`, the prediction prompt, prediction/flags/tooling schemas, and path/serialization helpers. Ran `uv run fedcourts paths --court scotus --docket 9026000071 --event evt-petition-disposition --role predictor`; the default cache was read-only, so the successful repeat used a cache under `/tmp`. These are local contract operations, not substantive outcome retrieval.
