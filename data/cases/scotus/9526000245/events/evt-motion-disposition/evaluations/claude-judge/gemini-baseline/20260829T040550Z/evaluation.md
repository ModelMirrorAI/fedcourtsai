# Evaluation — gemini-baseline, evt-motion-disposition (scotus/9526000245)

## The cell and the outcome

This is an **interim**-stage cell (`event.yaml` stage: `interim`): application
26A245 for an injunction pending appeal, submitted to Justice Barrett on
2026-08-17 and docketed 2026-08-25. The outcome is `denied`,
`actual_granted = 0`, resolved 2026-08-27, with the interim ladder never
firing (`response_requested: false`, `referred_to_court: false`,
`amicus_briefs: 0`).

## Scores

- **`correct` = 1.** `predicted_disposition` = `denied` matches exactly.
  (Written per the contract; re-stamped in code.)
- **`brier_score` = 0.000001** — `(0.001 - 0)^2`, the best elicited Brier of
  the three candidates. (Re-stamped in code on an interim cell.)
- **`segment_base_rate` and `brier_skill_score` are left null, and
  `base_rate_basis` stays null: interim cell**, so both are the harness's —
  `stamp-cell` pools the statpack interim section over application Terms
  strictly before OT2026. For the reader: the currently committed table pools
  OT2025 (16/178) + OT2024 (14/49) = 30/227 ≈ 13.2%, above the 50-resolved
  floor, so a non-null stamped rate is expected. `context.band` is null —
  the ordinary interim shape.
- **`vote_accuracy` omitted** — never scored off a merits stage; no votes
  predicted.
- **No `semantic_grades` block** — no semantic set declared on an interim
  event. **`claim_scores`** is the harness's (`interim-v1`); not filled here.

## Reasoning quality: 0.55

The call and the structure are right; the support is thin and partly
unverifiable.

What it does well:

- **Correct baseline discipline in one line**: it pools the strictly-prior
  Terms (quoting 30/226 ≈ 13.3% from the pack as committed at its run date),
  then adjusts down for the pro se, bottom-of-ladder posture — the right
  shape of argument for this cell.
- The predicted path (chambers denial by the Circuit Justice, no response
  call, no referral, no amici) tracks the correct "fair prospect / likelihood
  of reversal" framework and is exactly what happened.

What holds the score down:

- **The pivotal factual characterization is unverifiable and partly
  off-key.** The heavy downward adjustment leans on web-search context that
  the applicants show "a pattern of filing 'sovereign citizen' or frivolous
  common-law copyright claims" against Wisconsin officials. Its own log's
  results are all unobserved, its prose cites nothing from the court record
  itself, and a copyright-claims pattern is an odd fit for what the district
  record (per the docket entries other retrieval on this event surfaced)
  shows as a §2241 pretrial-habeas/bond dispute dismissed for
  non-exhaustion. The respondent-description ("an Ozaukee County judge") is
  also loose — the district party record ties Gerol to a *Washington* County
  court respondent group — a small error, but of a piece with the sourcing.
  The conclusion survives without the characterization, which is the point:
  the load-bearing evidence for the adjustment should have been the
  retrievable dismissal order, not an uncaptured search impression.
- **Total reasoning is a single short paragraph** with no engagement with the
  district court's actual grounds (exhaustion, COA denial), no analogue, no
  cohort caveat on the pooled rate, and no uncertainty accounting for the
  0.001 tail — an extremely aggressive floor given order-entry and resolver
  noise, which happened to pay off here but is not defended anywhere.
- The ladder claims are stated bare (0.01 / 0.05 / 0.001) with a one-clause
  justification.

The grade reflects sound structure and a correct, decisive call built on
thinly-sourced support — not the outcome, which the Brier already prices.

## Leakage

Forward mode, confirmed: prediction written 2026-08-25T23:45Z, denial
2026-08-27, so no outcome existed to leak. The log's
`result_capture_coverage` is 0.0 — every call unobserved, the engine's
standing telemetry shape, not a defect — so per the capture rule each call is
graded on its query: docket-number and party-name searches (CourtListener and
web) for background on a then-undecided application, statpack and schema
reads. None seeks a disposition; no `retrieved_doc_date` exists to postdate
anything; no `data/qp-topics/` read. Note the unobserved results mean "never
seen", not "nothing found" — but with the case genuinely open at prediction
time, there was no outcome for any result to carry.
`influenced_prediction` = `not_applicable`, `retrieved_outcome_material` =
`false`.
