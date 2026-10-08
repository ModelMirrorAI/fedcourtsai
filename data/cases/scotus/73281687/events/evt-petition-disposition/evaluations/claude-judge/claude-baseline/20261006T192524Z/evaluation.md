# Evaluation: claude-baseline — Mendenhall v. City and County of Denver, No. 25-1205

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`). The petition
was **denied** on 2026-10-05, no noted dissent, after two distributions and a
called-for response. `actual_granted` = 0.

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.09 − 0)² = 0.0081.
- `segment_base_rate` = 0.1724, basis `risk_set`. The prediction froze band
  `elevated` under `sal-v4`, Term 2025, and the statpack's "Segment base rate by
  salience band (sal-v4)" heading matches that version. I pooled the bracketed
  `reached` figures, resolved-weighted, over every rendered Term strictly before
  2025 — 2017 through 2024 (n = 2810; 2026 renders no figure and 2025 is the
  case's own Term). The caption renders 10 of 10 Terms, and the configured
  10-Term lookback would reach 2015–2024, but the pack holds no 2015 or 2016
  row, so the in-code window pools the same eight rows; no window divergence to
  flag.
- `brier_skill_score` = 1 − 0.0081 / 0.1724² = 0.727.
- `vote_accuracy` omitted (cert stage, never scored). No `semantic_grades`
  (no semantic set is declared on a cert cell; `semantic_claims` is null).

## What the prediction got right

- The disposition and the direction of the adjustment. The candidate anchored
  on the correct pooled reached rate (its own table matches mine) and moved
  about halfway below it, which the denial rewards.
- The sharpest observation in the set: that the second distribution is **not a
  relist**. The decided docket confirms the sequence exactly as the candidate
  read it: distributed June 2 for the June 18 conference, response requested
  June 15, opposition July 14, reply July 28, redistributed July 29 for the
  September 28 long conference, denied October 5. The petition was never
  considered and held. Recognising that the `elevated` band and the relist-1
  bucket both overstate the petition's real state is the right reason to sit
  below the anchor.
- A disciplined legal read: no split is possible because every lower court is
  bound by *Jones*; an "overrule X" ask almost never moves without a prior
  separate writing from a member of the Court; the workability radius (fellow-
  officer and informant affidavits) is the opposition's strongest point; the
  vehicle is an unpublished Tenth Circuit order in a *Monell* damages suit with
  no lower-court merits analysis. Each of these is accurate and each is a
  reason the Court denies silently, which it did.
- It credited the countervailing signals honestly (the response call at the
  first conference, four amici, a repeat-player advocate, originalist appetite)
  without letting them pull the number toward the band rate.

## Where it could be stronger

- The *Monell* aside ("an express policy that is itself unconstitutional needs
  no deliberate-indifference showing") is right but briefly stated; it slightly
  undercuts the candidate's own vehicle-issue point and would have benefited
  from saying how much weight it carries either way.
- The "Why I am not lower" section leans on the Institute for Justice's recent
  grants without saying which, which is the one place the rationale asserts a
  pattern it does not show.
- Its stated uncertainty section is a strength, not a weakness: it names the
  signal (response call without relist) for which no committed rate exists and
  says the treatment is judgement.

`reasoning_quality` = 0.85. The analysis is sound given the outcome, anchored
correctly, discounted for the right reason, and its uncertainty is stated.

## Leakage

Mode `forward` (log and context agree); the case was genuinely open when the
prediction was made (created 2026-09-17, snapshot 2026-09-17, denied
2026-10-05), so the default `not_applicable` holds. I checked rather than
rubber-stamped it: `result_capture_coverage` is 1.0, the only
`retrieved_doc_date` is 2026-09-17 (a corpus query, pre-resolution), the
CourtListener docket-entries call for this docket returned nothing, the
three searches returned nothing, and nothing in the log names
`data/qp-topics/`. The reasoning reads the docket off the provisioned
snapshot and nothing later. `retrieved_outcome_material` = false,
`leakage_suspected` = false.

## Big case

My own read is 0.55 (see `big_case.notes`). A caveat on independence: the
candidate's `big_case_score` sits in the staged `prediction.json`, which I had
read in full before forming my read, so the number was visible to me. My read
rests on the case itself: a question with nationwide radius if ever taken, in a
poor vehicle, denied silently.
