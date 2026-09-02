# Evaluation — claude-baseline, evt-order-response-requested-disposition

**Interim cell.** The event's stage is `interim` (stay application, forecast at
the response-requested rung), so `correct` and `brier_score` are computed on the
grant binary as recorded — `outcome.actual_granted = 1`, disposition `granted`
on 2026-08-31 — and the baseline and skill are the harness's: `stamp-cell` pools
the interim base rate from the committed statpack (application Terms strictly
before OT2026; on the current pack the strictly-prior substantive pool is
OT2024 + OT2025 = 296 resolved, 31 granted, ≈ 10.5%, which clears the
50-resolved floor), so I write neither `segment_base_rate` nor
`brier_skill_score`, and `base_rate_basis` stays null structurally. The
candidate's noted 6–3 vote lineup is elicited, never scored on an interim cell,
so `vote_accuracy` is omitted. No semantic set is declared on this stage, so no
`semantic_grades` block is written. `claim_scores` is the harness's.

## Outcome vs prediction

claude-baseline called `granted` at P = 0.80 — the highest probability of the three
candidates on an application the Court did grant. `correct = 1`,
`brier_score = (0.80 − 1)² = 0.04`.

## Reasoning quality: 0.90

The strongest write-up in the cell, and the discipline is visible end to end:

- **Anchored correctly.** It opens from the statpack's interim pool as it stood
  at prediction time (30/225 ≈ 13.3% strictly-prior), quotes the floor it
  clears, and carries the section's own caveats (unconditioned pool,
  right-censored escalation columns) rather than treating the number as a
  description of this application.
- **Adjustments argued in both directions.** Upward: government applicant
  (explicitly sourced to training knowledge and discounted as such), the
  D.C. Circuit's own 14-day self-stay inviting Supreme Court review, the
  response called for on a four-day clock timed to the mandate, and the current
  majority's revealed equities on judicial supervision of presidential action,
  with Franklin v. Massachusetts as the likelihood-of-success hook. Downward:
  the government lost below after full expedited merits consideration, the
  weaker irreparable-harm posture (the East Wing demolition already done), and
  ~5% explicitly priced on a partial grant reading as ungranted under the
  denial-first collapse. That last point — pricing the event's own resolution
  rule — is exactly what the headline number should do and the other candidates
  did less crisply.
- **Honest uncertainty accounting.** The "where to discount me" section names
  its weakest link (the applicant-class adjustment rests on recalled
  OT2024–OT2025 emergency-docket outcomes, not a committed cut) and states what
  would move the number. It also disclosed a snapshot/context mismatch and its
  deliberate stop before the application's own disposition.

The outcome bore the analysis out: an unqualified grant, with the candidate's
0.80 the best-calibrated headline number of the three. Held short of higher
only because the decisive applicant-class reference is a training-knowledge
estimate rather than a verifiable committed rate — a limitation the candidate
itself flagged.

## Leakage: none (forward)

Mode `forward`; the application was genuinely open at prediction time
(predicted 2026-08-20, resolved 2026-08-31). The captured log (coverage 1.0)
shows lower-court docket retrieval no later than 2026-08-07 on this dispute and
a corpus vintage check at 2026-08-19 — all legitimate forward signal — and the
prose predicts rather than reports. `influenced_prediction = not_applicable`.
