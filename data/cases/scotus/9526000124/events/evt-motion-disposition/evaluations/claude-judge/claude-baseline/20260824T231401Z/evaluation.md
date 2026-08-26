# Evaluation — claude-baseline, evt-motion-disposition (scotus/9526000124)

## The cell and the outcome

This is an **interim** cell: an application to stay lower-court rulings against
a presidential executive order on federal election administration, filed
2026-07-27 and resolved 2026-08-24. The outcome is `granted`
(`actual_granted` = 1, `disposition_basis` = `standard`), with
`interim_signals` recording a response requested, referral to the full Court,
and 6 amicus briefs.

## Scores

- `correct` = 0: the prediction named `denied`; the Court granted the stay.
- `brier_score` = (0.25 − 1)² = **0.5625**.
- `segment_base_rate` and `brier_skill_score` are **not written here** — on an
  interim cell both are the harness's, stamped by `stamp-cell` from the
  committed statpack, and `base_rate_basis` stays null structurally (the
  interim pool is no salience-band product; an application freezes no band).
  For the reader: the pool the stamp should support is application-Terms
  strictly before 2026 — Term 2025 (178 resolved substantive, 16 granted) plus
  Term 2024 (47 resolved, 14 granted), 225 resolved / 30 granted ≈ 13.3%,
  which clears the pre-registered 50-resolution floor, so a null stamp here
  would indicate a pack problem rather than a thin pool.
- `vote_accuracy` is omitted: votes are never scored off the merits stage.
- `claim_scores` is the harness's (`interim-v1`), computed in code; nothing
  here estimates it.

## Reasoning quality: 0.8

The strongest process of the three candidates, even though its headline number
was on the wrong side. What earns the score:

- **Correct anchoring**: it pooled the statpack's strictly-prior interim rows
  itself (225 resolved / 30 granted, 13.3%), checked the floor, and carried the
  section's caveats (uneven parse coverage, denial-first mixed orders, the
  scored population sitting higher on the escalation ladder) rather than
  quoting a bare rate.
- **An explicit, checkable decomposition**: P(any relief) ≈ 0.45 for a fully
  briefed Solicitor General application at the top of the escalation ladder,
  times P(unqualified | any relief) ≈ 0.55 for a multi-provision EO where
  partial relief reads as denial → 0.25. Given the granted outcome, the first
  factor was directionally right and well argued (government applicant, recent
  practice of staying broad injunctions against executive action); the miss
  concentrates in the discounts — Purcell and the merits read — and in the
  partial-relief haircut, which the unqualified grant proved too heavy.
- **Honest epistemics**: it disclosed that it could not read the filings (PDF
  links only), that CourtListener was rate-limited, and where its numbers came
  from general knowledge rather than a committed cut. Its identification of the
  amicus-counter discrepancy (frozen 6 vs 13 snapshot entries, singular- vs
  plural-caption parsing) was careful and, per the outcome's `amicus_briefs: 6`,
  prescient about how the counter would resolve.

What holds it back from higher: the two heaviest discounts were stated with
more confidence than the record supported. The Purcell argument treated the
injunction as the status quo, but Purcell's force is weakest when it is the
*Supreme Court* acting on a fully briefed application, and the Court's recent
interim practice — which the candidate itself cited — was the better guide it
declined to follow. The 0.55 partial-relief haircut was an uncommitted
free parameter doing a lot of work.

## Leakage

Forward mode, confirmed against the log: nothing retrieved postdates the
prediction, and nothing shows this case's disposition as already decided. The
one dated retrieval (2026-08-14 corpus row) predates resolution and concerned
routine extension grants elsewhere. `influenced_prediction` = `not_applicable`.
