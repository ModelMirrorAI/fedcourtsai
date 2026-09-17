# Retrieval log

## Local context beyond the provisioned case inputs

- Read `metrics/statpack.md`: modern-cert disposition counts; paid-segment relist, CVSG and capital cuts; the sal-v4 per-Term reached-band table; and the warning about historical grant/GVR labels.
- Read selected fields of `metrics/statpack.json`, including its Term/segment structure and the baseline reached-band values for Terms 2017–2024. A local jq weighted calculation returned 593 / 11,580 = 0.05120898100172712. No corpus query or open-events call was made; there are no ranged-corpus transfer lines to report.
- Read task instructions and the prediction, tooling and flags schemas. Ran `uv run fedcourts paths --court scotus --docket 73281656 --event evt-petition-disposition --role predictor`. The default cache was read-only; the same command succeeded with its cache redirected to `/tmp/uv-cache`. This was path resolution, not a docket or outcome lookup.

## External attempts

1. Web search batch: `site.supremecourt.gov opinions Thornell Jones 2024 22-982` and `site.supremecourt.gov Rule 10 considerations governing review certiorari`. No usable result content was returned.
2. Web open attempt for the official general-precedent opinion path `https://www.supremecourt.gov/opinions/23pdf/22-982_bq7d.pdf`. No usable document content was returned. This was not Lindsey's docket or decision.
3. CourtListener MCP `search`: `type=o`, `case_name=Thornell v. Jones`, `court=scotus`, `num_results=3`. Returned HTTP 429, with a stated retry delay of 729 seconds. No opinions or snippets were delivered. Did not retry or use a direct REST fallback.

No external case facts or outcome-revealing material were obtained. No search targeted this case's disposition or subsequent history; no other predictor's output, evaluator outcome, or QP-labeling artifact was consulted.
