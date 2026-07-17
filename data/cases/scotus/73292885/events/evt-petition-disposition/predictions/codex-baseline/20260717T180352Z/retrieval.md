# Retrieval beyond provisioned inputs

No query sought this case's certiorari disposition or post-petition history.

## Corpus

- `fedcourts query --court scotus --era 2020s --limit 10`
  - `ranged corpus reads: 429 GET(s), 112328704 byte(s)`
  - Returned a generic sample of recent resolved SCOTUS priors. It did not provide a close subject-matter analogue and was used only as a qualitative calibration check.
- `metrics/statpack.md` and `metrics/statpack.json`
  - Consulted the modern discretionary-cert, 2025 Term, paid-fee, relist, and CVSG base rates.

## CourtListener MCP

- Opinion search: `q=\"coercive control\" \"protection order\" due process`, 5 results. This returned a small set of state decisions but no clear conflict bearing on the petition.
- Opinion search: `q=\"922(g)(8)\" \"bill of attainder\"`, 5 results. This returned three results, including *United States v. Emerson*, 270 F.3d 203 (5th Cir. 2001), and *United States v. Coccia*, 598 F.3d 293 (6th Cir. 2010).
- Opinion search: `q=civil protection order preponderance evidence due process confrontation`, 5 results. The search was overbroad (10,522 results) and its leading results were not useful.
- Opinion search by case name: `United States v. Emerson`, 3 results. The name search was noisy and did not isolate the intended case.
- Cluster lookup: CourtListener cluster `25545`, selected fields only. This confirmed the citation, date, docket linkage, and sub-opinion identifiers for *United States v. Emerson*.
- Repeated opinion search: `q=\"922(g)(8)\" \"bill of attainder\"`, 3 results with opinion snippets. The *Emerson* snippet states that the Fifth Circuit reversed the district court's facial Second Amendment and as-applied due-process invalidation.

No open-web search was used.
