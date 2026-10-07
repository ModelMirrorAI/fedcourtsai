# Evaluation: gemini-baseline — Mendenhall v. City and County of Denver, No. 25-1205

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`). The petition
was **denied** on 2026-10-05, no noted dissent, after two distributions and a
called-for response. `actual_granted` = 0.

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.08 − 0)² = 0.0064.
- `segment_base_rate` = 0.1724, basis `risk_set`. The prediction froze band
  `elevated` under `sal-v4`, Term 2025, matching the statpack table's heading.
  Pooled bracketed `reached` figures, resolved-weighted, over Terms 2017–2024
  (n = 2810). The caption renders all 10 Terms the pack holds; the configured
  10-Term lookback would reach 2015–2024 but the pack carries no 2015 or 2016
  row, so the in-code pool is the same eight rows and there is no window
  divergence to flag.
- `brier_skill_score` = 1 − 0.0064 / 0.1724² = 0.785, the best of the three by
  a hair, because its probability was one point lower.
- `vote_accuracy` omitted (cert stage). No `semantic_grades` (none declared on
  a cert cell; `semantic_claims` is null).

## What the prediction got right

- The disposition, and the two drivers that actually decided it: the ask is to
  overrule an entrenched precedent, and the Court rarely does that without
  prior signalling in separate opinions; the reliance interests are enormous.
  Both are correct and both point to a silent denial, which is what happened.
- It noticed the amici and the response call and gave them the right sign.

## Where it falls short

- The anchor is not the one the contract asks for. The rationale quotes the
  `relist_bucket=1` terminal cut (8.2%) as "the base rate" and gives the band
  rate only as a range ("historically around 13–18%"), never pooling the
  bracketed `reached` figures over prior Terms. It then "adjusts down from the
  band's upper range to 0.08", which is a move from an unstated number to a
  figure that happens to coincide with the relist-bucket cut. The number is
  defensible; the path to it is not shown.
- It treats the second distribution as a relist for base-rate purposes (the
  bucket-1 rate) even though its own forecast document correctly describes the
  first distribution as pre-dating the response request. The decided docket
  confirms the petition was redistributed after the opposition and reply, not
  held over from a conference. The two stronger rationales caught this and
  explained why it matters; this one did not connect the two observations.
- No vehicle analysis at all: the unpublished Tenth Circuit order, the *Monell*
  posture, the absence of any lower-court merits treatment, and Denver's
  municipal-liability argument are not mentioned, though the opposition was
  provisioned and the candidate's log shows it read its first hundred lines.
- The rationale is a single paragraph with no stated uncertainty, no account
  of what was and was not read (the log shows only partial reads of the
  petition and opposition), and no engagement with the countervailing case
  for a grant beyond naming the amici and the response call.

`reasoning_quality` = 0.55. The conclusion and the headline reasons are right,
and the number scored well, but the analysis is thin, the anchor is the wrong
cut, and the relist mis-reading is carried into the number rather than
corrected.

## Leakage

Mode `forward` (log and context agree); the case was open at prediction
(2026-09-17 versus the 2026-10-05 denial), so `not_applicable` is the default
and I confirmed it on the queries. `result_capture_coverage` is 0.0, which is
this engine's standing shape rather than a defect: every row is unobserved, so
each is graded on its query and none is credited as having returned nothing.
The queries are provisioned-record reads, two statpack greps, and `fedcourts
query` calls bounded `--decided-before 2026-09-17` or `2026`; there are no
CourtListener calls, no web searches, and nothing names this docket's outcome
or `data/qp-topics/`. The reasoning reads only the 2026-09-17 snapshot.
`retrieved_outcome_material` = false, `leakage_suspected` = false.

## Big case

My own read is 0.55 (see `big_case.notes`). Caveat on independence: the
candidate's `big_case_score` sits in the staged `prediction.json`, which I had
read in full before forming my read, so the number was visible to me. My read
rests on the case itself.
