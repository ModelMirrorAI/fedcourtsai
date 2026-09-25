# Retrieval log

## Corpus lookups (`fedcourts query`, read-only, via the cell's corpus backend)

1. `uv run fedcourts query --court scotus --era 2020s --limit 8`
   stderr: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
   Returned eight recent SCOTUS priors with no subject overlap (the command has
   no free-text filter); not used in the forecast.
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 6`
   stderr: `ranged corpus reads: 19 GET(s), 4980736 byte(s)`
   Returned six recent grants, none related to vaccination mandates; not used.

## CourtListener MCP lookups (all returned `count: 0`)

1. `search` type `o`, q `"vaccine" "Jacobson" "substantive due process" "investigational"`, courts ca1-ca11 and cadc, filed after 2024-01-01.
2. `search` type `d`, court scotus, q `vaccine (Curtis OR Boyd OR Brock OR Horsley OR Sweeney OR Carvalho)`, filed after 2025-06-01.
3. `search` type `o`, case_name `Boysen v. PeaceHealth`.
4. `search` type `d`, court scotus, case_name `Curtis v. Inslee`.
5. `search` type `d`, court scotus, q `Bellingham OR Shriners`, filed after 2026-07-01.
6. `search` type `d`, court scotus, docket_number `25-1119` (a known docket, used as a liveness check).

Every call, including the docket-number liveness check, returned zero results,
so I treated the MCP search surface as unavailable for this cell and did not
retry further. No call sought this case's own disposition.

## Base rates

`metrics/statpack.md`: "Modern discretionary-cert petitions by disposition",
"Cert petitions by relist count (paid scored segment)", "Cert petitions by
CVSG status (paid scored segment)", "Cert petitions by salience band", and
"Segment base rate by salience band (sal-v4)" (pooled OT2017-OT2024
`elevated` bracketed `reached` figures).

## Web searches

None.
