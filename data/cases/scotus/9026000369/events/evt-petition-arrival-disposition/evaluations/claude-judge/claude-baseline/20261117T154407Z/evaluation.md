# Evaluation — claude-baseline, evt-petition-arrival-disposition (scotus/9026000369)

**Cell.** Cert stage, arrival moment: *Loop v. Washington*, No. 26-369. Outcome: petition **denied** on 2026-11-16 after one distribution (conference of 11/13/2026), all respondents having waived; no CVSG, no noted dissent.

**Scores.** Predicted `denied` at P(grant) = 0.006 → `correct` = 1, `brier_score` = 0.000036. No `vote_accuracy` (cert cell). The segment base rate, skill score and claim scores are the harness's to stamp; any comparison is against the stamped segment base rate. No semantic grades (cert cell, no declared set).

## Reasoning (`reasoning_quality` = 0.85)

The call (denied, P(grant) 0.006) was correct and well calibrated for the vehicle. The rationale is the most complete of the cell: it anchors on the frozen band's arrival-population rate and says why it did not substitute the relist-0 terminal cut, then walks down through concrete, petition-grounded vehicle defects — pro se filing, unpublished memorandum below, no alleged split (the petition's own CA9/CA3 citations agree with its rule, so the claim is error correction), independent immunity and sovereign-immunity bars that make a Rooker-Feldman win non-outcome-determinative, QP2 never passed on below, and the just-decided T.M. decision cutting against a hold-and-GVR channel. Each of those is a real cert-stage consideration and correctly weighted. It is candid about limits (it did not read the CA9 memorandum; the statpack has no pro se cut, so the largest adjustment rests on general knowledge). Marks off: it says the appendix was not in the extracted text and so relied on the petition's characterisation of the decision below, and the alternative-grounds point is asserted from the party list rather than from the ruling below. The later arrival of retained counsel and five amicus briefs was not foreseen, but nothing in the arrival record pointed to it and the denial followed anyway.

## Predicted reasoning (`predicted_reasoning_quality` = 0.9)

Central claims: denial without writing; exactly one distribution and no relist; waivers by both respondent groups inside the response window; a late-October/November distribution with denial at the first conference in November or early December; no CVSG, no dissent. All five were borne out against the docket and outcome, and the waiver and timing claims are specific calls a reader of the arrival record could have missed (a response could have been filed or requested; five amicus briefs could have prompted a relist). The conditional content (QP1 over QP2, GVR-over-plenary if granted, the merits note) never came into play and earns neither credit nor penalty. Short of 1.0 only because the headline denial itself was the overwhelmingly likely outcome for this vehicle.

Checked against: Docket (2026-11-16 snapshot): waivers Oct 2 and Oct 8, DISTRIBUTED Oct 28 for Conference of 11/13/2026, 'Petition DENIED' Nov 16.

## Leakage

Mode `forward`; `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. Forward cell, predicted 2026-09-27; event resolved 2026-11-16. Captured log (coverage 1.0, 24 calls): provisioned files, statpack, two fedcourts queries, CourtListener searches for the CA9 memorandum (0 results), the WAWD docket metadata (doc date 2024-05-15) and the T.M. v. Univ. of Md. Medical System opinion (2026-06-18, a different case predating the snapshot). No retrieved date on or after resolution; nothing resolving this petition. The only 'qp-topics' string is a grep -v filter over git status output, which opens no file under that path.

## Big case (evaluator read 0.12)

Paid petition, pro se at filing, from an unpublished CA9 memorandum affirming a Rooker-Feldman dismissal of a section 1983 suit arising from a privately arbitrated parenting plan. QP2 (delegating parental-rights adjudication to a private arbitrator) has some national family-law reach in the abstract and drew five cert-stage amicus briefs plus a later counsel appearance, but it was never reached below; all respondents waived, the petition was distributed once and denied without a writing.
