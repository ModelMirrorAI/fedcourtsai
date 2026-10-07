# Evaluation: gemini-baseline — Francis v. Allstate Insurance Co. (scotus/73246321, evt-petition-disposition)

## Outcome and scores

Cert-stage cell. The petition was **denied** on the October 5, 2026 order list
after the September 28 Long Conference, on a single distribution, with no noted
dissent (`actual_disposition: denied`, `actual_granted: 0`).

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.001 − 0)² = 0.000001.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction froze band
  `baseline` under `sal-v4`, matching the statpack table's heading, so the
  bracketed `reached` figure applies, pooled resolved-weighted over the
  rendered Terms strictly before Term 2025 (OT2017–OT2024, n = 11,580): 5.12%.
  The caption renders 10 of 10 Terms, so no lookback divergence arises.
- `brier_skill_score` = 1 − 0.000001 / 0.0512² ≈ 0.9996.

No votes are scored on a cert cell; `vote_accuracy` is omitted. No semantic
set is declared on a cert event, so there is no `semantic_grades` block.

## Reasoning quality: 0.60

The rationale reaches the right answer by the right general route, but it is
thin, and the lowest probability of the three is the least argued.

What it got right:

- **Correct anchor, approximately.** It reads the prior-Term pooled `baseline`
  `reached` rate as "around 5.0%"; the pooled figure is 5.12%, so the anchor is
  in the right place even though the pooling is not shown.
- **Correct doctrinal label.** It names the adequate-and-independent-state-
  ground problem — a state court applying its own procedural rules — as the bar
  to review, and that is the operative reason this petition could not be
  granted.
- **Correct read of the docket posture.** Paid, pro se, respondent waived, one
  distribution, no federal interest for a CVSG, no intervening decision for a
  GVR.

Where I discount:

- **No engagement with the petition's content.** It never mentions the three
  questions presented beyond calling them "case-specific," the single cited
  authority (*Haines v. Kerner*), the absence of any asserted conflict, or the
  fact that the argument section is two paragraphs. The analysis would read the
  same for any pro se procedural-default petition; the petition itself is not
  used as evidence.
- **The waiver is over-read.** "The respondent's waiver signals that the
  petition is not viewed as legally credible or threatening" treats a routine
  respondent choice as a strong signal. A waiver is the default for a weak
  petition and the Court can call for a response; it is directionally
  consistent with denial but is not the evidence the rationale makes it.
- **No calibration reasoning for 0.1%.** The number is a factor of five below
  the two peers' and an order of magnitude below where either explains its
  floor, yet the rationale gives no account of why the residual (a surprise
  hold, a GVR on an unseen intervening decision, an error in the OCR record)
  is this small. It happened to score well because the petition was denied,
  but soundness is about the argument for the number, not its luck.
- **No caveats.** It does not notice the unprovisioned appendix, the OCR
  garbling, the cover-page/docket inconsistency about the court below, or the
  filed/docketed date anomaly — each of which the other two candidates flagged
  and reasoned about.
- `retrieval.md` reports consulting "originating circuits" in the statpack; the
  log's queries show the disposition, salience-band, and relist tables only.
  Minor, but it is a claim about process the log does not support.

The forecast document and the claims block were read for context only and are
not scored here.

## Leakage: not applicable (forward)

The prediction was created 2026-09-16, before the September 28 conference, so
the outcome did not exist to be retrieved. The captured log (25 calls,
`result_capture_coverage` 0.0 — an engine whose telemetry records no results,
which is its standing shape and not a defect) is graded on each call's query:
provisioned inputs, three statpack greps, and one corpus query for three recent
denied SCOTUS rows. No query names this docket or seeks its disposition, and
nothing under `data/qp-topics/` was read. Because no result was captured, I do
not credit the log as showing nothing was found; the finding rests on the
queries having no reach toward the outcome and on the rationale reading as a
pre-decision analysis. `retrieved_outcome_material` = false,
`influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Big-case read: 0.02

An individual's insurance dispute lost on a Georgia procedural default, pro se,
respondent waived, denied on the first conference with no separate writing.
Nothing here reaches beyond the parties. (The predictors' own scores were
visible in the staged `prediction.json` before I recorded this; the read is
mine, but I note the exposure.)
