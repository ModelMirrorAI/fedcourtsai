# Evaluation of claude-baseline — scotus/73500232, evt-petition-disposition

**Cell.** Cert stage (`event.yaml`: `stage: cert`, `moment: distribution`), forward mode. Outcome: petition **denied** on the 2026-10-05 order list after a single distribution to the 2026-09-28 long conference, no response filed, no noted dissent (`actual_granted = 0`, `disposition_basis: standard`).

## Scores

| field | value | how |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition: denied` matches `actual_disposition: denied` |
| `brier_score` | 0.000036 | (0.006 − 0)² |
| `segment_base_rate` | 0.0512 | sal-v4 `baseline` band, bracketed `reached` figure pooled resolved-weighted over Terms 2017–2024 (≈593 grants / 11,580) |
| `base_rate_basis` | `risk_set` | the prediction froze `band: baseline` **and** `salience_version: sal-v4`; the statpack table heading is sal-v4 |
| `brier_skill_score` | 0.9863 | 1 − 0.000036 / 0.0512² |
| `reasoning_quality` | 0.88 | below |

**Base-rate window.** The case's Term is 2025 (`context.term`, docket 25-1331). The sal-v4 table renders Terms 2017–2026 ("Most recent 10 of 10 Term(s)"), so the strictly-prior rows available are 2017–2024, eight Terms. That is narrower than the configured ten-Term in-code lookback, but the caption says the rendered window is the whole pack, so there is no rendered-vs-held divergence to flag; the eight-Term pool is the only one computable from the committed surface. The 2025 row is the case's own Term and is excluded.

## What the prediction got right

- **The anchor.** claude-baseline pooled the same sal-v4 baseline bracketed figure over the same eight Terms and reached the same 5.1%, and explicitly identified it as the yardstick the evaluator scores against. This is the pre-registered anchor, used correctly, with the cross-checks (0-relist paid cut, CA3 cut, no-CVSG cut) correctly labelled as whole-segment or terminal cuts rather than substituted for it.
- **The vehicle analysis is accurate on the record.** Pro se petitioners (petition signature block). All four questions presented ask whether discretion was abused on this record; Rule 10 error-correction framing is correct. The "circuit split" in QP 3 is correctly dismantled: *Deloach* is an E.D. Mo. district-court decision cited as an Eighth Circuit position, *Advanced Estimating* is an unpublished 1996 Eleventh Circuit decision, and every circuit applies *Pioneer*'s factors. The Third Circuit decision is unpublished per the petition's own Opinions Below. The Rule 58 argument is correctly read as an alternative timeliness theory with no showing of preservation.
- **Docket signals read correctly.** One distribution, no brief in opposition, no amici, no CVSG possible. The inference that distribution after the response deadline with no BIO means the respondent did not respond is sound Clerk's-office practice.
- **Calibration against the outcome.** 0.006 against a denial with no separate writing is a well-placed number: far below the anchor for stated, record-grounded reasons, but not driven to a floor the evidence could not support. The forecast's companion numbers (8% relist, 1% dissent-from-denial) are not graded here, but the docket resolved without either.
- **Candour.** The rationale says where its largest adjustment (pro se) rests on general knowledge rather than a committed cut and asks to be discounted for it; it reports the CourtListener 429 and that the opinion below was not read; it states where a different reading of the opinion below would move it and by how much.

## Where it is weaker

- The pro se discount is the dominant move and the statpack publishes no cut for it; the predictor says so, which is the right handling, but the number remains judgment rather than a measured rate.
- On QP 4 the rationale stops at preservation. The sharper point, that FRCP 58(a)(5) excepts an order disposing of a Rule 60 motion from the separate-document requirement, so the 150-day theory fails on the petition's own description of the June 4, 2024 order, was available from the rule text and would have closed the question rather than deferring it.
- The 50% conditional summary-disposition share is argued from a segment-wide GVR/grant ratio and then raised on intuition; the reasoning is coherent but the move from a third to a half is not grounded in a cut.

## `reasoning_quality` = 0.88

A complete, record-grounded analysis that uses the registered anchor correctly, engages the petition's actual arguments and shows why each fails as a cert vehicle, reads the docket signals right, and discloses its own weak points. Marked down modestly for the un-measured size of the pro se adjustment and for leaving the Rule 58 question half-answered.

## Leakage

Mode `forward`; `retrieved_outcome_material: false`; `influenced_prediction: not_applicable`; `leakage_suspected: false`. The prediction was made 2026-09-17, eleven days before the conference; no disposition existed to retrieve. The one case-specific tool call sought the Third Circuit opinion below and was throttled; the corpus query sought granted priors generally. No own-docket query past the prediction date, no post-resolution document date, no `data/qp-topics/` read. Not a mis-provisioned decided case: the predictor's snapshot (2026-09-17) ends at the distribution entry.

## Big-case read

`evaluator_score` 0.03. One household's property in a decade-long foreclosure fight, a two-day-late notice of appeal, an unpublished abuse-of-discretion affirmance, denied without comment. The predictors' own scores were visible in the staged `prediction.json` before this read was fixed, so independence is by discipline rather than by sequence.
