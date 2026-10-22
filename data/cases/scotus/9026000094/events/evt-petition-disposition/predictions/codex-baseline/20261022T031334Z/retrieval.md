# Retrieval log

## Local statistical context

- Read `metrics/statpack.md`: modern discretionary-cert disposition and circuit tables, paid-segment relist/CVSG cuts, and sal-v4 per-Term reached-band table.
- Read `metrics/statpack.json` for the matching sal-v4 elevated risk-set fields. A local `jq` calculation pooled Terms 2017–2025, producing numerator 526, denominator 3,122, rate 0.16848174247277387. No individual corpus case rows or outcome artifacts were consulted.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.json metrics/statpack.md`: latest pack commit `ac757d745`, dated `2026-10-19T05:54:06Z`. This dates the committed artifact, not the corpus blob.
- Attempted `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info`. It failed because the service backend has no client-side connection; the error directs service clients to `query` and `open-events`. No corpus freshness stamps were returned and no ranged-transfer line was printed.
- No `fedcourts query` or `fedcourts open-events` call was made.

## General legal context, not this case's history

Web tool calls:

1. Search: `site.supremecourt.gov "Rule 10" "misapplication of a properly stated rule of law"`.
2. Search, in the same call: `site.loc.gov "Lawrence v. Chater" "reasonable probability"`.
3. Open attempt: the official Supreme Court 2023 Rules PDF under the Court's filing-and-rules site.

These web calls returned no usable source text in this session and were not relied on. None searched for this petition or its disposition.

CourtListener MCP calls:

1. `search(type="o", citation="516 U.S. 163", num_results=1, fields=["caseName", "citation", "dateFiled", "id", "absolute_url", "snippet"])`. The citation filter returned an unrelated fuzzy match, Monoson v. United States, 516 F.3d 163 (2008), and a missing-fields warning. That result was not used.
2. `search(type="o", q='caseName:"Lawrence v. Chater"', court="scotus", num_results=2, fields=["caseName", "citation", "dateFiled", "cluster_id", "opinions", "absolute_url"])`. Returned Lawrence Ex Rel. Lawrence v. Chater, 516 U.S. 163, decided January 8, 1996, cluster 117987; identified lead opinion 9433233.
3. `search_document(opinion_id=9433233, query="reasonable probability", snippet_size=650)`. Read the general GVR standard at pages 167–68 and the returned surrounding passages. Used only to assess the independent-ground objection to a possible GVR.

No live search, docket lookup, or opinion lookup concerning this petition's disposition or subsequent history was made. No lookup of King's later en banc outcome was made. The provisioned filings supply all case-specific facts used in the forecast.

## Contract and tooling reads

Read `AGENTS.md`, `.github/prompts/predict.md`, output schemas, and the repository's path/identifier/serialization helpers. Ran the prescribed `fedcourts paths` command with the literal cell identifiers. Its initial invocation failed because the default uv cache was read-only; retrying with a temporary cache succeeded. These were contract and output-preparation reads, not additional case evidence.
