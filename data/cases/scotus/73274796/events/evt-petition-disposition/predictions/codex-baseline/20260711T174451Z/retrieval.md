# Retrieval log

## Committed base rates

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” “SCOTUS petitions by Term,” “SCOTUS petitions by originating circuit,” and “SCOTUS cases by era,” to calibrate the baseline. The modern resolved sample contains 148 denials, 9 grants, 28 other dispositions, and 5 dismissals; the 2025 Term sample reports 91.3% denied, 5.6% granted, and 3.1% dismissed.

## Corpus lookup

- Command: `uv run fedcourts query --court scotus --era 2020s --citation 'Employment Division v. Smith, 494 U.S. 872' --limit 8 --corpus-backend ranged`
  - Purpose: retrieve recent resolved SCOTUS priors sharing the principal Free Exercise authority.
  - Result: failed before returning any prior because the ranged corpus host could not be resolved (`EndpointConnectionError`). The command emitted no `ranged corpus reads: ...` line, so no corpus prior informed the prediction.

## CourtListener MCP

- Opinion search for `"health care sharing ministry" "Free Exercise"`, filed through July 11, 2026. Returned 11 results. The most relevant was *Zion HealthShare, Inc. v. Office of the Insurance Commissioner* (Washington Court of Appeals, Feb. 5, 2026); the remaining leading results principally concerned ACA challenges rather than another HCSM/free-exercise appellate dispute.
- Cluster lookup for CourtListener cluster 10786678, confirming *Zion HealthShare* was a published Feb. 5, 2026 decision with opinion 11253319.
- Opinion lookup for CourtListener opinion 11253319. Consulted the opinion's discussion upholding the agency's conclusion that Zion made enforceable promises and was an insurer, and rejecting its constitutional challenges.
- Opinion search for case name `Renteria v. Kane` in the Tenth Circuit between Feb. 1 and Mar. 15, 2025. No results.
- Opinion search for `Renteria Kane Gospel Light Mennonite`, filed before July 28, 2025. No results.
- Opinion search for `"health care sharing ministry" preemption insurance`, filed through July 11, 2026. Returned six results, none establishing a federal appellate conflict over state regulation of HCSMs.
- Docket-item lookup for CourtListener docket 73274796. The first request included two unavailable fields and returned a field-validation error; a corrected request confirmed docket 25-113 was pending, with neither `date_cert_granted` nor `date_cert_denied` populated and no termination date.
- Endpoint-schema lookup for `docket-entries`, followed by a docket-entry query for docket 73274796. No API docket-entry records were returned.
- RECAP search for `"Breanna Renteria" "New Mexico Office" "Solicitor General"`, filed through July 11, 2026. No results.
- Docket-index search for case name `Breanna Renteria` and docket number `25-113`. No search-index result.
- Opinion search for the *Tandon* phrase `"Comparability is concerned with the risks various activities pose" "Free Exercise"`, filed through July 11, 2026. Returned five appellate decisions applying that risk-based formulation, including *M.A. v. Rockland County Department of Health* and *We the Patriots USA, Inc. v. Connecticut Office of Early Childhood Development*.

No REST fallback or general web search was used.
