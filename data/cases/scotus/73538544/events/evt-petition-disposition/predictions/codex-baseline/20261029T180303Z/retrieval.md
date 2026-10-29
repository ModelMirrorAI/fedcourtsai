# Retrieval record

## Committed context

- Read the modern-cert, paid-segment relist/CVSG/amicus, and matching sal-v4 band sections of `metrics/statpack.md`. Used `metrics/statpack.json` solely to pool the displayed 2017–2024 elevated risk sets: numerator 493, denominator 2,819, rate 0.17488471089038665. These are committed-pack figures, not a newly measured corpus state.
- Read the output schema and feedback schemas, and the serialization/path helpers for output compliance; these provided no legal evidence.

## Corpus and helper commands

- `uv run fedcourts paths --court scotus --docket 73538544 --event evt-petition-disposition --role predictor` and `uv run fedcourts query --help` initially failed because uv's default cache path was read-only. Retried with `UV_CACHE_DIR=/tmp/uv-cache`; both succeeded. Repeated path/help reads only confirmed the same layout and structured filters; they returned no case outcome.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition gvr --era 2020s --decided-before 2025 --limit 3` returned Monsanto Company v. Salas (24-1097), Monsanto Company v. Johnson (24-1098), and Petersen v. Doe (24-449). These were generic GVR examples, not factual analogues; none was this cell's case, and no opinion bodies were requested. The conservative Term mask restricts docket-number Terms, not calendar resolution dates; the returned 2026 grant dates precede this forward cell's October 29, 2026 vantage.
  - Exact stderr: `ranged corpus reads: 43 GET(s), 11075584 byte(s)`.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info` failed with `ValueError: the service backend has no client-side connection`. No corpus-wide vintage could be reported, and no fallback blob download or credential access was attempted.

## External legal context attempts

- Web search: `site.supremecourt.gov opinions Montgomery Caribe Transport II 2026 safety exception`. No usable result was returned.
- Web opening attempted: `https://www.supremecourt.gov/opinions/25pdf/24-1238_1b7d.pdf`. No usable content was returned. This was an attempted verification of the precedent, not a search for Casarez's outcome; no information from this unverified locator was used.
- CourtListener MCP `search`: `type=o`, `court=scotus`, `case_name=Montgomery v. Caribe`, `num_results=3`. Returned HTTP 429 daily-limit throttling, with 2,502 seconds until availability; no opinion text or search results were received. No REST fallback was attempted.

## Independent input reading

- One bounded subagent read only the provisioned combined opposition and identified the distinct Walmart and Irigoyen positions. It performed no external retrieval and wrote no files. The decisive GVR concession and reserved defenses were checked against the staged text before use.

No retrieval sought this petition's disposition, subsequent history, another cell's output, or topic-label artifacts. Montgomery's substance was used only as described in the provisioned filings after external verification yielded no usable material.
