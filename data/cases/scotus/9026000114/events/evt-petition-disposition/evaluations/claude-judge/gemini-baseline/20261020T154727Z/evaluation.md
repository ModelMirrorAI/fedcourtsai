# Evaluation — gemini-baseline

## Cell

Cert-stage, forward cell: *Allen v. Stein* (scotus/9026000114), `evt-petition-disposition`. Outcome: **denied** on 2026-10-19 (`actual_granted` 0), two distributions, no CVSG, no noted dissent from denial. The prediction froze `context.band` = `elevated` under `sal-v4` (Term 2026), so the segment base rate, `base_rate_basis` and Brier skill are the harness's risk-set stamp; I left them null and quote no rate of my own. Where comparison matters, read it against the stamped segment base rate. `correct` and `brier_score` below are my elicited reads, which the stamp recomputes and compares.

No semantic block applies (cert stage); votes are not scored at cert.

## Scores

- Predicted `denied`, P(grant) = 0.25 → **correct = 1**, **Brier = 0.0625**.

## Reasoning quality: 0.55

Right call, but the weakest calibration of the three. The rationale correctly anchors on the elevated band (~17%) and identifies the real points: the response requested after a waiver, the pleaded 8-3-2 split over *Swint*, and the BIO's position that the split is illusory and the decision below a misapplication. It then moves **up** to 0.25 on the response request and the "explicitly quantified" split. That double-counts: the response request is largely what produced the elevated band in the first place. It also takes the petition's split count largely at face value. It names the decisive uncertainty (genuine departure from *Swint* vs fact-bound misapplication) without weighing it, and the Court's denial is consistent with that reading. The rationale is brief and does not engage the vehicle problems (prior trip to the Court, Rule 60 reopening posture) or the absence of amici.

## Leakage

Forward; `not_applicable`. The log is all-unobserved (result capture 0.0), so I graded each call on its query. All are reads of the provisioned record, the contract, and `metrics/statpack.md`. No external retrieval, and nothing about this petition's disposition.
