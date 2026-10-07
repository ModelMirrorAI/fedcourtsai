# Evaluation: claude-baseline — scotus/73302615, evt-petition-disposition

**Stage:** cert (event.yaml `stage: cert`). **Outcome:** petition denied on 2026-10-05 after the September 28 long conference, no noted dissent, Justice Kavanaugh not participating; `actual_granted` 0, two distributions, no CVSG.

## Scores

| Field | Value | Basis |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` denied == `actual_disposition` denied |
| `brier_score` | 0.0441 | (0.21 − 0)² |
| `segment_base_rate` | 0.172242 | elevated band, bracketed **reached** figure, sal-v4 table, Terms 2017–2024 pooled resolved-weighted: 484 / 2810 |
| `base_rate_basis` | risk_set | the prediction froze `context.band` = elevated **and** `context.salience_version` = sal-v4, matching the table heading |
| `brier_skill_score` | −0.486 | 1 − 0.0441 / (0.172242)² = 1 − 0.0441 / 0.029667 |
| `reasoning_quality` | 0.76 | below |
| `vote_accuracy` | omitted | cert cell, never scored |
| `judgment_correct` | null | no judgment on either side |

Base-rate window: the sal-v4 table caption says it renders all 10 Terms the pack holds, so the rendered and pack windows coincide and nothing is flagged. Strictly-prior to Term 2025 leaves 2017–2024. The candidate pooled the same eight rows and reached the same 17.2% on n = 2810. The cell's own `record/context.json` band is terminal and was not used.

## What the prediction got right and wrong

Right: the disposition, and a probability that still kept denial as the clear modal outcome. The legal analysis is the richest of the three. It identifies the call for a response after waiver as the docket's clearest signal, reads the split accurately (the decision below expressly departs from the Second and Fifth Circuits; the opposition's answer is staleness and shallowness, not non-existence), situates the case in the Court's recent FSIA-expropriation line (Helmerich I, Philipp, Simon), and then weighs the vehicle problem properly: interlocutory, with the act-of-state holding reached through pendent appellate jurisdiction on a collateral-order immunity appeal, with Swint cited for the Court's scepticism of that route. It also makes the subtle point that Simon's own description of the Amendment suggests the Court might simply agree with the D.C. Circuit, which cuts against granting to resolve a split the other side may abandon. It read the August 26 withdrawal letter off the docket and carved out a dismissal tail. Its cross-check of the relist bucket correctly notes that the second distribution followed a CFR, not a bare relist.

Where it is weaker: having said the vehicle problem is "the strongest point in the BIO and I weight it heavily", the net number still lands above the anchor, on the strength of a judgment that a CFR after waiver roughly doubles the base rate. The document is candid that this is judgment rather than a computed figure, which is to its credit, but the two halves of the analysis pull against each other and the resolution is asserted rather than argued. The CVSG expectation (one in three) leaned, by the candidate's own account, on prior FSIA cases and on 2026 political context held from training rather than from any provisioned document; disclosed, but a soft foundation for the number that most drove the forecast upward. The statement that the decision below was by Judge Katsas for a unanimous panel is not verifiable from the provisioned petition or opposition text; minor, and not relied on for anything.

The 0.21 against a denial is a worse Brier than the anchor would have earned, but the question here is soundness, not hindsight: the analysis is thorough, honest about its uncertainties, and correct on every checkable point of law and procedure.

## reasoning_quality: 0.76

Correct anchor and window, strong and accurate legal analysis, well-chosen cross-checks, honest disclosure of where the numbers rest on judgment and training context. Marked down for the tension between heavily weighting the vehicle defect and still moving above the anchor, and for the CVSG-driven uplift resting on unprovisioned context. Graded on `reasoning.md` alone; the forecast document and the claims block were read for context only and are not scored here.

## Leakage

Mode forward; `retrieved_outcome_material` false; `influenced_prediction` not_applicable; `leakage_suspected` false. Predicted 2026-09-18, decided 2026-10-05. Every call captured. The CourtListener docket lookup for No. 25-1256 returned a null termination date (document date 2026-05-06), which confirms the forward provisioning rather than undermining it; the only other external hit is the 2025-10-03 D.C. Circuit opinion, which predates the petition. Two corpus queries returned nothing about this case. No `data/qp-topics/` read. Not a mis-provisioned decided case.

## Big case

My independent read, formed before reading any candidate's score, is 0.35: a genuine but narrow statutory question in foreign-expropriation litigation, interlocutory, no amici, resolved by a bare denial. The candidate's own score is recorded on its prediction; no agreement number is computed here.

## Blind

Graded from `record/blinded/claude-baseline/` only. The alias is the only identity used anywhere in this cell's output.
