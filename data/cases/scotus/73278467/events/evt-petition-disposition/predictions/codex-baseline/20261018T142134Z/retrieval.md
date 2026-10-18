# Retrieval record

## Local context beyond provisioned case inputs

- Read the applicable prediction instructions and output schemas, and used `fedcourts paths --court scotus --docket 73278467 --event evt-petition-disposition --role predictor` to confirm the event path. The initial invocation could not use the default read-only uv cache; retrying with a temporary cache succeeded.
- Read the relevant modern-cert, circuit, paid-relist, CVSG, and sal-v4 segment sections of `metrics/statpack.md`. Read `metrics/statpack.json` and calculated the high-band reached anchor over Terms 2017–2024: 314 grant-family equivalents / 898 weighted resolved petitions. Checked the pack's last modifying commit with `git log -1 --format='%h %cI' -- metrics/statpack.json`.
- Read the path, identifier, and serialization helpers to produce only the permitted cell outputs. No corpus `query`, `open-events`, or content-store retrieval was performed; consequently no ranged-corpus transfer line was emitted.

## Web attempts

- General-precedent searches only: `site.supremecourt.gov "Lawrence v. Chater" "GVR"` and `site.govinfo.gov "516 U.S. 163" "intervening developments"`. The web tool returned no usable content.
- Attempted to open the general precedent at `https://www.law.cornell.edu/supct/html/94-9323.ZPC.html`. The web tool again returned no usable content. No forecast proposition relies on either web attempt.

## CourtListener MCP

1. `search(type="o", citation="516 U.S. 163", num_results=1)`: returned an unrelated Monoson v. United States result, not relied on.
2. `search(type="o", case_name="Lawrence v. Chater", court="scotus", num_results=1)`: identified Lawrence ex rel. Lawrence v. Chater, January 8, 1996, 516 U.S. 163, cluster 117987, lead opinion 9433233.
3. `search_document(opinion_id=9433233, query="intervening developments", snippet_size=900)`: read the GVR standard and equitable qualifications. Used only as general procedural context.

No search requested Roybal/Griffith's disposition, subsequent history, or decision coverage. No outcome files, other predictions, evaluations, or topic-label artifacts were consulted.
