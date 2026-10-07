# Evaluation: claude-baseline — United Airlines v. Kincannon, No. 26-183 (arrival-moment cert cell)

## Outcome and the scored numbers

The petition was **denied** on 2026-10-05 after a single distribution (Conference of
9/28/2026), with Justice Kavanaugh noting he would grant. `actual_granted` = 0;
`noted_dissent_from_denial` = true.

- `correct` = 1: the candidate predicted `denied`.
- `brier_score` = (0.20 − 0)² = **0.04**.
- `segment_base_rate`, `brier_skill_score`, `base_rate_basis`: **omitted / null.**
  The prediction froze `band: baseline` under `salience_version: sal-v3`. The
  committed `metrics/statpack.md` renders its "Segment base rate by salience band"
  table under **sal-v4**, so the table is no baseline for this band and the
  prompt's only answer to that mismatch is the omission, recorded in this run's
  `flags.json`. For the reader: the committed `statpack.json` still carries a
  sal-v3 block for OT2017–OT2025 whose baseline-band bracketed `reached` figures
  pool to about 5.0% over n ≈ 12,720, and the harness's own version-pinned
  pooling may resolve a rate from it at the stamp; that is the harness's number,
  not one I may write here.
- `vote_accuracy`: omitted (cert stage). `judgment_correct`: null. No
  `semantic_grades` (cert cell; `semantic_claims` is null).

## Leakage

Forward cell, confirmed rather than assumed. The prediction was created
2026-08-16; the event resolved 2026-10-05. The captured log (29 calls, all
captured) shows provisioned-input and statpack reads, one corpus shape query on
recent grants (`retrieved_doc_date` 2025-09-03), two corpus greps for a Detwiler
row, and three CourtListener searches for the Detwiler companion, the only dated
hit a Ninth Circuit opinion of 2025-09-23. No query names this petition's
disposition and no retrieved document postdates the prediction. The candidate's
own `retrieval.md` says the same. `retrieved_outcome_material` = false,
`influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Reasoning quality: 0.80

The strongest of the three rationales, and the one whose structure matches
what happened.

- **Anchor done the contracted way.** It names the band and version, pools the
  bracketed `reached` figure over every rendered Term strictly before OT2026,
  and states the denominator. (The 6.5% / n ≈ 13,163 it quotes does not
  reproduce against the pack committed today, whose sal-v3 block pools to about
  5.0%; the pack has been rebuilt since the cell ran and the staged inputs do
  not let me check the table it read, so this is noted, not penalized.)
- **Both directions argued, with the decisive counter-considerations named.**
  The upward case (counsel, published opinion plus Judge Willett's partial
  non-joinder, LabCorp leaving Rule 23(b)(3) unresolved, business amici, the
  hold request) is set against exactly the points the opposition later pressed
  and a first-conference denial reflects: an application split rather than a
  square rule split, the interlocutory posture, and the unconfirmed Detwiler
  petition. The cross-cutting valence point — the Justices most receptive to a
  class-action-rigor argument are also the most receptive to religious
  objectors — is a genuine, non-obvious observation about this petition.
- **Honest about what it could not confirm.** It checked CourtListener for a
  Detwiler SCOTUS docket, found none, and priced the GVR route down for that
  reason instead of assuming it. The petition confirms the companion petition
  was only *due* on 2026-08-13.
- **Calibrated self-doubt.** The "where to discount me" section names the
  missing brief in opposition as the largest open input and labels the valence
  weight as judgment rather than data.

Where it falls short of higher: the 3x-over-baseline landing at 0.20 is
asserted by analogy ("comparable to an average petition that reaches the
elevated band") rather than derived; and the conditional reasoning that the
valence problem would suppress a written dissent sat beside a Justice noting he
would grant — a noted vote rather than a written dissent, so the forecast was
not wrong on its own terms, but the rationale did not distinguish the two.
Those are refinements, not errors.

## Stakes read

`big_case.evaluator_score` = 0.35, formed from the record before weighing the
candidate's own score (its score sits in the staged `prediction.json`, so I
read the file but set my number from the docket, the petition, the opposition,
and the order). Moderate stakes: a doctrinal Rule 23 question with business
amicus interest and a Justice noting he would grant, against an interlocutory,
fact-bound certification order denied at its first conference.

## Claims and forecast document

Not scored here: the `claims` block is the harness's (`cert` set), and
`predicted_reasoning.md` was read only for context on how the number was formed.
