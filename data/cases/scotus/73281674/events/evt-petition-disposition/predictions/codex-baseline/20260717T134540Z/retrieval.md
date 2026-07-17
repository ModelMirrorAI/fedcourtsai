# Retrieval beyond the provisioned inputs

## Committed base rates

- Read `metrics/statpack.md`, including modern discretionary-cert disposition, originating-circuit, relist, CVSG, and per-Term tables.
- Read the 2025 Term paid/IFP detail in `metrics/statpack.json`. The estimated paid-petition grant rate was 5.36%.

## Corpus query

- Command: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --citation '603 U.S. 369' --citation '397 U.S. 99' --limit 8`
- Result: failed before returning rows because the ranged corpus host could not be resolved (`EndpointConnectionError`). No `ranged corpus reads: ...` line was printed.

## CourtListener MCP

- Opinion search for `"foreseeable pecuniary harms" NLRB Thryv`, limited to decisions filed before July 17, 2026. It returned relevant Third, Fifth, Sixth, Ninth, and D.C. Circuit decisions, confirming active appellate treatment of the remedy issue.
- Opinion search for `"Vermont Information Processing" NLRB Thryv`, limited to decisions filed before July 17, 2026. It located *Vermont Information Processing, Inc. v. NLRB* (D.C. Cir. May 26, 2026).
- Retrieved CourtListener opinion record 11331702 for *Vermont Information Processing, Inc. v. NLRB*. The opinions reflect disagreement over preservation and the statutory validity/ripeness of a *Thryv* challenge, reinforcing the procedural complexity of this issue.
- Opinion search for `"District Hospital Partners" "substantially fewer rights" bargaining proposals`, limited to decisions filed before July 17, 2026. It located *District Hospital Partners, L.P. v. NLRB*, 141 F.4th 1279 (D.C. Cir. 2025), which treated the package of bargaining proposals under a totality-of-conduct framework.

No web search was used.
