# Evaluation: codex-baseline — evt-petition-disposition (scotus/73129750)

## Outcome and scores

Cert-stage cell (kind `petition`, no recorded stage). Realized outcome:
`granted` (certiorari before judgment granted 2025-12-05, `actual_granted` = 1).
The candidate predicted `granted` at p = 0.88, so `correct` = 1 and
`brier_score` = (0.88 − 1)² = 0.0144. No votes were predicted and the outcome
records none, so `vote_accuracy` is null.

**Base rate.** The prediction carries no frozen `context` block (an older-shape
record), so per the fallback rule I derived the band now and used the table's
*leading* (terminal) figure, recording `base_rate_basis` = `terminal`. The
terminal band is `federal` (sal-v2; the cell's own `record/context.json`
confirms it, and the SG-as-petitioner posture makes it unambiguous). Pooling
the statpack's "Segment base rate by salience band" leading figures
resolved-weighted over Terms strictly before 2025 (2017–2024; the caption
renders 9 of 9 Terms, so the rendered window is the full pack and matches the
configured 10-Term lookback — no window divergence to flag) gives
113.0/160 ≈ **0.7063**. `brier_skill_score` = 1 − 0.0144/(1 − 0.7063)² ≈
**0.833**.

## Leakage

The cell ran `forward` per its retrieval log, but this is a mis-provisioned
forward cell: the event resolved 2025-12-05 and the run is 2026-07-14, and the
provisioned snapshot contained the grant and the later argument and merits
entries. The candidate retrieved nothing external — its log shows only local
reads of the snapshot, the provisioned brief in opposition, the statpack, and
repo schemas — but it read the disposition off the provisioned snapshot and
says so plainly, in a dedicated leakage notice. It framed 0.88 as a
counterfactual estimate from the pre-disposition record only. That disclosure
is a point for the cell's integrity, but the outcome was known when the number
was formed, so `influenced_prediction` is graded `likely` (the reasoning admits
knowing the outcome); the notes record the mitigating counterfactual framing.
This cell should not be treated as forward forecasting signal.

## Reasoning quality: 0.90

Strong work under contaminated conditions. The document identifies the correct
decision standard (Rule 10 discretion plus Rule 11's imperative-public-importance
bar for cert before judgment), inventories the grant-side signals accurately
(SG petitioner, the Court's prior engagement in Trump v. CASA, the companion
Trump v. Washington vehicle, the single relist from the 11/21 to the 12/5
conference), and — unusually and creditably — weighs real denial-side
considerations (no circuit split, the independent § 1401(a) statutory ground,
the extraordinary posture of cert before judgment). It anchors on the statpack
(3.3% modern grant rate, 7.8% one-relist bucket) and explains the departure.
It declined to predict per-Justice cert votes with a sound justification
(cert votes are unrecorded, and merits alignments in the contaminated snapshot
are not a proxy). It also candidly noted the missing petition text and worked
from the BIO's characterization rather than inventing content. The residual
12% denial mass is defensible for a counterfactual; if anything slightly
conservative given the signal stack, which is a minor calibration quibble, not
an analytical flaw. Docked modestly only because the counterfactual number is
formed with the outcome known, which caps how much the calibration reasoning
can be credited as blind.
