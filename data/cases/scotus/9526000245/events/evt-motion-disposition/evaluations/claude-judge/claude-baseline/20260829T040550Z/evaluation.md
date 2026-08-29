# Evaluation — claude-baseline, evt-motion-disposition (scotus/9526000245)

## The cell and the outcome

This is an **interim**-stage cell (`event.yaml` stage: `interim`): application
26A245 for an injunction pending appeal, submitted to Justice Barrett on
2026-08-17 and docketed 2026-08-25. The outcome is `denied`,
`actual_granted = 0`, resolved 2026-08-27 on a `standard` disposition basis,
with the interim ladder never firing (`response_requested: false`,
`referred_to_court: false`, `amicus_briefs: 0`).

## Scores

- **`correct` = 1.** The prediction's `predicted_disposition` is `denied`,
  an exact match on the interim disposition axis. (Written per the contract;
  the harness re-stamps this bit in code.)
- **`brier_score` = 0.0001** — `(0.01 - 0)^2`. The lowest-probability call
  was right, so the elicited Brier is near-perfect. (Also re-stamped in code
  on an interim cell.)
- **`segment_base_rate` and `brier_skill_score` are left null, and
  `base_rate_basis` stays null: this is an interim cell**, so the baseline is
  the harness's — `stamp-cell` pools the statpack interim section's
  substantive grant rate over application Terms strictly before OT2026 and
  writes both fields itself. For the reader: the currently committed
  `metrics/statpack.md` interim table pools OT2025 (16/178) + OT2024 (14/49)
  = 30/227 ≈ 13.2% resolved-substantive grant rate, above the pre-registered
  50-resolved floor, so a non-null stamped rate is expected. The prediction's
  `context.band` is null — the ordinary interim shape, no flag needed.
- **`vote_accuracy` omitted** — never scored off a merits stage; the
  prediction noted no votes anyway.
- **No `semantic_grades` block** — no semantic set is declared on an interim
  event.
- **`claim_scores`** is the harness's (`interim-v1`, computed in code from the
  prediction's claims, the outcome's `interim_signals`, and the statpack);
  not filled or estimated here.

## Reasoning quality: 0.92

The strongest rationale of the three candidates, and it earns the number on
process, not just on being right:

- **Correct, checked baseline discipline.** It pooled the statpack's
  strictly-prior Terms (quoting 30/226 ≈ 13.3% from the pack as committed at
  its run date; the table now reads 30/227 — a refresh, not an error),
  verified the pool clears the 50-resolved floor, and correctly rejected a
  misread of the floor example.
- **The adjustment off the baseline is argued, not asserted.** It names the
  cohort mismatch (the pooled rate is dominated by counseled, referred,
  briefed applications; this one is pro se at the ladder's floor), applies
  the correct and hardest legal standard for an injunction pending appeal
  ("significantly higher justification" than a stay), and grounds the
  posture in the retrieved district record (habeas denied, action dismissed,
  TRO moot, COA declined, all within days).
- **A near-exact analogue** (26A237, pro se substantive application, denied
  in four days, no response, no referral) retrieved from the corpus
  disciplines both the disposition and the timing forecast — and the actual
  two-day denial landed inside its predicted window.
- **Honest uncertainty accounting**: it discloses it never read the
  application's own text, names the opaque district-docket entries, and
  correctly identifies resolver/order-form noise — not legal merit — as the
  residual risk, which is exactly why it floored at 0.01 rather than lower.
- The ladder claims (0.04 response, 0.10 referral, 0.02 amicus) are
  individually reasoned and internally consistent with the disposition
  number; all four resolved in its favor.

What keeps it off the very top: nothing material — a small deduction for the
unread application text (acknowledged) and for a referral number an order of
magnitude above the base-rate evidence it itself cites, which is defended but
thinly.

## Leakage

Forward mode, confirmed rather than rubber-stamped: the application was
docketed 2026-08-25, the prediction is timestamped 2026-08-25T23:35Z, and the
denial issued 2026-08-27, so the outcome did not exist at prediction time.
The captured log (`result_capture_coverage` 1.0) shows CourtListener reads of
the district docket (doc dates 2026-07-22), a corpus applications query
(2026-08-25), and statpack reads — nothing dated on or after the resolution,
no query for this application's disposition, no `data/qp-topics/` read.
`influenced_prediction` = `not_applicable`, `retrieved_outcome_material` =
`false`.
