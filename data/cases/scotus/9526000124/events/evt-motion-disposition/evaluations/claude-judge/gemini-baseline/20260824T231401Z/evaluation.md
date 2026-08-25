# Evaluation — gemini-baseline, evt-motion-disposition (scotus/9526000124)

## The cell and the outcome

This is an **interim** cell: an application to stay lower-court rulings against
a presidential executive order on federal election administration, filed
2026-07-27 and resolved 2026-08-24. The outcome is `granted`
(`actual_granted` = 1, `disposition_basis` = `standard`), with
`interim_signals` recording a response requested, referral to the full Court,
and 6 amicus briefs.

## Scores

- `correct` = 0: the prediction named `denied`; the Court granted the stay.
- `brier_score` = (0.15 − 1)² = **0.7225** — the worst of the three, the price
  of the most confident denial call.
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

## Reasoning quality: 0.45

The anchoring itself was correct — the right strictly-prior pool (225 resolved
/ 30 granted, 13.3%), the right floor check — and the referral call (0.95,
which the outcome bore out) was well judged. But the disposition analysis has
structural problems that the outcome exposed:

- **It anchored near the unconditioned baseline while reciting the reasons not
  to.** At 0.15 it sat essentially on the pooled 13.3% for a cell it itself
  described as a highly salient Solicitor General application with a same-day
  response call and heavy escalation. The statpack's own caveat says the
  scored population sits systematically higher on the escalation ladder than
  the pooled cohort; a fully briefed, referred government application is about
  as far from the pooled median as the interim docket gets, and the analysis
  acknowledged the signals without letting them move the number.
- **It rested its merits discount on a single uncorroborated characterization**
  — that the First Circuit observed the administration "did not defend the
  underlying legality" of the order — sourced from one web search whose results
  the log did not capture, and treated Purcell as close to dispositive. Purcell
  is an argument, and the Court granted anyway; a 0.15 needed more than one
  doctrine plus one secondhand quote.
- **A factual slip**: the document describes the target as "the District
  Court's nationwide injunction" where the snapshot names a First Circuit
  ruling (No. 26-1774). Minor, but it suggests the web-sourced narrative was
  not fully reconciled with the provisioned docket.
- The write-up is also the thinnest of the three — a single dense paragraph
  with no explicit decomposition and no self-assessment of where it would most
  likely be wrong.

The response-requested (0.01, correctly read as vacuous) and amicus (0.2)
claims were reasonably handled; those are harness-scored.

## Leakage

Forward mode. The log's result capture is entirely unobserved
(`result_capture_coverage` 0.0), so the assessment rests on the queries and
the prose, as the contract provides: the one web search targeted case context,
not a disposition; the CourtListener call was rate-limited; the reasoning
cites only pre-decision facts. No indication the case surfaced as already
decided. `influenced_prediction` = `not_applicable`.
