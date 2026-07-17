# Retrieval

## Committed base-rate context

- `metrics/statpack.md`: modern discretionary-cert disposition, Seventh Circuit, zero-relist, no-CVSG, and per-Term rates.
- `metrics/statpack.json`: 2025 Term paid-petition estimate (5.36% granted).

## Corpus lookup

- Command: `uv run fedcourts query --court scotus --citation 'Tyler v. Hennepin County' --era 2020s --limit 10`
- Result: failed before returning rows because the ranged corpus S3 hostname could not be resolved. No `ranged corpus reads: ...` line was emitted.

## CourtListener MCP

- Opinion search: `Takings Clause police power forfeiture Tyler Bennis`, opinions filed before 2026-07-17. Returned the Seventh Circuit decision below and general related authorities including *Jenkins v. United States*.
- Exact opinion searches for *Hadley v. City of South Bend*, *Pena v. City of Los Angeles*, and *Slaybaugh v. Rutherford County*, limited to opinions filed before 2026-07-17. Returned the 2025 Seventh and Ninth Circuit opinions for *Hadley* and *Pena*; no *Slaybaugh* result.
- Detail searches for the 2025 *Hadley* and *Pena* opinions, including their opinion metadata.
- Exact opinion search for *Pung v. Isabella County*, limited to 2026 opinions filed before 2026-07-17. Returned the Supreme Court's June 23, 2026 opinion.
- Opinion endpoint lookup for *Pung*, opinion id 11346051, limited to `id`, `type`, and `html_with_citations`. Consulted the syllabus and relevant Takings Clause analysis.

No web search was used.
