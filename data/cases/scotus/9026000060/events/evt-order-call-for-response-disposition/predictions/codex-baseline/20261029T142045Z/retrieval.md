# Retrieval log

## Local contract and historical context

- Read AGENTS.md, the prediction prompt, the prediction and tooling schemas, and the provisioned event, snapshot, context, petition/QP text and document manifest. Local inspection also covered the path/serialization helpers. No outcome, other cell output, or QP-labeling artifact was read.
- Initial `uv run fedcourts paths --court scotus --docket 9026000060 --event evt-order-call-for-response-disposition --role predictor` and `uv run fedcourts query --help` both failed because the default uv cache location was read-only. Neither reached retrieval. Reissued both successfully with `UV_CACHE_DIR=/tmp/uv-cache`. The paths command confirmed the case/event location, and help supplied the structured query interface.
- Read relevant cert sections of committed `metrics/statpack.md` and inspected `metrics/statpack.json`. A local jq calculation pooled baseline-band prefix/reached rates over all rendered prior Terms, 2017–2025: 660 grant-family equivalents over 12,913 weighted resolved petitions, 0.0511112832. This was a computation on the committed statpack, not another corpus query.

## Corpus

Command:

```text
UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 4
```

Transfer line:

```text
ranged corpus reads: 35 GET(s), 9175040 byte(s)
```

Returned four rows: U.S. DOGE Service v. United States District Court for the District of Columbia (25-1103), Corey Duran Berry v. United States (25-7026), Todd Blanche v. Izuchukwu Ozurumba (25-1343), and Missionaries of Saint John the Baptist v. Frederic (25-1131). These were recent grant-filtered examples, not matched traceability precedents or a denominator for a grant rate. No opinion bodies were requested. The year filter is the corpus's derived-year mask, not an August 2026 calendar cutoff; some grant dates were in October 2026. This is a forward cell, and none concerns the target petition. No target disposition was sought or surfaced.

## Web attempts

All returned no usable displayed results or source text, so none supplied substantive evidence:

1. Search batch: `site.supremecourt.gov opinions 2023 23-235 FDA Alliance Hippocratic Medicine traceability third parties`; `site.supremecourt.gov opinions 2023 23-411 Murthy Missouri standing independent action third party`.
2. Search: `FDA Alliance Hippocratic Medicine 2024 23-235 opinion Supreme Court pdf`.
3. Open: `https://www.supremecourt.gov/opinions/23pdf/23-235_n7ip.pdf`.
4. Find `predictable` at that same official-opinion URL.

No search named this case or sought its disposition.

## CourtListener MCP

- `search(type="o", citation="602 U.S. 367", num_results=2)`: HTTP 429, daily rate limit exceeded; no opinion returned. Stopped MCP retrieval and did not attempt direct REST access.

## Independent record review

A read-only subagent reviewed only the provisioned petition/QP and context for certworthiness and vehicle weaknesses. It did not retrieve online, query the corpus, or read outcomes/forecasts. Its main observations concerned the appellate alternative holding, generalized exposure allegations, and unresolved statutory defenses. I verified the central text locally. No other prediction was consulted.
