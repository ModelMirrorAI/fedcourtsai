# Evaluation: claude-baseline — scotus/73500216, evt-petition-disposition

## Cell and outcome

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`), forward mode. The petition (No. 25-1316, Pearson v. Guerrero) was distributed once, for the 2026-09-28 long conference, and **denied on 2026-10-05** with no noted dissent (`actual_disposition: denied`, `actual_granted: 0`, `distribution_count: 1`).

## Scores

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.02 − 0)² = 0.0004.
- `segment_base_rate` = 0.0512, `base_rate_basis` = `risk_set`. The prediction's frozen context carries `band: baseline` **and** `salience_version: sal-v4`, matching the heading of the committed statpack's "Segment base rate by salience band" table, so the bracketed `reached` figure applies. Pooled resolved-weighted over the rendered Terms strictly before Term 2025 (OT2017–OT2024): 592.9 / 11,580 ≈ 0.0512. The caption renders 10 of 10 Terms, so no window divergence.
- `brier_skill_score` = 1 − 0.0004 / 0.0512² ≈ 0.8474.
- `vote_accuracy`, `judgment_correct`, `semantic_grades`: omitted — cert stage.

## Reasoning quality: 0.86

A strong rationale with the right anchor and a well-ordered set of adjustments. The base-rate step is correct: `baseline` band, `sal-v4` matching the table heading, bracketed `reached` figure pooled over OT2017–OT2024, about 5.1%, with the relist-0 and CA5 cuts explicitly labeled shape rather than anchor.

The adjustments are accurate on the record I hold. The AEDPA point is made with the right texture: the Fifth Circuit assumed arguendo that implied bias is clearly established and held these facts outside the "extreme genre" (petition Appendix A, which I checked), and the candidate's observation that the petition itself never engages section 2254(d) is correct — the petition body mentions the statute only in its jurisdiction statement, and every AEDPA discussion in the staged text sits in the appended opinions. The no-response point is read correctly from the docket (response due 2026-06-29, no waiver, no brief, no counsel of record listed, no call for a response) and labeled as inference where it is one. The split-quality and facts paragraphs engage the petition's own cases rather than its headline: the voluntary disclosure, the "thought she could be fair" statement, counsel not hearing the note, and the Strickland layer of deference. The unpublished opinion, private counsel, and absence of amici are weighed. The upward counterweights are named. The uncertainty section is candid about what the candidate could not see.

Deductions: the prose asserts that the Court "almost never grants without a response on file" and that "a grant path requires a call for a response first" as if settled, without a source; it is the Court's ordinary practice but is stated more flatly than the record supports. The live docket confirmation added nothing the snapshot did not already hold, though it was legitimate in forward mode and honestly reported. The relist-hazard reasoning blends a CFR path and a bare relist into a single 0.12 by rough addition; that is a claims-side matter the harness scores, so it does not enter this number, but the rationale's calibration step is less transparent than its legal analysis.

## Leakage

`mode: forward`, `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`. Prediction created 2026-09-17 against a snapshot ending at the 2026-07-15 distribution; the conference was eleven days away. The log (23 calls, `result_capture_coverage` 1.0) shows provisioned record reads, two corpus queries (`retrieved_doc_date` 2026-09-16, returning recency-ranked applications and unrelated dockets), a CourtListener `get_endpoint_item` on this docket (`retrieved_doc_date` 2026-05-28, `date_terminated` null), a docket-entries call returning nothing, an opinion search for "implied bias" juror, and one `web-fetch` of this case's live supremecourt.gov docket page on 2026-09-17, which the candidate reports entry-for-entry identical to the snapshot. Every retrieved date precedes the 2026-09-28 conference and the 2026-10-05 denial, so none of it is outcome material; reading an open case's live docket is the ordinary forward shape, and the candidate's `retrieval.md` disclosed it, which is a point for the cell. No `data/qp-topics/` path appears. Not a mis-provisioned decided case.

## Big case

My own read is 0.22 (see `big_case.notes`). The predictors' scores sat inside the staged `prediction.json`, which I had read before writing mine down, so the independence of this read is partial.
