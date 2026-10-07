# Evaluation — claude-baseline — Fairfield Sentry Ltd. v. Citibank NA London (scotus/73281372, evt-petition-disposition)

## Outcome and scores

The petition was **denied** on the October 5, 2026 order list after its first
distribution (Conference of September 28, 2026): no relist, no CVSG, no noted
dissent; Justice Alito took no part. `actual_granted` = 0.

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.12 − 0)² = **0.0144**.
- `segment_base_rate` = **0.0512**, basis `risk_set`. The prediction froze
  `band: baseline` under `salience_version: sal-v4`; the statpack's segment
  table heading is sal-v4, so the versions match. I pooled the bracketed
  `reached` figure for `baseline`, resolved-weighted over the Terms the table
  renders strictly before the case's Term 2025 (OT2017–OT2024, eight rows):
  592.9 / 11,580 ≈ 5.12%. The caption says the table renders 10 of 10 Terms,
  so the rendered window is the pack's whole window and no window divergence
  arises.
- `brier_skill_score` = 1 − 0.0144 / 0.0512² = **−4.49**. The naive baseline
  forecast (5.1%) would have scored a Brier of 0.0026; a 12% forecast on a
  denied petition does several times worse. The sign is the point: the
  candidate named the right label but priced the grant at more than double
  the band anchor, and the realized outcome was the anchor's modal one.

This is a cert cell, so no `vote_accuracy`, `judgment_correct`,
`semantic_grades`, or `claim_scores` is mine to write.

## Reasoning quality: 0.78

What drove the score up:

- The anchor is handled exactly as the contract asks: bracketed reached
  figure, strictly-prior Terms, version check stated, pooled to ~5.1%.
- Every statpack figure it quotes checks out against the committed pack:
  relist-0 grant family 1.7% (1.2 + 0.5), relist-1 about 13% (8.2 + 5.1),
  CVSG grant family about 35% (29.4 + 5.5), Second Circuit 4.9% (2.6 + 2.3).
- The legal analysis is the most complete of the three: it identifies the
  two distinct holdings below (extraterritoriality via §561(d); the direct
  §546(e) bar on common-law claims), weighs the BIO's "no outcome-level
  split" answer fairly, catches the district court's alternative domestic-
  application ground, and names the vehicle problems (300 adversary
  proceedings, prior BVI losses). It also brings in the Court's record of
  denying prior Madoff safe-harbor petitions and the long-conference
  discount, both of which pointed at exactly what happened.
- The limitations section is honest: it did not read the Second Circuit
  opinion, it flags the CVSG number as the softest input, and it discloses
  the dockets-endpoint confirmation that the case was pending.

What held it down:

- The number does not follow from the analysis. The downward factors it
  lists (no clean split, documented vehicle problems, an unbroken record of
  Madoff denials, first distribution at the long conference) are the ones
  that decided the case, yet the final probability is more than double the
  anchor. The upward factors are generic prestige signals (counsel, amici,
  stakes) that the baseline band already contains in part.
- P(CVSG) = 0.22 carries most of the grant mass and rests on analogy to
  Tribune with no docket signal; the candidate says so, but still lets it
  drive the headline number. The docket-wide CVSG incidence it cites (~1%)
  makes a 22-fold uplift hard to defend for a private-party petition the SG
  had never been invited into.
- The "one or two further relists" expectation and 0.40 relist probability
  did not materialize; that is a forecast-document matter and not scored
  here, but it is consistent with the same optimism in the headline number.

## Leakage

Forward cell. The prediction was created 2026-09-16, twelve days before the
conference and nineteen before the denial. The log carries 33 calls, all
captured. The only call touching this docket is a dockets-endpoint read with
`retrieved_doc_date` 2026-03-17 (the filing date), which the candidate used
to confirm `date_terminated` was null. The two opinion searches reached the
Second Circuit decision below (2025-08-05), not anything about this
petition's disposition. No `data/qp-topics/` read. `retrieved_outcome_material`
= false, `influenced_prediction` = `not_applicable`, `leakage_suspected` =
false. The candidate's disclosure that nothing outcome-revealing surfaced is
consistent with the log.

## Big case

My independent read is 0.40, formed from the record before weighing the
candidate's own score: large dollar stakes and a first-impression Chapter 15
question that matters to the cross-border insolvency bar, but a technical
commercial dispute with little public salience, which the Court disposed of
at its first conference without a CVSG, relist, or separate writing.
