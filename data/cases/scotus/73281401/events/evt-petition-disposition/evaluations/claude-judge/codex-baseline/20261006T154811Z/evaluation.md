# Evaluation: codex-baseline — Zook v. Fuqua, No. 25-1108 (scotus/73281401), evt-petition-disposition

## Outcome and headline scores

The petition was **denied** on the 2026-10-05 order list after the 2026-09-28 long conference, with no noted dissent (`outcome.json`: `actual_disposition` denied, `actual_granted` 0, `distribution_count` 2, `noted_dissent_from_denial` false). This is a cert-stage cell (`event.yaml` stage `cert`).

- `correct` = 1: `predicted_disposition` denied matches the outcome label exactly.
- `brier_score` = (0.12 − 0)² = **0.0144**.
- `segment_base_rate` = **0.1724**, basis `risk_set`. The prediction's frozen context carries band `elevated` and `salience_version` `sal-v4`, and the statpack's "Segment base rate by salience band (sal-v4)" heading names the same version, so the bracketed `reached` figure applies. Pooled resolved-weighted over the rendered Terms strictly before Term 2025 (OT2017–OT2024; the caption renders 10 of 10 Terms, so the rendered window is the pack's window and no divergence is flagged): 17.9% (n=336), 17.5% (354), 19.0% (300), 20.5% (342), 16.1% (397), 13.8% (334), 15.9% (347), 17.5% (400) → 484.4 / 2810 = 0.1724. Baseline Brier (0.1724)² = 0.0297.
- `brier_skill_score` = 1 − 0.0144 / 0.0297 = **0.5155**. The forecast clearly beat the always-predict-the-band-rate baseline.
- No `vote_accuracy`, no `semantic_grades`: cert stage. `claim_scores` is the harness's.

## What the prediction got right and wrong

Right: the disposition, the direction and roughly the size of the downward move from the band anchor, and the reasons. The three load-bearing observations were each borne out or at least not contradicted by the denial: (1) the second distribution was not a true relist, because a response request on May 15 pulled the petition from the May 21 conference and the July 29 distribution followed the requested BIO; (2) the Tenth Circuit's alternative holding (even under the Sixth Circuit rule the videos do not blatantly contradict the complaint) blunts the vehicle for Question 1; (3) the BIO's report of a third amended complaint weakens the omitted-facts question. The candidate also correctly declined to treat the three questions as three independent chances of review.

Wrong or weak: nothing material against the outcome. At 12% the candidate left a modest residual that a sharper read of the vehicle could have cut further, but the number sits well below the anchor and the complement is correctly treated as mostly denial.

## Reasoning quality: 0.85

`reasoning.md` is a sound forward analysis. It anchors on the right table and the right figure (bracketed reached, elevated, sal-v4, OT2017–OT2024, computed from the pack's JSON as 484/2810), explains why the whole-docket and terminal-relist cuts are not the anchor, and then makes a legally grounded adjustment from primary sources: it read the opinion below (pages 14–16, the alternative holding) and the Eleventh Circuit's *Johnson* opinion to test the split as the petition framed it, rather than taking either side's account. It is honest about what it did not inspect (the videos, the amendment order) and labels its 17.2% → 12% move as judgmental. The treatment of the distribution signal is correct and carefully worded.

What keeps it short of the top: the write-up spends a paragraph on the statpack's commit vintage and on population cuts it then sets aside, and the vehicle discussion, while right, stops at "substantial obstacle" without weighing how routinely the Court treats an alternative holding as disqualifying for a split-resolution grant. The conditional claims are explained but those are the harness's to score and did not enter this number. The forecast document was read for context only and was not graded.

## Leakage: forward, not applicable

Mode `forward` per `retrieval_log.json`. The prediction was created 2026-09-18 against the 2026-09-18 snapshot while the petition was pending for the 2026-09-28 conference, eighteen days before the denial, so no outcome existed to leak. I checked anyway: 44 logged calls (capture coverage 0.93); the CourtListener calls target the 2025-11-04 Tenth Circuit opinion and a 2024 Eleventh Circuit opinion with narrow date filters; the two unobserved web opens target the petitioner's own March 2026 appendix PDF and one unobserved site search targets general authority, all graded on their queries as pre-resolution material; no `retrieved_doc_date` on or after 2026-10-05; no query for this docket's later history; no `data/qp-topics/` read. `retrieved_outcome_material` false, `influenced_prediction` not_applicable, `leakage_suspected` false. The candidate's own retrieval note matches the log.

## Big-case read: 0.30

Formed from the record and outcome before weighing the candidate's score. A paid Section 1983 petition from county deputies with a recurring procedural question (video at Rule 12(b)(6)) and a claimed circuit split, but no amicus support, non-specialist counsel, a fact-bound shooting, an alternative holding below, and a silent denial. Moderate-low stakes. The candidate's own score is not graded here; the panel compares reads by rank at leaderboard time.
