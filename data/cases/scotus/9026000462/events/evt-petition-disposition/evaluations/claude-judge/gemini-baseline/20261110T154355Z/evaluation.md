# Evaluation — gemini-baseline, scotus/9026000462 (Hauber v. Honkamp Krueger & Co.), evt-petition-disposition

**Stage:** cert (forward, `moment: distribution`). **Outcome:** denied 2026-11-09, no noted dissent, no CVSG, two distributions.

## Scores
- Predicted `denied` at P(grant) = 0.005 → `correct` = 1, `brier_score` = 0.000025.
- `segment_base_rate`, `brier_skill_score` and `base_rate_basis` are left for the harness stamp; I quote no rate of my own. Votes are not scored on a cert cell.

## Reasoning quality — 0.45
The final number and the direction are right, and the rationale names the right vulnerabilities: a pro se petitioner, a respondent waiver, the rarity of a grant without a response, and a fact-bound ADA dispute. The analysis is thin and partly mis-anchored, though. I rebuilt the statpack the candidate was placed against (`statpack-at`, build 1c4f550b7b75, the same `sal-v4` table). Its "~0.9%" figure is the baseline band's *terminal* (leading) rate for a single Term, OT2025. For a cell with a frozen band, the pack directs anchoring on the bracketed risk-set `reached` rate, pooled over prior Terms, and that figure is several times higher. So the "slight downward adjustment" was made from the wrong anchor. Two further problems: the claim that a waiver "strongly signals" the respondent thinks the petition meritless overstates what a waiver means, and the rationale never notices that the single frozen distribution belonged to the sealing motion. The prose is one paragraph long, with no stated uncertainty and no account of the posture below.

## Predicted reasoning — 0.4
Central claims: (1) "Distributed once so far; expect no further relists before a decision." This was not borne out. The petition was distributed again on Oct 14 for the Nov 6 conference before the denial, because the earlier distribution was the motion's. That second distribution is not a relist after a cert conference, but the document's specific procedural forecast was that the count would stay at one, and it did not. (2) No call for a response and no CVSG: held. (3) No writing on denial: held. (4) The conditional summary route: unresolved. The one specific procedural call failed, and the remaining claims are the generic defaults for this kind of petition, which puts the document between the 0.25 and 0.5 anchors.

## Leakage
Forward. The prediction was made 2026-10-08 and the denial issued 2026-11-09. Result capture is 0.0 because every call is unobserved, which is an engine's standing shape. Graded on their queries, the calls are CourtListener searches for the Eighth Circuit opinion and the lower-court dockets, plus reads of provisioned inputs and the statpack. There is no disposition query and no `qp-topics` read. Graded `not_applicable`, so `leakage_suspected` = false.

## Semantic grades
Cert cell: no semantic set is declared, so none was written.
