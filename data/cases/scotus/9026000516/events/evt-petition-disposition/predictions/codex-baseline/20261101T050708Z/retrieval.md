# Retrieval log

No search sought this petition's disposition, subsequent history, or decision coverage. The provisioned snapshot, context, event definition, document manifest, questions presented, petition and relevant appendix sections, and empty same-question list were read locally. Stable contract/schema reads and output validation are operational, not case-outcome retrieval.

## Committed statistical context

Read `metrics/statpack.md`: modern discretionary-cert dispositions; originating-circuit cuts; paid-segment relist, CVSG, and amicus cuts; and the sal-v6 per-Term reached-band table. Used the frozen 5.18752467429925% anchor from `record/context.json`, with strictly prior 2017–2025 rows as a cross-check, not the current-Term rate.

## Corpus tool calls

Commands used `UV_CACHE_DIR=/tmp/uv-cache` and `uv run --no-sync` after the first default-cache invocation failed. No packages were installed.

1. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help` — returned structured-filter usage. A later help read used `COLUMNS=120` and `head -72` to inspect the same options.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition gvr --era 2020s --decided-before 2026 --limit 4` — returned Burford German Funding (25-1269), Roofing Designs by JR (25-1367), Pedro Jose Silva Ochoa (25-7569), and Benancio Garcia (25-901). Two, two, two, and three distributions respectively; none had an opinion body. The original transfer line was not visible in the truncated combined tool response, so I cannot accurately report its byte count.
3. The same query, piped to `jq -c '{case_id,case_name,docket_number,disposition,date_cert_granted,distribution_count,has_opinion}'`, repeated the four rows in compact form. Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --citation '608 U.S. 597' --decided-before 2026 --limit 1 --full`, piped to `jq -c '{case_id,case_name,citations,disposition,has_opinion,opinion_text}'` — returned no row and a warning that reporter citations are populated on only 200 SCOTUS rows in scope. Transfer: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`. No opinion body was returned.
5. The GVR query from item 2 was repeated with `2>&1 | sed -n '1p'` to check its transfer-report format. Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`. This supplied no additional case evidence.

The Term clock on these forward-mode queries was an extra conservative filter for historical context, not an assertion that this cell was a replay. The returned prior-Term petitions had disposition stamps in October 2026, before the November 1 snapshot. They were not this case or identified companions and were not used to infer its outcome.

## CourtListener MCP

1. `search(type="o", citation="516 U.S. 163", num_results=2)` — returned Lawrence ex rel. Lawrence v. Chater (January 8, 1996; cluster/opinion 117987), plus an irrelevant reporter-number match, Monoson, which was not used.
2. `search(type="o", court="scotus", case_name="Abouammo", num_results=2, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])` — returned the original and revised Abouammo opinions, both dated June 11, 2026. Selected revised opinion 11343328, revised June 16, 2026. Its official source is `https://www.supremecourt.gov/opinions/25pdf/25-5146_new_kifl.pdf`.
3. `read_document(opinion_id=11343328)` — retrieved the revised Abouammo primary opinion. Used the conduct-element/effects distinction, rejection of importing other offenses' conduct, and narrow statute-specific character of the holding. This is a different, already decided precedent, not the petition being forecast.
4. `search_document(opinion_id=[11343328,117987], query="reasonable probability", snippet_size=700)` — found no occurrence in Abouammo and seven snippets in Lawrence. Used the majority's discussion at 516 U.S. 167–168 concerning an outcome-relevant probability of reconsideration and the equities. Other snippets include discussion and dissent; no dissent was treated as the holding.

## Web attempts

The web tool returned an empty visible response to each of these calls, without a result list, source text, citation identifier, or explicit error. They therefore supplied no evidence and did not verify the requested pages:

1. Search: `Abouammo United States 608 U.S. 597 2026 venue Supreme Court opinion`.
2. Search: `site.supremecourt.gov "Abouammo" "venue"`.
3. Open: `https://www.supremecourt.gov/opinions/25pdf/25-5146_new_kifl.pdf`.

The later successful CourtListener search independently returned that official PDF address and opinion text.

## Operational limitation

The prescribed initial `uv run fedcourts paths --court scotus --docket 9026000516 --event evt-petition-disposition --role predictor` failed because the default uv cache was read-only. The same command succeeded with `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync`. This resolved the tooling issue without altering inputs or installing anything.
