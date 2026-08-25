# Evaluation — codex-baseline, evt-motion-disposition (scotus/9526000124)

## The cell and the outcome

This is an **interim** cell: an application to stay lower-court rulings against
a presidential executive order on federal election administration, filed
2026-07-27 and resolved 2026-08-24. The outcome is `granted`
(`actual_granted` = 1, `disposition_basis` = `standard`), with
`interim_signals` recording a response requested, referral to the full Court,
and 6 amicus briefs.

## Scores

- `correct` = 0: the prediction named `denied`; the Court granted the stay.
- `brier_score` = (0.45 − 1)² = **0.3025** — the best of the three candidates,
  because this was the only one that moved substantially toward a grant.
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
  here estimates it. (Its `amicus-increment` proposition at 0.99 was stated
  against a counter-semantics reading — see the run-level flags note on the
  frozen count of 6 versus 13 snapshot entries.)

## Reasoning quality: 0.65

The number was the closest to the outcome, and much of the process is sound:
the same correct strictly-prior anchoring (225 resolved / 30 granted, 13.3%,
floor checked, and explicitly not the pack-wide or a cert rate), a substantial
and justified upward adjustment for the selection signals (Solicitor General
applicant, same-day response request, sustained briefing through supplements,
heavy amicus attention), and unusually honest calibration about what it could
not know — the filings themselves were not provisioned, CourtListener was
throttled, and it said so rather than inventing a merits read.

What holds the score to 0.65 rather than higher:

- **The analysis is procedurally deep but doctrinally empty.** It engaged
  neither Purcell, nor the merits of presidential authority over election
  administration, nor the Court's recent interim practice on stays of
  injunctions against executive action. It got the best number substantially
  by riding the selection signals, and its stated reasons for stopping below
  0.50 are the weak part of the document.
- **One stated reason is close to self-contradictory**: it stopped below 0.50
  partly because "the context does not yet record referral to the full
  Court" — while itself putting 0.78 on referral occurring. A rung it expects
  to fire before disposition carries little weight against the disposition.
- The partial-relief collapse point (a mixed order reads as ungranted) was
  correctly identified and is a legitimate discount; unlike claude-baseline it was
  left unquantified, which is more honest but also less checkable.

## Leakage

Forward mode, confirmed against the log: the CourtListener search was
rate-limited, everything else read provisioned or committed inputs, and no
retrieved document postdates the prediction. The final log row is a
harness-redacted credential-shaped payload — per the capture contract that is
removed text, not evidence of anything retrieved. `influenced_prediction` =
`not_applicable`.
