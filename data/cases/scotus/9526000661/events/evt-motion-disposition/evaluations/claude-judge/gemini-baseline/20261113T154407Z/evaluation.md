# Evaluation — gemini-baseline

**Cell:** `scotus/9526000661`, `evt-motion-disposition`, stage **interim** (application 26A661 for a stay of execution, *Pavatt v. Oklahoma*). The outcome carries the finer interim reading (`interim_reading: denied`, `interim_granted: 0`), so the cell is scored against `interim_granted`. The baseline (`segment_base_rate`) and `brier_skill_score` are the harness's on an interim cell and are left null here, as is `base_rate_basis`; `claim_scores` is likewise computed in code.

## Scores

- Predicted `denied` at P(granted) = 0.03; outcome denied. `correct` = 1, `brier_score` = (0.03 − 0)² = 0.0009.
- `vote_accuracy` omitted (not a merits cell). No `semantic_grades` (none declared off merits).

## Reasoning quality — 0.85

The rationale anchors correctly on the interim pool (156/1,337 over OT2016–OT2025) and then on the matching private × capital cell (10/288 = 3.5%); both figures match the committed statpack's applicant-class table. It goes further and reads the per-Term cuts to show the recent rate for private capital applicants is far lower, which is the right direction of adjustment and well evidenced. The legal analysis is the strongest of the three: it identifies why *Peña-Rodriguez* is a poor bridge (the exception was confined to racial animus; a false-argument due-process claim runs on an objective materiality standard that neither needs nor permits juror testimony), and flags the successive post-conviction posture and the possibility of an independent state procedural bar as an unverified downside — the later record summary indicates the state court did rest on a procedural bar. The "why not lower" reasons (the co-defendant's recent summary vacatur; institutional counsel) are modest but reasonable. Minor reservations: staying at 3% when its own recent-Term evidence (1/159) pointed lower is slightly under-argued, and the document is heavier than its content requires. The per-Term cut figures were not independently re-derived by me; the pooled figures were checked against the committed pack.

## Predicted reasoning — 0.9

Central claims: the form and wording of the order (unsigned, "presented to Justice Gorsuch and by him referred to the Court is denied") with a simultaneous denial of certiorari in 26-6095; timing on Nov 11 or the morning of Nov 12; referral to the full Court; no formal call for a response because the State files on its own; no separate writing and no amicus. Every one was borne out by the docket and outcome: the disposing entry of Nov 12 matches the predicted wording almost verbatim and denies certiorari in the same entry, the response arrived uninvited on Nov 9, and there was no writing, noted dissent or amicus. The no-response-call and same-order cert denial are discriminating calls a competent reader could have made otherwise. Held short of 1.0 because each call was the modal capital-stay pattern rather than a contested one, and the conditional merits section (what the Court "will conclude" about the stay standard) cannot be checked against an unexplained order.

## Leakage

Forward mode; predicted 2026-11-09, resolved 2026-11-12. The log's results are `outcome_only`, so calls are graded on their queries: CourtListener searches on the applicant's name reached earlier published decisions and an October 2026 district-court complaint — legitimate forward context on an open case. Nothing shows this application's disposition surfacing as decided. `influenced_prediction: not_applicable`.
