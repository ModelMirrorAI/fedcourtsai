# Evaluation: codex-baseline

## Outcome and score

This cert-stage prediction calls `denied`, matching the supplied outcome resolved October 5, 2026. Correctness is **1**. With `actual_granted = 0`, Brier loss is `(0.003 - 0)^2 = 0.000009`. This result alone does not establish that 0.3% was a calibrated estimate.

## Analysis quality: 0.86

The rationale explains its arrival risk-set anchor and makes case-specific adjustments rather than treating absence of later docket activity as a terminal signal. It distinguishes the petition's asserted procedural exception from an established showing, identifies the absence of a developed conflict, and connects the requested relief to disputed notice, prejudice, transcripts, and record reconstruction. The provisioned petition supports those descriptions. Its explicit caveat that no lower-court-opinion or appendix text was provisioned appropriately limits confidence in its vehicle assessment.

The discussion is more discriminating than a categorical dismissal of all domestic-relations petitions: it engages the cited reviewability theory while identifying why this petition may not substantiate it. However, the exact reduction to 0.3% is not quantitatively supported by matched priors. The asserted authority research is described in the retrieval note but not independently verifiable from individual authority calls in the supplied log. I grade the quality of the argument as presented, without treating that report as verification of the authorities' full holdings. The denial confirms the predicted label, not the rationale as the Court's actual reasoning.

## Baseline and scoring boundaries

Frozen context records `baseline`, `sal-v3`, Term 2026. The committed statpack's segment heading is `sal-v4`, so the rate and skill score must be omitted and the basis left null. The cell flags record the mismatch. The current differently versioned table cannot substantiate the historical 863/13,163 calculation; no terminal fallback is permissible for this frozen band.

The forecast document and quantitative claim explanations are excluded from the quality grade. The harness computes claim scores. No semantic grading or vote accuracy applies on this cert cell.

## Leakage

The logged mode is forward; the prediction and visible calls date to August 16, before the October 5 resolution. Recorded-call result coverage is 1.0, but this does not establish completeness of all reported research: the retrieval note's general authority searches are not individually logged here. Neither the visible queries nor the prose indicates retrieval of this case's eventual outcome. Redaction markers are not substantive evidence. A file-listing query expressly excludes the prohibited labeling directory; it is not a read of its contents. Influence is `not_applicable`, with no supported leakage exclusion.
