# Retrieval record

## Corpus

- Read command help using `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help`, then repeated the help display with `COLUMNS=180` and `COLUMNS=150` for legibility. These are help calls, not corpus reads.
- Executed `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition denied --decided-before 2026 --limit 5`.
  - Transfer report: `ranged corpus reads: 16 GET(s), 4194304 byte(s)`.
  - Returned five cert denials, including petitions by Google LLC, Hastings College Conservation Committee, Ryan O'Donnell, Utah, and Amy Hadley. These were not comparable substantive stay applications; none was used as an interim base rate or a substantive analogy. No opinion bodies were requested.

## General legal context

- Web search attempted: `site.supremecourt.gov Hollingsworth Perry 558 U.S. 183 stay reasonable probability fair prospect irreparable harm`. The tool returned no visible results or usable text.
- Web open attempted for the historical U.S. Reports PDF at `https://tile.loc.gov/storage-services/service/ll/usrep/usrep558/usrep558183/usrep558183.pdf`. The tool returned no visible document content. No proposition was taken from that attempt.
- CourtListener MCP `search`: type `o`, citation `558 U.S. 183`, limit 2, requested case name, date, citation, URL, and opinions. Returned *Hollingsworth v. Perry* (January 13, 2010), including lead opinion 9413203 and combined opinion 1747, plus an unrelated second result. Only Hollingsworth was used.
- CourtListener MCP `search_document`: opinion 9413203, literal phrase `reasonable probability`, snippet size 900. Returned the passage at reporter page 190 setting out the stay-pending-certiorari standard. Used as general procedural context, not as a factual analogy.

## Local reference and utility reads

Read the prediction prompt and schemas, event definition, provisioned snapshot, document manifest, empty application text, and context. Read the interim and applicant-class sections of `metrics/statpack.md` and the corresponding `metrics/statpack.json` data. Computed the OT2016–OT2025 finer-reading pool and applicant cut locally with `jq`.

Ran `fedcourts paths` for this cell: its first invocation failed because the default uv cache directory was read-only; repeating with `UV_CACHE_DIR=/tmp/uv-cache` succeeded. Also inspected file listings and working-tree status without reading any outcome, prediction by another cell, evaluation, or labeling artifact. The local validation command is recorded by the engine transcript.

No retrieval requested this application's current docket, disposition, subsequent history, or decision coverage. No application PDF was independently downloaded.
