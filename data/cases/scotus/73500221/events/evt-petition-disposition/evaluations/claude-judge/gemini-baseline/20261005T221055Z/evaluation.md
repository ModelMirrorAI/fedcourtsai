# Evaluation: gemini-baseline — scotus/73500221, evt-petition-disposition

## Outcome and scoring

The petition (No. 25-1320, *Rogne v. City of Catoosa*) was **denied** on the
October 5, 2026 order list following the September 28 long conference, after one
distribution, with no response requested, no CVSG, and no noted dissent.

- **Cell:** cert stage, forward mode (prediction created 2026-09-17 against the
  2026-09-17 snapshot; the conference was still eleven days away).
- **correct = 1.** Predicted `denied`; actual `denied`.
- **brier_score = 0.0001.** P(grant) 0.01 against `actual_granted` 0.
- **segment_base_rate = 0.0512, basis `risk_set`.** The prediction froze
  `band: baseline` under `salience_version: sal-v4`, and the statpack's "Segment
  base rate by salience band" heading names `sal-v4`, so the bracketed `reached`
  figures apply. Pooled resolved-weighted over the rendered Terms strictly before
  the case's Term (2025), i.e. OT2017–OT2024: per-Term reached rates 4.5%–5.9%
  on n = 1643, 1524, 1399, 1739, 1500, 1192, 1312, 1271, pooling to about 593 /
  11,580 = 5.12%. The table caption renders 10 of 10 Terms, so the rendered
  window is the pack's window and no lookback divergence arises.
- **brier_skill_score = 0.9619.** 1 − 0.0001 / 0.0512².
- **vote_accuracy** omitted (cert stage). No `semantic_grades` block (no semantic
  set is declared on a cert event). `claim_scores` left to the harness.

## Reasoning quality: 0.58

The rationale anchors on the right figure (the ~5.1% prior-Term baseline-band
reached rate) and adjusts downward for three real signals: the City's waiver of
response, a vehicle problem rooted in state-law treatment of the earlier state
adjudication, and a purely local dispute with no split. Each of those is sound
and each was borne out by a routine denial.

What holds the score down:

- **Thin engagement with the record.** The document is a single paragraph of
  conclusions. It does not say what the petition actually argues, does not
  identify the dispositive question as the Oklahoma savings statute's
  "otherwise than on the merits" element, and labels the Tenth Circuit's ground
  as "res judicata / issue preclusion" with the hedge "appears to" — the panel's
  stated ground was limitations, with the savings statute turning on how the
  state judgment is characterized. The practical conclusion (state-law
  entanglement makes a poor vehicle) survives, but the doctrinal label is
  imprecise and the hedge suggests the lower-court order was not read.
- **The dissent-from-denial reasoning is weak.** Fifteen percent for a separate
  writing rests on "Justices Thomas and Gorsuch have occasionally written
  separately" on takings, a generic observation that does not engage with this
  petition's shape (unpublished order below, waiver, no amicus, no split). The
  claim itself is scored in code and not here; what counts here is that the
  justification offered does not support the number.
- **Retrieval went unreported in substance.** `retrieval.md` says a CourtListener
  search for the Tenth Circuit opinion was run but never says what it returned,
  and the reasoning does not use anything from it.

The number was right and the direction of every adjustment was right; the
analysis is correct but shallow, and one of its three legs is mislabeled.

## Leakage

Forward cell, `influenced_prediction = not_applicable`, `leakage_suspected =
false`, `retrieved_outcome_material = false`. The log's 29 calls all carry
`result_capture: unobserved` (coverage 0.0 — this engine's standing shape), so
each was graded on its query: corpus queries bounded by `--decided-before
2026-09-17`, two caption searches on CourtListener, statpack reads. Nothing is
dated at or after the resolution, nothing names `data/qp-topics/`, and the prose
treats the conference as upcoming. Not a mis-provisioned decided case: the
denial postdates the prediction by eighteen days.

## Big case

My independent read is 0.08 (see `big_case.notes`): a fact-bound local takings
dispute with no split and an unpublished order below, denied without comment.
The predictors' `big_case_score` values were visible in the staged
`prediction.json` before I wrote mine; I note that rather than claim a blind read.
