# Evaluation: claude-baseline — Zook v. Fuqua, No. 25-1108 (scotus/73281401), evt-petition-disposition

## Outcome and headline scores

The petition was **denied** on the 2026-10-05 order list after the 2026-09-28 long conference, with no noted dissent (`outcome.json`: `actual_disposition` denied, `actual_granted` 0, `distribution_count` 2, `noted_dissent_from_denial` false). Cert-stage cell (`event.yaml` stage `cert`).

- `correct` = 1: `predicted_disposition` denied matches the outcome label exactly.
- `brier_score` = (0.10 − 0)² = **0.0100**.
- `segment_base_rate` = **0.1724**, basis `risk_set`. The frozen context carries band `elevated` under `sal-v4`, the same version the statpack's "Segment base rate by salience band (sal-v4)" heading names, so the bracketed `reached` figure applies. Pooled resolved-weighted over the rendered Terms strictly before Term 2025 (OT2017–OT2024; the caption renders 10 of 10 Terms, so no window divergence): 17.9% (n=336), 17.5% (354), 19.0% (300), 20.5% (342), 16.1% (397), 13.8% (334), 15.9% (347), 17.5% (400) → 484.4 / 2810 = 0.1724. Baseline Brier 0.0297.
- `brier_skill_score` = 1 − 0.0100 / 0.0297 = **0.6635**. The best skill of the three candidates on this cell.
- No `vote_accuracy`, no `semantic_grades`: cert stage. `claim_scores` is the harness's.

## What the prediction got right and wrong

Right: the disposition, the timing (denial on the October 5 order list off the long conference, stated in the forecast document, which I read for context only), and the mechanism. The candidate's central reading, that the second distribution was not a relist because the May 15 response request removed the petition from the May 21 conference, so the petition was functionally at its first conference with an `elevated` band "carrying a call-for-response signal dressed as a relist", is exactly what the docket shows and is the sharpest account of the salience signal among the three candidates. Its vehicle reading (the Tenth Circuit's alternative holding at slip op. 15, verified against the opinion text) and its observation that Questions 2 and 3 depend on Question 1 both survive the outcome.

Wrong or weak: nothing material. The candidate itself names where to discount it (it could not see what prompted the call for response), and that uncertainty is appropriately priced rather than ignored.

## Reasoning quality: 0.88

`reasoning.md` is the strongest of the three. It anchors correctly (bracketed reached, elevated, sal-v4, OT2017–OT2024, 17.2% n=2810, with a shorter-window check at 18.1%) and cross-checks against the terminal relist cut. It then gives five numbered, independently checkable reasons to move down, each tied to a specific source: the docket sequence; the opinion below (alternative holding and its distinctions of *Bailey*, *Saalim*, *Chrestman*, read via search_document); the shape of the split; the dependence of Questions 2 and 3 on Question 1; and the absence of amicus support, the non-specialist counsel of record, the missing reply, and the amended complaint reported in the BIO. It balances this with a "why I do not go lower" section (call for response after waiver, published dissent by a former chief judge, the Court's history of summary intervention in this genre), so the 10% is a net of weighed considerations rather than a one-sided case. The uncertainty section is candid, including that its two corpus queries returned nothing useful and did not move the number.

What keeps it from higher: the claim that "most modern grants follow a relist" is asserted rather than tied to a pack figure, and the "non-specialist counsel" point is a soft heuristic stated more confidently than the evidence supports. Minor. The forecast document and the claims block were not graded.

## Leakage: forward, not applicable

Mode `forward` per `retrieval_log.json`. The prediction was created 2026-09-17 against the 2026-09-17 snapshot, eighteen days before the denial, so no outcome existed to leak. Checked anyway: 35 logged calls, capture coverage 1.0. The two `fedcourts query` calls (a Garner citation lookup returning no rows, a recency-ranked granted pull returning aggregate shape) carry nothing about this case. The CourtListener `get_endpoint_item` fetch of this docket's record carries `retrieved_doc_date` 2026-03-23 (the filing date) and the candidate reports it was last modified 2026-07-29 with no entries beyond the snapshot, which is pre-resolution and disclosed in `retrieval.md`; the opinion search carries 2025-11-04. No `retrieved_doc_date` on or after 2026-10-05, no `data/qp-topics/` read. `retrieved_outcome_material` false, `influenced_prediction` not_applicable, `leakage_suspected` false.

## Big-case read: 0.30

Formed from the record and outcome before weighing the candidate's score. A paid Section 1983 petition from county deputies with a recurring procedural question (video at Rule 12(b)(6)) and a claimed circuit split, but no amicus support, non-specialist counsel, a fact-bound shooting, an alternative holding below, and a silent denial. Moderate-low stakes. The candidate's own score is not graded here.
