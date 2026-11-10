# Evaluation — gemini-baseline · scotus/73548979 · evt-petition-disposition (cert)

**Outcome.** Cert denied on 2026-11-09. Before that the petition was distributed three times: for the 10/9, 10/16 and 11/6 conferences. There was no CVSG and no noted dissent or statement respecting denial.

**Scores.** The prediction was `denied` at P(grant) = 0.22. `correct` = 1 and Brier = (0.22 − 0)² = **0.0484**. The harness stamps the segment base rate, basis and skill; I set none of them. This is a cert cell, so no votes are scored. It is a forward cell (snapshot 2026-10-14) and the event resolved 2026-11-09.

## Reasoning quality — 0.45
The direction and the main reason for discounting (the brief in opposition's no-real-split argument) are sound. The analysis is thin, though, and has two errors of fact or method:
- **Anchor misread.** "Elevated band grant rate roughly 7.3% to 13.1%" are the *leading terminal* figures from the 2025 and 2023 rows of the sal-v4 table. The statpack the candidate ran against was rebuilt with `statpack-at` (build 886549a3ac32, landed 2026-10-13) and graded against that build. Its table says a frozen band is scored against the bracketed risk-set ("reached") figure, and the 2025 row is the case's own Term, which should not be pooled. The prior-Term reached rates run from about 14% to 20.5%. The "relist bucket 1 ≈13.3%" figure is a terminal-state cut, not a forward rate. The final number still lands near a sensible place, but by an unsound route.
- **Amici misnamed.** The rationale credits "Manhattan Institute, Buckeye Institute, Atlantic Legal Foundation". The docket shows Instituto de Libertad Económica para Puerto Rico et al., Buckeye, and Atlantic Legal Foundation.
- It barely engages the Puerto Rico immunity question (QP 2). It does not address the Financial Oversight opening, the vehicle problems on QP 1 (Penn Central disclaimed, waiver), or the supplemental brief.

## Predicted reasoning — 0.55
I treated five claims as central: the denial, a further relist, no CVSG, a dissent from denial, and no GVR. The denial, the further relist ("decent chance"), the unlikely CVSG and the unlikely GVR all held. The document also says there is a "reasonable likelihood" of a dissent from denial by conservative Justices, and that did not happen. Most claims are hedged and generic: they commit to little beyond the disposition and the base shape of a relisted petition. That puts the grade a little above the generic midpoint, held down by the missed dissent call.

## Leakage
Mode is `forward`. The log has 33 calls, all with unobserved results, and every one reads provisioned case files, the committed statpack or the schemas. There was no external retrieval, and nothing in the prose reflects the 11/6 relist or the denial. Graded `not_applicable`, `leakage_suspected` = false.

## Semantic grades
None; this is a cert cell.
