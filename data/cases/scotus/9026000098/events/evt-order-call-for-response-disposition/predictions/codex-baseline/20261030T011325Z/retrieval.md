# Retrieval record

## Committed context and local inspection

- Read `metrics/statpack.md` and the relevant prior-Term baseline segments and aggregate metadata in `metrics/statpack.json`. The matching sal-v4 baseline reached pool for docket Terms 2017–2025 is 660 grant-family outcomes / 12,913 weighted resolved petitions. These are committed-pack figures, not a claim that the live corpus was refreshed during this cell. No generation timestamp was found among the top-level pack fields inspected.
- Read the prediction and tooling schemas and the local path/serialization helpers to construct and validate the allowed outputs. No other cell's prediction or evaluation, realized-outcome file, or topic-label artifact was read.

## Corpus CLI attempts

The initial `uv run fedcourts paths --court scotus --docket 9026000098 --event evt-order-call-for-response-disposition --role predictor` failed before execution because uv's default cache directory was read-only. Retrying with `UV_CACHE_DIR=/tmp/uv-cache` succeeded and resolved the case and event paths. This command did not retrieve a disposition.

Read query help twice: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help`, then the same command with `COLUMNS=160` and `head -65`, and once with `COLUMNS=140` and `head -38` to inspect the structured-filter documentation. These were help-only calls, with no corpus transfer report.

Executed:

```text
UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 3
ranged corpus reads: 29 GET(s), 7536640 byte(s)
```

Returned three generic grants: U.S. DOGE Service v. United States District Court for the District of Columbia (25-1103), Corey Duran Berry v. United States (25-7026), and Todd Blanche v. Izuchukwu Ozurumba (25-1343). No opinion bodies were requested. The date filter operates on derived docket year, so these earlier-Term rows can carry October 2026 grant dates; this is a forward cell, and none is this petition's disposition. They did not establish a useful subject-specific prior, and I did not use their outcomes to infer this case's outcome.

Executed `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info` to establish blob vintage. It failed because the service backend has no client-side connection and supports query/open-events forwarding instead. No newest pull stamp or stored-snapshot vintage was obtained; no direct remote-store fallback was attempted.

## CourtListener MCP

Attempted `search(type="o", court="ca1", case_name="Public Interest Legal Foundation Bellows", filed_before="2026-08-27", num_results=3)`. It returned HTTP 429, rate limit exceeded, with an indicated five-second availability delay. No opinion or search result was returned. I degraded to the provisioned petition's appellate appendix and committed base rates rather than making direct REST calls.

## General-context web attempts

Attempted one batched search with the queries `site.ca1.uscourts.gov "92 F.4th 36" voter` and `site.ca10.uscourts.gov "Public Interest" "voter" "records"`. The tool returned no visible result content. No retrieved proposition informed the forecast.

Attempted to open the official U.S. Code House page for title 52, section 20507 (`req=granuleid:USC-prelim-title52-section20507`, preliminary edition). The tool returned no visible page content. I relied on the statutory language and competing interpretations in the provisioned petition and appendix instead.

No live Supreme Court docket, this petition's disposition or subsequent history, or later case-specific coverage was sought. No outcome-revealing material about this petition surfaced.
