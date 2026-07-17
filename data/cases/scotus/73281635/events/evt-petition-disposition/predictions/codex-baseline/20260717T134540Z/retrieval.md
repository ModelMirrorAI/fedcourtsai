# Retrieval beyond provisioned inputs

## Committed base rates

- Consulted `metrics/statpack.md` and `metrics/statpack.json`, including modern discretionary-cert disposition rates, originating-circuit rates, relist and CVSG cuts, and Term 2025 paid-petition rates.

## Corpus lookup

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation 'Gilliam v. Allen' --citation 'Barnard v. Theobald' --citation 'City of Milwaukee v. Cement Division, National Gypsum Co.' --limit 8`
  - The lookup failed before producing priors because the ranged corpus host could not be resolved. No `ranged corpus reads: ...` line was emitted.

## CourtListener MCP lookups

- Opinion search for `"prejudgment interest" "noneconomic damages"` (10 results). This surfaced, among other results, the Tenth Circuit opinion reported at 862 F.3d 1065.
- Opinion search for `"prejudgment interest" "pain and suffering"` (10 results).
- Case-name search for *Gilliam v. Allen* (up to 5 results).
- Case-name search for *Barnard v. Theobald* (up to 5 results).
- Case-name search for *Thomas v. Texas Department of Criminal Justice* (up to 5 results).
- Case-name search for *Nevor v. Moneypenny Holdings* (up to 5 results).
- Citation search for `297 F.3d 361` (up to 5 results), confirming the Fifth Circuit authority and its Title VII context.
- Citation search for `826 F.2d 1270` (up to 5 results), confirming the Third Circuit authority and its FELA context.
- Citation search for `862 F.3d 1065` (up to 5 results), confirming the Tenth Circuit authority and its discretionary posture.

No web search was used, and no lookup sought this case's disposition or subsequent history.
