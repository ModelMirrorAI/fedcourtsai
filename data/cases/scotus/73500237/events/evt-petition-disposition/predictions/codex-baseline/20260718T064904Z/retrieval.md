# Retrieval beyond provisioned inputs

## Corpus and base rates

- Consulted `metrics/statpack.md` and `metrics/statpack.json`, especially modern cert disposition, originating-circuit, relist, CVSG, Term, and paid-fee-class rates.
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  - `ranged corpus reads: 153 GET(s), 40108032 byte(s)`
  - Returned recent granted SCOTUS priors; used only as general calibration, not as case-specific outcome research.
- `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 8`
  - No ranged-read line was returned. The corpus sidecar timed out, so this lookup supplied no results.

## CourtListener MCP

- Opinion search: `"failure to engage in the interactive process" "independent cause of action"` (filed before July 19, 2026).
- Opinion search: `"interactive process" "good faith" "reasonable accommodation"` in the Third, Fourth, Fifth, Seventh, Ninth, Tenth, and Eleventh Circuits (filed before July 19, 2026).
- Opinion search: `"no independent cause of action" "interactive process"` (filed before July 19, 2026).
- Opinion search: `"Strife v. Aldine" OR "138 F.4th 237"` (filed before July 19, 2026).
- Opinion search: `"A.J.T. v. Osseo" "interactive process"` (filed before July 19, 2026).
- Citation lookup for `138 F.4th 237`, identifying *Strife v. AISD*, Fifth Circuit No. 24-20269, and opinion id 11052367.
- Opinion endpoint lookup for id 11052367, limited to the opinion text and basic identifiers; consulted the failure-to-accommodate analysis in *Strife*.

No web searches were used. None of the lookups sought this petition's disposition or subsequent history.
