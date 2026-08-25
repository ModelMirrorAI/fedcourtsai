# Evaluation — codex-baseline

## The cell and the outcome

This is an **interim-stage** cell (`event.yaml` stage: `interim`): the disposition
of stay application 26A124, *Trump v. California*, forecast after Justice Jackson
called for a response on the filing date. The Court **granted** the application on
2026-08-24 (`actual_disposition: granted`, `actual_granted: 1`), referring it to
the full Court the same day. codex-baseline predicted `denied` at probability 0.44,
so `correct = 0` and `brier_score = (0.44 - 1)^2 = 0.3136` — the best Brier of the
three candidates, though still on the wrong side of even.

## Baseline and skill are the harness's

Because the cell is interim, `segment_base_rate` and `brier_skill_score` are
stamped by the harness from the committed statpack, and `base_rate_basis` stays
null structurally (an application freezes no band). For the reader: the statpack's
interim table supports a strictly-prior pool for a Term-2026 application of
Terms 2025 (178 resolved substantive, 16 granted) + 2024 (47, 14) = 30/225 ≈ 13.3%,
which clears the 50-resolution floor, so a stamped rate near 0.133 is expected
rather than a null. `claim_scores` is likewise the harness's (`interim-v1`).

## Reasoning quality: 0.72

Strengths:

- **Correct base-rate discipline.** It pooled the strictly-prior Terms itself
  (30/225 = 13.3%), explicitly rejected the pack-wide 12.1–12.3% rate because it
  contains the case's own Term, and noted the floor was cleared. That matches the
  registered rule.
- **The signals it weighted were the predictive ones.** It adjusted sharply upward
  on the same-day response request, the SG as applicant, completed reply and
  supplemental briefing, and heavy amicus participation — the escalation ladder
  that, on the realized outcome, was the true signal. Its 0.44 was the closest of
  the cohort to the realized grant.
- **A verified defect discovery.** It identified that the frozen
  `amicus_briefs: 6` counts only singular-form "Brief amicus curiae" entries while
  the snapshot shows thirteen amicus filings. I verified this against the
  committed 2026-08-24 snapshot: 6 singular + 7 plural entries. Distinguishing a
  contaminated conditioning state from a substitute baseline is exactly the right
  epistemic move.
- **Honest degradation.** The CourtListener 429 and the absence of provisioned
  filing text are disclosed and the resulting limits stated rather than papered
  over.

Weaknesses:

- **Thin legal analysis.** The rationale is nearly all base rate plus docket-shape
  signals; it declines any merits or equities analysis on the ground that no
  filing text was provisioned. That is candid, but a stronger cell would have
  reasoned from what was knowable — the party lineup, the lower-court posture, the
  government's recent success rate on emergency applications — as claude-baseline did.
  The 0.44 landing point is well-placed but under-argued: the step from 13.3% to
  0.44 rests on "strong attention and stakes signals" without articulating why
  those signals should more than triple the base rate rather than double it.
- The "unqualified grant is a narrower target than partial relief" point was
  reasonable ex ante but cut the wrong way here — the Court granted outright.

## Leakage

Forward mode, run 2026-08-16, resolved 2026-08-24: no outcome existed to leak.
The log shows no post-resolution document dates, no web searches, and one failed
MCP call; nothing reads the disposition off any source. `not_applicable`.
