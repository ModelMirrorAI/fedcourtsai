# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md` and `metrics/statpack.json`. The relevant estimates were: 5.36% grants for paid 2025-Term petitions; 5.4% grants for modern petitions originating in the Second Circuit; 0.8% for petitions with zero relists; 7.6% with one relist; and 3.0% with no CVSG. The case-specific response request is not a statpack cut.

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8 --corpus-backend service`
  - `ranged corpus reads: 148 GET(s), 38731776 byte(s)`
  - Consulted recent granted-petition rows for docket-stage context, including distribution counts and originating courts.
- `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 12 --corpus-backend service`
  - `ranged corpus reads: 198 GET(s), 51838976 byte(s)`
  - Consulted recent denied-petition rows for the same context. The comparison showed that multiple distributions alone occur on both sides and did not justify treating docket activity as outcome-determinative.

## CourtListener MCP

- Opinion search for `"Libretti" "Southern Union" criminal forfeiture jury Sixth Amendment` before April 27, 2026: no results.
- Opinion search for `Libretti criminal forfeiture Apprendi` before April 27, 2026: 54 results; reviewed the leading returned appellate authorities and selected *United States v. Bradley*, 969 F.3d 585 (6th Cir. 2020), for closer inspection.
- Opinion search for `Ellingburg United States 18 U.S.C. 982(a)(1) forfeiture criminal punishment` before April 27, 2026: no results.
- Citation search for *United States v. Bradley*, 969 F.3d 585, followed by retrieval of CourtListener opinion ID 4554402. The published Sixth Circuit opinion treats *Libretti* as binding, characterizes forfeiture as lacking a determinate statutory maximum, and describes the circuits as uniform on *Southern Union*'s effect.

No search sought this petition's disposition or subsequent history.
