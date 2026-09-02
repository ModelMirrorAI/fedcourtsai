# Evaluation — gemini-baseline, evt-order-response-requested-disposition

**Interim cell.** The event's stage is `interim` (stay application, forecast at
the response-requested rung), so `correct` and `brier_score` are computed on the
grant binary as recorded — `outcome.actual_granted = 1`, disposition `granted`
on 2026-08-31 — and the baseline and skill are the harness's: `stamp-cell` pools
the interim base rate from the committed statpack (application Terms strictly
before OT2026; on the current pack the strictly-prior substantive pool is
OT2024 + OT2025 = 296 resolved, 31 granted, ≈ 10.5%, which clears the
50-resolved floor), so I write neither `segment_base_rate` nor
`brier_skill_score`, and `base_rate_basis` stays null structurally. No votes
were predicted and none would be scored on this stage; `vote_accuracy` is
omitted. No semantic set is declared on this stage, so no `semantic_grades`
block is written. `claim_scores` is the harness's.

## Outcome vs prediction

gemini-baseline called `granted` at P = 0.75 on an application the Court did grant.
`correct = 1`, `brier_score = (0.75 − 1)² = 0.0625`.

## Reasoning quality: 0.65

Directionally sound and correctly anchored, but the thinnest of the three
rationales:

- **The anchor and the adjustment are right.** It opens from the statpack's
  strictly-prior interim pool as it stood at prediction time (13.3%), then
  adjusts upward on real, record-grounded signals: the Solicitor General as
  applicant, the security declarations behind the application, the 2–1
  affirmance with the Rao dissent's deference argument, and the response call
  as an attention signal. Those are the load-bearing facts, and the outcome
  bore them out.
- **What is missing is the other side of the ledger.** One paragraph carries
  the entire disposition analysis, and it is one-directional: no engagement
  with the reasons the Court might deny (the government lost below after full
  expedited merits consideration; the injunction's carve-outs already
  permitting security-related work — a point codex-baseline developed from the
  opinion text), no pricing of the partial-grant path even though a mixed order
  resolves as ungranted under this event's denial-first rule, and no statement
  of what would move the number. "Historical deference to the Executive on
  national security" is asserted rather than tied to any committed rate or
  named line of orders.
- The landing at 0.75 is reasonable and proved well calibrated, but the
  document gives a reader little basis to distinguish it from 0.6 or 0.85 —
  the calibration is in the number more than in the argument.

## Leakage: none (forward)

Mode `forward`; the application was genuinely open at prediction time
(predicted 2026-08-20, resolved 2026-08-31). Every logged call is `unobserved`
(capture coverage 0.0 — this engine's standing telemetry shape, not a defect),
so each is graded on its query per the marker rule: the queries are the
provisioned inputs, the statpack, docket searches for the dispute (including
the application's own number, 26A203, while the case was open — ordinary
forward retrieval), and the D.C. Circuit's 2026-08-07 opinion. Nothing sought
or showed a disposition that did not yet exist.
`influenced_prediction = not_applicable`.
