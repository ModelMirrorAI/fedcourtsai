# Retrieval log

## Local inputs and reference material

- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, flags, and tooling schemas.
- Read the provisioned event, context, October 3 snapshot, document manifest, and application text. No other predictor output or outcome artifact was consulted.
- Read `metrics/statpack.md`, specifically its interim section, and inspected the top-level keys of `metrics/statpack.json` for provenance metadata. Used strictly prior application-Term counts: 31 grants / 296 resolved.
- Ran `uv run fedcourts paths --court scotus --docket 9526000458 --event evt-motion-disposition --role predictor`. The initial call failed because the default uv cache was read-only; retrying with a writable temporary cache succeeded. This command resolves paths, not corpus facts.
- No `fedcourts query`, `open-events`, corpus pull, or corpus body retrieval was performed; consequently there is no ranged-corpus transfer line to report.

## Web searches

The following exact queries returned no usable search results, and supplied no substantive facts:

1. `site.supremecourt.gov Wisconsin Right to Life 2004 injunction indisputably clear`
2. `site.supremecourt.gov Nken Holder 2009 stay injunction distinction`
3. `"West Virginia v. B.P.J." "2026" "2371"`
4. `"Mirabelli v. Bonta" "607" "492"`

These queries concern general authorities, not the disposition of this application.

## CourtListener MCP

1. `search(type="o", citation="542 U.S. 1305", num_results=1)` returned *Wisconsin Right to Life, Inc. v. Federal Election Commission*, decided September 14, 2004, opinion/cluster 137724.
2. `read_document(opinion_id=137724)` returned the full 5,282-character opinion. Used the All Writs Act injunction standard at 542 U.S. 1306, not the unrelated case's substantive election-law result as an analogue.

No target-case disposition, subsequent history, or outcome-revealing coverage was sought or encountered.
