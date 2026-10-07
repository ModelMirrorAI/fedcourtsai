# Evaluation: codex-baseline — Mendenhall v. City and County of Denver, No. 25-1205

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`). The petition
was **denied** on 2026-10-05, no noted dissent, after two distributions and a
called-for response. `actual_granted` = 0.

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.09 − 0)² = 0.0081.
- `segment_base_rate` = 0.1724, basis `risk_set`. The prediction froze band
  `elevated` under `sal-v4`, Term 2025, matching the statpack table's heading.
  Pooled bracketed `reached` figures, resolved-weighted, over Terms 2017–2024
  (n = 2810). The caption renders all 10 Terms the pack holds; the configured
  10-Term lookback would reach 2015–2024 but the pack carries no 2015 or 2016
  row, so the in-code pool is the same eight rows and there is no window
  divergence to flag.
- `brier_skill_score` = 1 − 0.0081 / 0.1724² = 0.727.
- `vote_accuracy` omitted (cert stage). No `semantic_grades` (none declared on
  a cert cell; `semantic_claims` is null).

## What the prediction got right

- The disposition and a well-placed number. The candidate's pooled anchor
  (17.24%, n = 2810, with the rounding caveat stated) is exactly the figure I
  computed, and it explained in which direction and why it moved from it.
- The distribution discount is correct and verified: the decided docket shows
  the response was requested after the first distribution and before the first
  conference, and the second distribution followed the opposition and reply.
  The candidate rightly declined to read the summer interval as a hold.
- The vehicle analysis is the most careful in the set. It did not simply accept
  Denver's *Monell* framing, checked *Bryan County v. Brown* through
  CourtListener for the distinction between directly unconstitutional municipal
  action and facially lawful action, and gave the vehicle point a modest rather
  than dispositive weight. It also verified *Jones*'s hearsay holding at the
  pin cite rather than asserting it.
- It stated its limits plainly: the reply was listed but not provisioned and
  was not read; the web searches returned nothing usable; no outcome material
  was encountered.

## Where it could be stronger

- The rationale says the event "has no express stage" and that the petition-
  disposition identity supplies the cert standard. The committed `event.yaml`
  carries `stage: cert`; the candidate reached the right standard either way,
  but this is a misread of its input.
- It uses the terminal relist and CVSG cuts "qualitatively" but does not say
  what that qualitative use contributed, so the path from the 17.24% anchor to
  9% is asserted as "substantial downward adjustment" rather than decomposed.
  claude-baseline's rationale decomposes the same move more legibly.
- The prose is dense; several sentences restate the contract rather than
  advance the analysis.

`reasoning_quality` = 0.82. Sound, correctly anchored, legally careful on the
vehicle question, slightly less legible than the strongest rationale on how the
number was reached.

## Leakage

Mode `forward` (log and context agree); the case was open at prediction
(2026-09-17 versus the 2026-10-05 denial), so `not_applicable` is the default
and I confirmed it. `result_capture_coverage` is 0.93: the two unobserved rows
are hosted web searches, graded on their queries, and both query historical
*Jones v. United States* citations, not this docket. The captured CourtListener
calls resolve *Bryan County v. Brown* and *Jones* (1960) by citation and read
snippets of those opinions. No call targets docket 73281687 or No. 25-1205,
no `retrieved_doc_date` is set anywhere, and nothing names `data/qp-topics/`.
The candidate's own statement that it did not retrieve the disposition is
consistent with the log. `retrieved_outcome_material` = false,
`leakage_suspected` = false.

## Big case

My own read is 0.55 (see `big_case.notes`). Caveat on independence: the
candidate's `big_case_score` sits in the staged `prediction.json`, which I had
read in full before forming my read, so the number was visible to me. My read
rests on the case itself.
