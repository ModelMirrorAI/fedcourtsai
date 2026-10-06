# Evaluation: claude-baseline — scotus/73280412, evt-petition-disposition

**Outcome.** Cert stage. On October 5, 2026 the Court granted the petition, vacated the Ninth Circuit's judgment, and remanded for further consideration in light of *Louisiana v. Callais*, 608 U.S. 85 (2026): `actual_disposition = gvr`, `actual_granted = 1`, after three distributions and no CVSG.

**Prediction.** `predicted_disposition = gvr`, `probability = 0.60`, `granted = 1`.

## Scores

| Field | Value | Basis |
| --- | --- | --- |
| `correct` | 1 | exact label match, `gvr` against `gvr` |
| `brier_score` | 0.16 | (0.60 − 1)² |
| `segment_base_rate` | 0.3495 | `high` band, `sal-v4`, risk-set basis (below) |
| `brier_skill_score` | 0.6219 | 1 − 0.16 / (0.3495 − 1)² |
| `reasoning_quality` | 0.84 | see below |

**Base rate.** The prediction's frozen context carries `band = high` **and** `salience_version = sal-v4`, and the statpack's "Segment base rate by salience band" table is headed `sal-v4`, so the basis is `risk_set`. I pooled the bracketed `reached` figures for `high`, resolved-weighted, over the eight rendered Terms strictly before this case's Term (OT2025): OT2017–OT2024, n = 898, giving 0.3495 from the rendered percentages (the unrounded `statpack.json` fields give 314/898 = 0.3497; the difference is immaterial). The table renders 10 of 10 Terms, so the rendered window and the in-code ten-Term lookback coincide and no window divergence needs flagging. OT2025 and OT2026 are excluded.

## What the reasoning got right

- **The decisive signal, found and weighed correctly.** The predictor fetched the State's June 2 brief in opposition (not provisioned) and read that Washington asked the Court to GVR this petition alongside *Soto Palmer*/*Trevino* in light of *Callais*, with no party opposing vacatur. It identified a respondent-endorsed GVR as the strongest single predictor of a grant-family outcome, which is exactly what happened.
- **Correct anchor and correct handling of the distribution count.** It anchored on the `high` band's bracketed rate pooled over OT2017–OT2024 (about 35%, matching my figure) and declined to read the three distributions as two substantive relists, because the calendar shows a reschedule and a response request rather than conference-to-conference relists. Both reads are right.
- **Legitimate forward context, used as such.** *Callais* (April 29, 2026) and the Court's post-*Callais* GVRs of Section 2 judgments were public before the September 16 snapshot and are exactly the kind of forward signal the doctrine permits.
- **Honest about the downside.** The reasoning composed its number explicitly through the *Trevino* intervenor-standing objection (P(Trevino grant family) ≈ 0.65, P(Garcia grant | Trevino GVR) ≈ 0.85, P(Garcia grant | Trevino denied) ≈ 0.12, composing to ≈ 0.59) and stated where to discount it. That is a model of how a hedge should be written.

## Where it was weaker

- **The hedge was probably too heavy.** With a respondent asking for the GVR, no opposition to vacatur, the Court already GVRing Section 2 judgments after *Callais*, and the mootness holding below resting entirely on the *Soto Palmer* judgment, 0.60 leaves a lot of mass on an outcome (denial of both petitions on the standing objection) the Court had shown little appetite for. The reasoning itself anticipated this: it said the forecast leaned on the Court following the respondent's request and would be "badly wrong" otherwise. The direction and label were right; the confidence was conservative.
- The P(Trevino denied) leg treated an intervenor-standing objection pressed in a brief in opposition as roughly a one-in-three event, without much argument for why the Court would reach it rather than GVR past it, which is the usual pattern for a GVR in light of an intervening decision.

Neither weakness is an error of law or fact. `reasoning_quality` is 0.84: a thorough, correctly anchored, correctly sourced analysis whose only real fault is under-confidence in a signal it had itself identified as dominant.

## Leakage

Forward cell (`mode = forward` in the captured log). The prediction was created 2026-09-16; the event resolved 2026-10-05. The log's 33 calls are all timestamped September 16 and include the docket page for 25-901 (reported as matching the snapshot, no entry after June 17), the two briefs, the companion 25-918 docket and filings, two web searches, one CourtListener search (0 results) and two corpus queries (latest `retrieved_doc_date` 2026-09-10). Nothing in the log or the prose reads this petition's disposition, which did not yet exist. No `data/qp-topics/` read. `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, `leakage_suspected = false`. The candidate's `flags.json` is not staged, so its own disclosures reach me only through `reasoning.md` and `retrieval.md`; both are explicit about what was fetched and why.

## Big case

My own read, formed before reading the candidate's: 0.35 (see `evaluation.json`). The candidate's 0.40 is in the same neighbourhood; I record no agreement number.

## Not scored here

`claim_scores` is the harness's. The forecast document (`predicted_reasoning.md`) was read for context only; it is not scored. No `semantic_grades` block: this is a cert cell, no semantic set is declared, and the prediction carries no `semantic_claims`. No `vote_accuracy`: cert stage.
