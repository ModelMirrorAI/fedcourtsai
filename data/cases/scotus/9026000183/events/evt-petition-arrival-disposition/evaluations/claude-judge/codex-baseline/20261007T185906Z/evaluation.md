# Evaluation: codex-baseline — United Airlines v. Kincannon, No. 26-183 (arrival-moment cert cell)

## Outcome and the scored numbers

The petition was **denied** on 2026-10-05 after a single distribution (Conference of
9/28/2026), with Justice Kavanaugh noting he would grant. `actual_granted` = 0;
`noted_dissent_from_denial` = true.

- `correct` = 1: the candidate predicted `denied`.
- `brier_score` = (0.14 − 0)² = **0.0196**, the best of the three.
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
captured) is shell reads of the prompt, schemas, source, statpack, provisioned
documents and snapshot, plus two `other` rows whose text the harness redacted
as credential-shaped — removed text, not outcome material. The candidate's
`retrieval.md` reports three CourtListener searches (Detwiler, Speerly, a
Rule 23 phrase) that failed with HTTP 429; no `mcp:` call class appears in the
captured log, so those calls are unobserved here and are graded on the queries
the candidate disclosed, none of which names this petition's disposition. No
retrieved document postdates the prediction. `retrieved_outcome_material` =
false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Reasoning quality: 0.72

A compact rationale whose judgment proved the best calibrated, and whose
reasons are the right ones.

- **Anchor done the contracted way**, with the right population choice stated:
  the bracketed `reached` figure pooled over OT2017–OT2025, and an explicit
  rejection of the terminal relist-zero rate as an arrival prior. (Its 6.56% /
  n = 13,163 matches claude-baseline's figure and likewise does not reproduce
  against the pack committed today; noted, not penalized, since the staged
  inputs do not show the table it read.)
- **The vehicle problems are named.** Interlocutory Rule 23(f) posture, Judge
  Willett joining the judgment under abuse-of-discretion review, several of the
  petition's conflict authorities being district-court decisions, and the
  possibility that the appellate cases are applications of settled commonality
  principles to different records — the exact line the opposition later took
  and a first-conference denial reflects.
- **Candid about its evidence.** It says the record was one-sided (no brief in
  opposition, no appendix), that its CourtListener checks failed, and that the
  absent adversarial filing was the largest uncertainty — rather than filling
  the gap with assumption.
- **The Detwiler hold is read both ways**: as a GVR route and as a reason the
  Court might see another case as controlling part of the dispute.

Why not higher: the upward adjustment from 6.56% to 0.14 is a list of features
rather than a weighing, so the reader cannot see why the landing is 0.14 rather
than 0.10 or 0.20; it does not engage the counsel-quality signal or the
business-amicus likelihood that the other candidates priced; and it is the
thinnest of the three on the legal merits of the commonality question itself.
The rationale is sound and disciplined but less developed than claude-baseline's.

## Stakes read

`big_case.evaluator_score` = 0.35, formed from the record before weighing the
candidate's own score (its score sits in the staged `prediction.json`, so I
read the file but set my number from the docket, the petition, the opposition,
and the order). Moderate stakes: a doctrinal Rule 23 question with business
amicus interest and a Justice noting he would grant, against an interlocutory,
fact-bound certification order denied at its first conference.

## Claims and forecast document

Not scored here: the `claims` block is the harness's (`cert` set), and
`predicted_reasoning.md` was read only for context on how the number was
formed. Observed for the record only: that document forecast no noted dissent
or statement on denial; a Justice noted he would grant.
