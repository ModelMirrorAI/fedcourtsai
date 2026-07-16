# Retrieval

## Corpus

- Attempted: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --citation 'Trinity Lutheran Church of Columbia, Inc. v. Comer, 582 U.S. 449 (2017)' --citation 'Carson v. Makin, 596 U.S. 767 (2022)' --limit 8 --corpus-backend ranged`
- Result: the command failed with an endpoint name-resolution error before returning priors. It printed no `ranged corpus reads: ...` statistics line.
- Consulted the committed `metrics/statpack.md`, including modern discretionary-cert, originating-circuit, relist, CVSG, and per-Term base rates.

## CourtListener MCP

- Opinion search for `Union Gospel Mission of Yakima v. Brown` in the Ninth Circuit. It returned the January 6, 2026 panel decision and the June 18, 2026 en banc order.
- Retrieved CourtListener cluster 10877281 and opinion 11344784. The June 18 order grants rehearing en banc and vacates the three-judge panel opinion.
- Opinion search for `St. Mary Parish v. Roy` in the Tenth Circuit; no result was returned.
- Opinion search for `universal preschool religious school` in the Tenth Circuit, limited to January 1, 2025 through July 16, 2026; no result was returned.
- Citation search for `154 F.4th 752`; no result was returned.

No web search was used. No lookup sought this case's disposition or subsequent history.
