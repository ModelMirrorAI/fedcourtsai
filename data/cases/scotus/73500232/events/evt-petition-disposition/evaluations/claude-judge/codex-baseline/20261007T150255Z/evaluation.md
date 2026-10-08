# Evaluation of codex-baseline — scotus/73500232, evt-petition-disposition

**Cell.** Cert stage (`event.yaml`: `stage: cert`, `moment: distribution`), forward mode. Outcome: petition **denied** on the 2026-10-05 order list after a single distribution to the 2026-09-28 long conference, no response filed, no noted dissent (`actual_granted = 0`, `disposition_basis: standard`).

## Scores

| field | value | how |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition: denied` matches `actual_disposition: denied` |
| `brier_score` | 0.000064 | (0.008 − 0)² |
| `segment_base_rate` | 0.0512 | sal-v4 `baseline` band, bracketed `reached` figure pooled resolved-weighted over Terms 2017–2024 (≈593 grants / 11,580) |
| `base_rate_basis` | `risk_set` | the prediction froze `band: baseline` **and** `salience_version: sal-v4`; the statpack table heading is sal-v4 |
| `brier_skill_score` | 0.9756 | 1 − 0.000064 / 0.0512² |
| `reasoning_quality` | 0.85 | below |

**Base-rate window.** Case Term 2025; the sal-v4 table renders 2017–2026 ("Most recent 10 of 10 Term(s)"), so the strictly-prior pool is 2017–2024, eight Terms, the whole rendered pack. No rendered-vs-held divergence to flag.

## What the prediction got right

- **The anchor.** codex-baseline pooled the sal-v4 baseline bracketed `reached` figures over 2017–2024 to 5.12% on a weighted denominator of 11,580, matching the evaluator's computation, correctly excluded the case's own Term and the empty 2026 row, and said the figure is approximate because it reconstructs from rounded percentages. It correctly declined to substitute the modern-cert disposition count (a mixed population) for the selected anchor, and used the frozen `context.term` rather than the calendar year.
- **The sharpest legal point of the three.** On QP 4 the rationale observes that FRCP 58(a)(5) excepts an order disposing of a Rule 60 motion from the separate-document requirement, so the petition's 150-day theory does not follow from its own description of the June 4, 2024 order. The predictor verified this against the rule text (fetched from Cornell LII) rather than from memory, and labelled it an inference about vehicle weakness rather than a verified holding below. That is exactly how a cert analyst should handle a question presented that is defective on its face.
- **Vehicle analysis otherwise accurate.** QPs 1 and 2 as error-correction; the opinion below unpublished per the petition; the asserted split not cleanly demonstrated and resting partly on a district-court decision (*Deloach*) cited as an Eighth Circuit position; the Third Circuit's own holistic-balancing cases making an intracircuit application dispute plausible; the petition's concealment and no-prejudice assertions treated as contentions rather than facts.
- **Methodologically careful about conditioning.** Relist and CVSG cuts correctly described as terminal buckets rather than forward hazards; the one distribution correctly read as the initial conference distribution, not a relist; the silence on a response correctly not inflated into a formal waiver or any stronger inference.
- **Calibration.** 0.008 against a denial is well placed: a stated reason for every step down from the anchor and a stated reason for the residual.

## Where it is weaker

- The rationale says "the event has no explicit stage or moment"; the committed `event.yaml` carries `stage: cert` and `moment: distribution`. The predictor reached the right contract anyway, so nothing turned on it, but it is a misstatement about an input it read.
- The 25% conditional summary-disposition share is asserted rather than grounded in a cut, and the 0.18 stakes score is generous for a pro se, fact-bound, unpublished-affirmance petition (the stakes score is graded elsewhere, not here, but the rationale's one-sentence defence of it is thin).
- The petition's pro se status, the most visible feature of the filing, is not named anywhere in the rationale as a factor, even though its adjustments plainly presuppose it.
- The forecast's companion numbers (7% relist, 1% denial writing) are not graded here; the docket resolved without either.

## `reasoning_quality` = 0.85

A rigorous, correctly anchored, record-grounded analysis with the best single legal insight of the three (Rule 58(a)(5)) and careful handling of terminal-versus-forward conditioning. Marked down modestly for the mis-description of the event file, for not naming the pro se feature its adjustments rest on, and for conditional numbers asserted without a basis.

## Leakage

Mode `forward`; `retrieved_outcome_material: false`; `influenced_prediction: not_applicable`; `leakage_suspected: false`. Prediction made 2026-09-17, before the 2026-09-28 conference. Log capture coverage 0.93. The one case-specific call is a CourtListener opinion search for Third Circuit docket 24-2794 bounded `filed_before 2025-10-02`, seeking only the pre-petition decision below (zero results). Two unobserved web searches and two shell fetches target Cornell LII rule text for FRCP 58 and FRAP 4, general authority with no case content. No own-docket query, no post-resolution document date, no `data/qp-topics/` read. Not a mis-provisioned decided case: the snapshot the cell read (2026-09-17) ends at the distribution entry.

## Big-case read

`evaluator_score` 0.03. One household's property in a decade-long foreclosure fight, a two-day-late notice of appeal, an unpublished abuse-of-discretion affirmance, denied without comment. The predictors' own scores were visible in the staged `prediction.json` before this read was fixed, so independence is by discipline rather than by sequence.
