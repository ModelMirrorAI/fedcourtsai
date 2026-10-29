# Retrieval record

## Local inputs and tools

Read AGENTS.md, the prediction prompt, prediction/flags/tooling schemas, the
event definition, `record/context.json`, and `record/snapshots/2026-09-23.json`.
The provisioned record contains no filed-document text. Also consulted the
committed `metrics/statpack.md` and `metrics/statpack.json`, and the local path,
schema, and serialization helpers to resolve output paths and validate files.
No other cell's prediction/evaluation or topic-label artifact was read.

`uv run fedcourts paths --court scotus --docket 9026000146 --event evt-order-call-for-response-disposition --role predictor`
and `uv run fedcourts query --help` initially failed because uv's default cache
was read-only. Both succeeded with `UV_CACHE_DIR=/tmp/uv-cache`. The paths
command was repeated successfully; the query help was also re-read. These
were setup/help calls, not corpus lookups.

## Corpus lookups

1. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era modern --decided-before 2026 --limit 4`
   failed: `modern` is not an era token. The CLI returned the valid decade
   vocabulary and filter instructions. No transfer line was emitted.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 4`
   succeeded and returned four grant-side priors, with distribution counts of
   2, 5, 2, and 2. This outcome-selected set was not treated as a grant-rate
   sample. It did not include the target case. Transfer line:

   `ranged corpus reads: 34 GET(s), 8716288 byte(s)`

The optional Term filter was used although this is a forward cell. Some
returned prior petitions were granted after the target's snapshot date; I did
not use those dates as snapshot-time evidence or retrieve the target's outcome.

## CourtListener MCP

Attempted opinion search with `type=o`, `court=ca10`,
`docket_number=24-1191`, `filed_before=2026-09-23`, `num_results=3`.
It returned HTTP 429: daily limit 1400 exceeded, with availability estimated
in 6035 seconds. No opinion or docket was obtained through MCP. No direct
CourtListener REST request or credential workaround was attempted.

## Web and primary-source retrieval

Attempted web searches:

- `site.ca10.uscourts.gov "24-1191"`
- `"Baltazar" "Daley" "Tenth Circuit"`

Attempted two web opens of the official lower-court opinion:

`https://www.ca10.uscourts.gov/sites/ca10/files/opinions/010111328396.pdf`

For reliable text access, attempted a shell `curl` of that same official PDF
piped to `pdftotext`. The pipeline failed because `pdftotext` was not installed;
curl reported a broken downstream write. Then retrieved the same PDF using
Python `urllib.request.urlopen` and parsed it in memory with the installed
`pypdf.PdfReader`: 30 pages, No. 24-1191, filed November 3, 2025. Read the
first five pages. A second in-memory fetch searched extracted pages for split
and named-precedent terms and displayed pages 4 and 25–27, confirming the
express disagreement. No document was added to the provisioned record.

The substantive external source used is the Tenth Circuit's dated opinion,
pages 3–5 and 26–27. I did not retrieve the Supreme Court docket, this
petition's disposition, later history, other forecasts, or reporting on a
Supreme Court decision in this case.
