# Evaluation — codex-baseline, scotus/73500245, evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`). The petition in *Blevins v. Alabama State Bar*, No. 25-1344, was distributed once (July 8, 2026, for the September 28, 2026 conference) and **denied on October 5, 2026** without a noted dissent (`outcome.json`: `actual_disposition` denied, `actual_granted` 0, `distribution_count` 1).

- `predicted_disposition` denied vs actual denied → **correct = 1**.
- `probability` 0.01 → **brier_score = 0.0001**.
- Base rate: the prediction's frozen context carries `band: baseline` and `salience_version: sal-v4`; the statpack's "Segment base rate by salience band (sal-v4)" heading matches, so the basis is **risk_set**. Pooling the bracketed `reached` figure, resolved-weighted, over every rendered Term strictly before this case's Term 2025 (OT2017–OT2024, the table renders 10 of 10 Terms so the window is complete) gives 593 / 11,580 = **0.0512**. The in-code lookback of ten Terms would reach OT2015, but the pack holds nothing before OT2017, so the two windows coincide and there is no divergence to flag.
- `brier_skill_score` = 1 − 0.0001 / (0.0512 − 0)² = **0.962**.

## Reasoning quality: 0.80

The rationale is careful and well-disciplined. It identifies the anchor correctly (the sal-v4 baseline `reached` rate pooled over OT2017–OT2024, 593/11,580), excludes the case's own Term, and explains why the paid-segment relist and CVSG cuts are terminal-state cuts not to be read as hazards. The downward adjustment is justified on the right grounds: the QP is a challenge to one state court's reading of one state statute, there is no asserted conflict, the petition's own account shows the Alabama court rejecting reasonable reliance, and the federal theory first appeared in a reply brief below, raising a preservation question that the candidate flags without overclaiming a default. It treats the respondent's waiver as a modest signal rather than a dispositive one, treats the petition's descriptions as the petitioner's characterizations rather than established fact, and notices the petition's December 19, 2026 misdating. It also discloses that its web attempts returned nothing and that no legal proposition rests on them.

What keeps it from higher: it did not read the Alabama Supreme Court opinion, which was available on CourtListener, and so missed the strongest vehicle problem in the case — the state court's alternative holding that § 34-3-62 was inapplicable because the Bar prosecuted communication and fee violations rather than wrongful retention, which means a favorable fair-notice ruling would not necessarily disturb the discipline. The analysis of the *Marks* theory is also thin: it correctly calls the dispute "fact-sensitive" but does not say why a *Marks*/*Bouie* fair-notice claim fits poorly outside a criminal or quasi-penal enlargement context. The 1% landing point is reasonable but, given the weakness identified, the residual (an "unusually clear federal fair-notice violation") is more generous than the record supports.

## Leakage

Mode `forward`. The prediction was written September 17, 2026, before the first conference (September 28) and the denial (October 5), so the outcome did not exist to be leaked. The log (24 calls, capture coverage 0.875) shows 21 captured reads of the prompt, schemas, provisioned record, petition and statpack, plus three unobserved web-search calls whose queries concern Supreme Court Rule 10 and the Court's rules pages, not this docket; those are graded on their queries and credited as having returned nothing only on the candidate's own disclosure, not on the log. No CourtListener, corpus or `data/qp-topics/` call. `retrieved_outcome_material` false, `influenced_prediction` not_applicable, `leakage_suspected` false.

## Big case

My independent read is 0.04: one attorney's 180-day suspension, a state-law-framed QP with a thin federal hook, no split, no amici, waived response, routine first-list denial. The candidate's own `big_case_score` sits in the staged `prediction.json` I read for the context block, so I could not form my read before seeing it; it rests on the record and the outcome rather than on the candidate's number.

## Not graded here

The claims block and `predicted_reasoning.md` are harness-scored or unscored by contract. No semantic set is declared on a cert cell, so no `semantic_grades` block is written. `vote_accuracy` is omitted on a cert cell.
