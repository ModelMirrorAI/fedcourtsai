# Evaluation — gemini-baseline — Fairfield Sentry Ltd. v. Citibank NA London (scotus/73281372, evt-petition-disposition)

## Outcome and scores

The petition was **denied** on the October 5, 2026 order list after its first
distribution (Conference of September 28, 2026): no relist, no CVSG, no noted
dissent; Justice Alito took no part. `actual_granted` = 0.

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.03 − 0)² = **0.0009**.
- `segment_base_rate` = **0.0512**, basis `risk_set`. The prediction froze
  `band: baseline` under `salience_version: sal-v4`, matching the statpack
  table heading. Pooled bracketed `reached` figure for `baseline`,
  resolved-weighted over OT2017–OT2024 (the eight rendered Terms strictly
  before Term 2025): 592.9 / 11,580 ≈ 5.12%. The caption renders 10 of 10
  Terms, so no window divergence.
- `brier_skill_score` = 1 − 0.0009 / 0.0512² = **+0.66**. The only candidate
  to beat the band baseline on this cell.

Cert cell: no `vote_accuracy`, `judgment_correct`, `semantic_grades`, or
`claim_scores` is mine to write.

## Reasoning quality: 0.45

The number landed closest, but `reasoning_quality` grades the soundness of
the rationale, and this one is thin.

What it does right:

- It anchors on the statpack rather than on intuition, names the band and
  the first-distribution posture, and correctly reads the relist-0 bucket's
  grant family (1.7%) and the baseline band's reached rate.
- It identifies the respondents' contested-split argument as the main
  reason denial stays likely, which is the right lever.
- It notes CVSG as the main uncertainty and keeps it low, which was right.

What held it down:

- The anchor is mis-pooled. It quotes the 2024 row's reached rate (5.7%)
  alone rather than pooling the strictly-prior Terms the contract and the
  table caption call for; the pooled figure is 5.1%. The two differ little
  here, but the method is wrong and would matter in a band where the Terms
  diverge.
- The move from the anchor to 3% is asserted rather than argued: "adjust
  this slightly downward ... despite the high stakes" is followed by one
  sentence on the contested split and one on the absence of a relist or
  CVSG. The latter is not discriminating at a first distribution, since no
  petition has a relist yet. The factors that actually decided the case (no
  square conflict on a first-construed statute, the vehicle complications
  the BIO documents, the Court's record of denying Madoff safe-harbor
  petitions, the long-conference backlog) are not engaged.
- The relist-0 terminal rate of 1.7% is quoted as if it were a prior for a
  petition that has not yet been considered; it is the terminal grant rate
  of petitions that *ended* at zero relists, which is a different
  population. Mixing it with the reached-band rate is the kind of
  conflation the statpack caption warns against.
- Three short paragraphs do not show that the petition, BIO, or the Second
  Circuit's two holdings were actually read beyond the headline question.
  The retrieval note's "Failed due to syntax" corpus query also means no
  priors were consulted.

In short: a well-calibrated number reached by a route that would not
reliably produce one.

## Leakage

Forward cell. The prediction was created 2026-09-16, before the conference
and the denial. The log carries 36 calls; every marker-carrying call is
`unobserved` (`result_capture_coverage` 0.0), which is this engine's
standing capture shape and not a defect, so each call is graded on its
query. The queries are reads of the provisioned record, statpack greps, two
attempted corpus queries, and one CourtListener search for "extraterritorial
application 546(e)". None names this docket, its caption, its disposition,
or `data/qp-topics/`. `retrieved_outcome_material` = false,
`influenced_prediction` = `not_applicable`, `leakage_suspected` = false.
Because nothing was captured, the "nothing retrieved" conclusion rests on
the queries, not on observed results; the candidate's own statement that it
did no outcome search is consistent with them.

## Big case

My independent read is 0.40, formed from the record before weighing the
candidate's own score: roughly $6 billion in Madoff feeder-fund clawback
claims and a first-impression Chapter 15 / §546(e) question, but a technical
dispute of specialized interest, denied at first conference without CVSG,
relist, or noted dissent.
