# Retrieval record

## Provisioned and committed material

- Read the task contract, output schemas, event definition, case-level context and `2026-08-29.json` snapshot, document manifest, questions-presented extract, and relevant petition passages, including the appended Federal Circuit opinion. No response was provisioned for this response-requested moment.
- Consulted the committed `metrics/statpack.md` and the corresponding `metrics/statpack.json` risk-set fields. Computed the prior-Term private-baseline anchor as 660 / 12,913 = 0.0511112832 over OT2017–OT2025. Corpus-wide freshness was not available; these are committed-pack figures, not a live refresh.

## Corpus calls, including failed attempts

1. `uv run fedcourts paths --court scotus --docket 9026000170 --event evt-order-call-for-response-disposition --role predictor` and `uv run fedcourts query --help` initially failed before execution because uv's default cache directory was read-only. No corpus data was returned.
2. Retried those two administrative commands with `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync ...`. Both succeeded. The path command did not expose an outcome, and the help command documented structured query filters. Neither printed a ranged-transfer line.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --era 2020s --disposition denied --decided-before 2026 --limit 3` succeeded. Exact transfer report: `ranged corpus reads: 11 GET(s), 2883584 byte(s)`. Returned Google LLC v. VirtaMove, Corp., et al. (scotus/73265705), Hastings College Conservation Committee, et al. v. California, et al. (scotus/73266074), and Ryan O'Donnell, et al. v. City of Chicago, Illinois, et al. (scotus/73281381). All were denied, as requested by the filter. None was this cell's case. The derived-year clock admitted denial dates of October 19, 2026; this forward cell did not use them as pre-August-29 analogues. No aggregate inference was drawn from the selected rows.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts corpus-info` failed: the service backend has no client-side connection for this command. It returned no vintage report or transfer line. No credential extraction, alternate cloud access, or corpus mutation was attempted.

## External calls

- Web search query: `site.supremecourt.gov opinions 2019 Thryv Click-to-Call 314(d) SAS institution`. The tool returned no usable result or source text. This sought general precedent, not this petition or its outcome.
- CourtListener MCP `search`, type `o`, court `scotus`, case_name `Thryv`, num_results `3`: failed with HTTP 429, daily rate limit exceeded. No opinion text was returned. Degraded to provisioned materials and corpus/statpack context; no direct CourtListener REST fallback was attempted.

No lookup sought the disposition or subsequent history of Federal Express v. Qualcomm. No other prediction, evaluation, or topic-label artifact was read.
