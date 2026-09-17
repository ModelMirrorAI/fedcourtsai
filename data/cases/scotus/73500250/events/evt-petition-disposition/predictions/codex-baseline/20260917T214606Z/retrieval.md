# Retrieval log

## Local context beyond the provisioned case record

- Read the cert disposition, paid-segment relist/CVSG, and sal-v4 per-Term risk-set tables in `metrics/statpack.md`.
- Read corresponding baseline risk-set fields in `metrics/statpack.json`; pooled displayed Terms 2017–2024 with `jq`, producing weighted denominator 11,580 and grant-family rate 0.05120898100172712.
- Used `git log -1 --format='%h %cI' -- metrics/statpack.json` to identify the artifact's commit vintage: `55121cdb8`, September 14, 2026 at 11:02 UTC. This is not a corpus freshness measurement.
- Ran `fedcourts paths --court scotus --docket 73500250 --event evt-petition-disposition --role predictor`. The initial uv invocation could not access its default cache; retrying with a writable temporary cache succeeded. No corpus query or open-events lookup was performed, and no ranged-corpus transfer line was produced.

## Web attempts

1. Searched for `site.supremecourt.gov opinions 2024 Barnes Felix 23-1239 totality circumstances May 15 2025`. The tool returned no usable result content.
2. Attempted to open the Barnes slip-opinion PDF at the Supreme Court opinions path `/opinions/24pdf/23-1239_onjq.pdf`. The tool returned no usable content. Neither attempt informed the merits analysis.

## CourtListener MCP

1. `search(type="o", citation="544 F.3d 88", num_results=1)`: returned an unrelated Bayer antitrust opinion. Disregarded; the citation field did not isolate the intended case.
2. `search(type="o", case_name="United States v. Cote", court="ca2", filed_before="2009-01-01", num_results=2)`: found the intended September 24, 2008 opinion, 544 F.3d 88, opinion ID 1314955, plus an unrelated older Cote case. Used only the 2008 case.
3. `search_document(opinion_id=1314955, query="de minimis", snippet_size=1400)`: read the bodily-injury passage at reporter pp. 100–101 and adjacent discussion of circumstantial criminal intent. This narrowed the claimed injury-threshold split materially.
4. `search(type="o", case_name="Barnes v. Felix", court="scotus", filed_after="2025-05-14", filed_before="2025-05-16", num_results=1)`: identified 605 U.S. 73, decided May 15, 2025, opinion ID 11243439.
5. `search_document(opinion_id=11243439, query="totality", snippet_size=500)`: read relevant excerpts establishing the prohibition on temporal exclusion and the reservation concerning officer-created danger. Used as preexisting legal context, not as information about Delgado's disposition.

No search requested Delgado's disposition, subsequent history, or post-decision coverage. No outcome-revealing information about the target petition was encountered. No labeling artifacts or other predictors' outputs were read.
