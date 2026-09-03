# Evaluation — codex-baseline, evt-order-response-requested-disposition

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

codex-baseline called `granted` at P = 0.68 — the most conservative of the three
candidates on an application the Court did grant. `correct = 1`,
`brier_score = (0.68 − 1)² = 0.1024`.

## Reasoning quality: 0.85

A careful, record-grounded rationale whose caution was reasoned rather than
hedged:

- **Anchored correctly** on the statpack's strictly-prior interim pool as it
  stood at prediction time (30/225 ≈ 13.3%, floor cleared) and explicit that
  the pool is unconditioned on the escalation ladder this cell was selected on.
- **The deepest record engagement of the three.** It did not stop at the docket
  sheet: it searched inside the D.C. Circuit opinion itself (the Rao dissent's
  standing, statutory-authority, deference, and equities arguments; the
  majority's tailoring of the injunction to permit below-ground security work;
  the majority's point that the government had earlier called the projects
  independent). Its restraint at 0.68 is argued from those specifics, not from
  vagueness — the injunction's carve-outs gave the Court a practical path to
  deny, and without the application text it could not know whether those
  record-specific points were answered.
- **Priced the event's resolution rule** — a grant-in-part reads as ungranted
  under the denial-first collapse — and was honest that the missing application
  and response text was its main uncertainty.

In hindsight the down-weighting overcorrected: the applicant-class signal
(the Solicitor General seeking emergency relief in a presidential-power
posture) deserved more weight than the record-specific denial paths, and
claude-baseline's 0.80 shows that reference class was available. But the analysis
itself is sound, transparent about its limits, and everything in it resolves
against the record; the miss is one of weighting, not method.

## Leakage: none (forward)

Mode `forward`; the application was genuinely open at prediction time
(predicted 2026-08-20, resolved 2026-08-31). Result-capture coverage is 0.71
and the unobserved rows are graded on their queries per the marker rule: every
retrieval query is a lower-court record read, self-bounded with explicit
filed-before filters at 2026-08-14/15, and no legible document date on this
dispute postdates 2026-08-07. The final log row carries harness redaction
markers, which read as removed text, not outcome material.
`influenced_prediction = not_applicable`.
