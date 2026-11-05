# Retrieval record

## Local reference material

Consulted `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_tooling.schema.json`, and `schemas/agent_flags.schema.json` for the output contract. Beyond the staged case record, read only the merits and eligible Justice-vote sections of `metrics/statpack.md`, the `merits`, `justice_votes`, and `authorship` portions of `metrics/statpack.json`, and the explanatory merits/vote/authorship passages of `metrics/README.md`. Pooled merits grant Terms 2015–2024 (available rows 2017–2024) and Justice-vote/authorship Terms 2020–2024. Later displayed Term rows were not used. No cert-band table supplied an anchor.

## Corpus commands, including unsuccessful attempts

1. `uv run fedcourts query --help` failed before running because the default uv cache under `/home/codexcell/.cache/uv` was read-only. No corpus rows or transfer line returned. Retried successfully as `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help`; later inspected that help again with `UV_CACHE_DIR=/tmp/uv-cache COLUMNS=140 uv run fedcourts query --help | head -65`. These were interface reads, not corpus searches. No packages were installed.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '593 U.S. 522' --limit 2` returned no case rows and warned that only 200 in-scope rows carried reporter citations, so an empty result was not evidence that Fulton did not exist. Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era modern --disposition granted --decided-before 2025 --limit 3` was rejected because `modern` is not a permitted decade token. No corpus rows or transfer line returned. Corrected the flag as instructed by its error.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2025 --limit 3` returned RiseandShine v. PepsiCo (24-1016), Monsanto v. Durnell (24-1068), and Hikma v. Amarin (24-889). These rows carry cert grants but no usable merits judgments or opinion bodies; they are not substantively matched merits precedents. No prediction probability was inferred from them. The year clock is a coarse derived-year screen, not a guarantee that every returned date field predates 2025; the returned grant dates include 2026. This forward-mode run did not treat them as strictly prior merits observations. Transfer: `ranged corpus reads: 72 GET(s), 18874368 byte(s)`.

## Web attempts

1. `web.run` search for `site.supremecourt.gov opinions 2020 Fulton Philadelphia 19-123 exemptions sole discretion`: the tool returned no visible content or sources. No factual inference from that response.
2. `web.run` open of the official Fulton slip opinion, `https://www.supremecourt.gov/opinions/20pdf/19-123_g3bi.pdf`: again no visible content returned. Used the sanctioned CourtListener MCP path below to check the precedent instead. Neither web attempt concerned this case's outcome.

## CourtListener MCP

1. `search(type="o", citation="593 U.S. 522", num_results=1)` returned Fulton v. Philadelphia, decided June 17, 2021, cluster 4892570, combined opinion 4696349, with Roberts identified as author and the official slip-opinion location. Search query identifier: `3f1849b3`.
2. `search_document(opinion_id=4696349, query="strict scrutiny", snippet_size=450)` returned 20 of 21 matches in the combined opinion. Read the syllabus/majority excerpts distinguishing Smith, finding the discretionary-exception problem, and testing the particular refusal of an accommodation, together with the indicated concurrence material. This was general precedent, not the present case's subsequent history. I did not request the full combined opinion or any current docket/outcome for St. Mary.

No other external retrieval was attempted. Shell reads of the provisioned record, schema inspection, arithmetic over the committed statpack, and cell validation are local operations rather than additional case retrieval.
