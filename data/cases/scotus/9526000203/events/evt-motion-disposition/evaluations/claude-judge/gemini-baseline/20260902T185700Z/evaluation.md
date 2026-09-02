# Evaluation — gemini-baseline, evt-motion-disposition (scotus/9526000203)

This is an **interim** cell (`event.yaml` stage: `interim`): an emergency
application by the Solicitor General to stay the D.C. Circuit's affirmance of a
preliminary injunction against White House ballroom construction. The outcome
is `granted` (`actual_granted` = 1, resolved 2026-08-31, standard basis, with
`interim_signals`: 7 amicus briefs, referred to the Court, response requested).

## Scores

- **correct = 1.** Predicted disposition `granted` matches `actual_disposition`
  `granted` exactly.
- **brier_score = 0.09** — (0.70 − 1)².
- **Baseline and skill are the harness's on an interim cell.** I wrote neither
  `segment_base_rate` nor `brier_skill_score`; `stamp-cell` pools the interim
  baseline from the committed statpack (application Terms strictly before this
  case's Term 2026) and derives the skill from it. For the reader: the
  currently committed statpack's interim table shows Terms 2025 + 2024 =
  296 resolved substantive applications, 31 granted (≈ 10.5%), which clears the
  pre-registered 50-resolved floor, so a stamped rate should exist. The
  candidate quoted 13.3% (30/225) from the statpack as committed at its run
  date (2026-08-20); the difference is ordinary corpus refresh between its run
  and mine, not an error by the candidate. `base_rate_basis` stays null
  structurally — the interim pool is no salience-band product, and this
  prediction froze no band (`context.band` null), the ordinary interim shape.
- **vote_accuracy omitted** — never scored off a merits cell; the prediction
  carried no votes anyway.
- **No semantic grades** — no semantic set is declared on an interim event.
- `claim_scores` is the harness's; nothing here grades the claims block or
  `predicted_reasoning.md`.

## Reasoning quality: 0.55

The rationale is directionally sound but thin — two short paragraphs. On the
plus side: it anchors on the statpack's pooled strictly-prior substantive
grant rate (correct framing and floor check), then adjusts upward on the two
most probative facts — the United States as applicant via the SG in an
executive-power dispute, and the Court's recent receptivity to government
emergency applications — plus the already-fired response request. Those are the
right drivers, and the outcome bore them out.

What holds the score down: there is essentially no engagement with the other
side. No mention of the equities that favored denial (irreversibility of
construction, the panel majority's holding that Congress controls federal
property), no acknowledgment of the mixed/partial-relief risk that the interim
resolver reads denial-first, and no discussion of what would make 0.70 too
high or too low. The analysis reads as a competent single-direction adjustment
rather than a weighed forecast; the calibration is asserted more than argued.

## Leakage: not applicable (forward)

The log's `mode` is `forward` and the cell was genuinely open: prediction
created 2026-08-20, resolution 2026-08-31. I checked for mis-provisioning —
nothing in the log or prose reads this application's own disposition as
already decided. Every call in the log carries `result_capture: unobserved`
(coverage 0.0 — this engine's standing telemetry shape, not a defect), so each
call was graded on its query: a CourtListener docket lookup for 26A203
(returned nothing, per the candidate's own retrieval.md) and one web search
for the pending case, dated 2026-08-20, when no outcome existed. The
candidate's disclosure that its web search surfaced the August 18 amicus
filings is legitimate forward signal and a point for the cell's integrity.

## Big case

My independent read is 0.8 (see `evaluation.json`), formed before consulting
the candidate's `big_case_score`.
