# Retrieval record

## Provisioned inputs

Read the event definition, `record/context.json`, `record/snapshots/2026-09-29.json`, document metadata, questions presented, relevant petition sections, and the lower-court opinion in the appendix. No own-case live docket, subsequent history, realized outcome, other cell's output, or topic-label artifact was retrieved.

## Local contract and baseline material

Read `AGENTS.md`, `.github/prompts/predict.md`, the prediction and tooling schemas, and flags-schema fields; consulted the committed `metrics/statpack.md` and relevant `metrics/statpack.json` fields. Exact JSON pooling over the displayed 2017–2025 sal-v4 baseline risk sets produced 660/12,913 = 0.0511112832. This is a committed-pack observation, not a fresh corpus-wide census. Read path and serialization helpers to keep output locations and file format consistent. Local shell searches and schema inspection were not additional case retrieval.

## Corpus CLI attempts

1. `uv run fedcourts paths --court scotus --docket 9026000171 --event evt-order-call-for-response-disposition --role predictor` initially failed before command execution because uv's default cache was read-only. No corpus result or transfer line.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000171 --event evt-order-call-for-response-disposition --role predictor` succeeded and resolved case/event paths. No outcome file was opened. No transfer line.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` returned structured-filter help. A second help invocation, with `COLUMNS=140`, made the options easier to inspect. Neither accessed corpus priors or printed a transfer line.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 3` returned three unrelated grant records: `scotus/73281386` (25-1103), `scotus/73283862` (25-7026), and `scotus/73500246` (25-1343). These were not substantive IDEA analogues and did not alter the forecast. No full opinions were requested. The command's year filter is a Term mask; dates in calendar 2026 can accompany prior-Term dockets.

   `ranged corpus reads: 28 GET(s), 7340032 byte(s)`

## General legal-context web attempts

One `web.run` search invocation contained two general queries:
- `site.law.cornell.edu/uscode/text/20/1415 additional evidence preponderance`
- `site.supremecourt.gov opinions Endrew F 2017 reasonable not ideal`

The tool returned no visible results or source content. A second `web.run` invocation attempted to open `https://www.law.cornell.edu/uscode/text/20/1415`; it also returned no visible content. Neither query named this petition or sought its outcome. No information from these unsuccessful attempts entered the forecast, and no third-party authority is claimed independently verified through them.

No CourtListener MCP lookup was attempted. No direct CourtListener REST request was made.
