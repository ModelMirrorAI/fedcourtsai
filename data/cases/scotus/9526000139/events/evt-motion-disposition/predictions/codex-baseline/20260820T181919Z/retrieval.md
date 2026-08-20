# Retrieval

- Consulted `metrics/statpack.md`, “The interim docket (applications),” for the strictly prior-Term substantive-application baseline. No corpus query was run.
- CourtListener MCP search: RECAP, First Circuit docket `26-1774`, filed before `2026-07-30`, limited metadata. It identified *State of California v. Trump*, docket ID 73568304.
- CourtListener MCP search: the same docket with cause, nature-of-suit, and RECAP-document metadata. It identified the voting nature of suit and pre-event filings.
- CourtListener MCP document read: RECAP document 485454574 (supplemental record). CourtListener reported that no text was available.
- CourtListener MCP search: RECAP query for `"State of California" Trump voting stay`, First Circuit and District of Massachusetts, filed before `2026-07-30`. It surfaced the emergency stay motion and opposition; the broad response was truncated.
- CourtListener MCP document read: RECAP document 485347180, chunks 0–3. This was the federal defendants' July 7 emergency stay motion and supplied the challenged executive-order provisions, procedural posture, and applicants' justiciability theory.
- CourtListener MCP endpoint-schema lookup for `docket-entries`, used to constrain later calls.
- CourtListener MCP docket-entry call for First Circuit docket ID 73568304 through `2026-07-29`. The first attempt was throttled; the retry succeeded but returned a very large truncated response.
- CourtListener MCP docket-entry call using a `2026-07-20` to `2026-07-29` range. The API rejected the range encoding.
- CourtListener MCP docket-entry call using separate lower and upper date bounds for `2026-07-20` through `2026-07-29`. It identified the July 25 order denying both stay motions and the partial dissent.
- CourtListener MCP docket-entry call for entry ID 472137409. It supplied the pre-event First Circuit order, including the dissent's proposed partial stay and its treatment of the Postal Service provisions.
- No web search and no lookup of this Supreme Court application's disposition or subsequent docket history.
