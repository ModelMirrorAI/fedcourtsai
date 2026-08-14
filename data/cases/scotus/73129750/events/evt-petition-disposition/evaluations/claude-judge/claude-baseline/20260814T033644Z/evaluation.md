# Evaluation: claude-baseline — evt-petition-disposition (scotus/73129750)

## Outcome and scores

Cert-stage cell (kind `petition`, no recorded stage). Realized outcome:
`granted` (certiorari before judgment granted 2025-12-05, `actual_granted` = 1).
The candidate predicted `granted` at p = 0.99, so `correct` = 1 and
`brier_score` = (0.99 − 1)² = 0.0001. No votes were predicted and the outcome
records none, so `vote_accuracy` is null.

**Base rate.** The prediction carries no frozen `context` block (an older-shape
record), so per the fallback rule I derived the band now and used the table's
*leading* (terminal) figure, recording `base_rate_basis` = `terminal`. The
terminal band is `federal` (sal-v2). Pooling the leading figures
resolved-weighted over Terms strictly before 2025 (2017–2024; the caption
renders 9 of 9 Terms, so the rendered window is the full pack and matches the
configured 10-Term lookback — no window divergence to flag) gives ≈ **0.7063**.
`brier_skill_score` = 1 − 0.0001/(1 − 0.7063)² ≈ **0.9988**. Both numbers
should be read under the leakage grading below: the near-perfect skill is a
read-off of a leaked outcome, not forecasting.

## Leakage

The cell ran `forward` per its retrieval log, but the event resolved
2025-12-05, seven months before the 2026-07-14 run — a decided case was
provisioned forward. The candidate is the most explicit of the three about
this: it leads with a section documenting that the provisioned snapshot
contains the grant, the argument date, and the June 2026 merits judgment, filed
a data-quality flag (per its reasoning; predictor flags are not staged into the
blinded set), and retrieved nothing external. It then chose to report 0.99 on
the stated ground that the sanctioned input contains the disposition and that
feigned uncertainty would corrupt calibration measurement the other way, while
separately stating what its blind estimate would have been (0.93–0.96).
`influenced_prediction` is `likely` — the headline probability presupposes the
result, by the candidate's own account. The honesty of the disclosure is
credited; the cell still cannot serve as forward signal.

## Reasoning quality: 0.88

The richest factual and doctrinal analysis of the three. It correctly frames
the Rule 11 cert-before-judgment standard, and its counterfactual section is
precise and well-sourced: the D.N.H. classwide injunction, the pending First
Circuit appeal (No. 25-1861), the companion Trump v. Washington petition
(No. 25-364), the BIO's vehicle-focused (not review-resisting) posture, the
Rule 15.5 waiver, the distribution/relist mechanics, petition-stage amicus
volume, and the statpack anchor (~3.3%) with a reasoned departure. Its residual
mass is even allocated sensibly (deny/hold in favor of the companion as lead
vehicle). Two things keep it below codex-baseline: the headline number knowingly
restates the leaked outcome rather than the candidate's own counterfactual
estimate — a defensible, transparently argued choice, but on the forecasting
axis this cell is scored on it substitutes the answer key for the analysis —
and the counterfactual, though excellent, is offered as a secondary exhibit
rather than the deliverable. As pure legal reasoning it is arguably the best
document here, and the 0.88 reflects that quality net of the reporting choice.
