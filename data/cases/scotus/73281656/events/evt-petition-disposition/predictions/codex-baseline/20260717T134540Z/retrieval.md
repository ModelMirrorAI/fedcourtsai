# Retrieval beyond the provisioned inputs

## Committed base rates

- Consulted `metrics/statpack.md`, especially modern discretionary-cert dispositions, relist count, CVSG status, and the per-Term table.
- Consulted `metrics/statpack.json` for the 2025 Term paid-petition estimate (5.36% granted).

## Corpus lookup

- Command: `uv run fedcourts query --court scotus --citation 'Strickland v. Washington' --era 2020s --limit 10`
- Result: failed before returning priors because the remote corpus host could not be resolved (`EndpointConnectionError`). No `ranged corpus reads: ...` line was printed and no corpus prior was used.

## CourtListener MCP

- Opinion search: `"cumulative effect" counsel deficiencies Strickland prejudice`, court `scotus`, filed before `2026-07-17`. The result was *Kyles v. Whitley*, which did not provide a direct Strickland vehicle comparison.
- Opinion search: `Strickland totality mitigation aggravating evidence capital sentencing`, court `scotus`, filed from `2000-01-01` through `2026-07-17`. Results included *Thornell v. Jones*, *Shinn v. Kayer*, *Sears v. Upton*, *Dunn v. Reeves*, *Andrus v. Texas*, *Porter v. McCollum*, *Wiggins v. Smith*, and *Williams v. Taylor*.
- Opinion search: `verbatim adoption proposed findings due process Jefferson Upton`, court `scotus`, filed before `2026-07-17`. The result was *Jefferson v. Upton*.

No web search was used.
