# Evaluation — claude-baseline, evt-motion-disposition (interim)

## The cell and what is scored

This is an **interim**-stage cell (`event.yaml` stage: `interim`): a stay
application at the arrival moment in *Alabama, et al. v. California, et al.*
The outcome resolved **denied** on 2026-08-24 with `actual_granted = 0`.

`segment_base_rate` and `brier_skill_score` are the **harness's** on an
interim cell — `stamp-cell` pools the statpack's interim section over
application-Terms strictly before OT2026 — so I wrote neither, and
`base_rate_basis` stays null structurally (the interim pool is no salience-band
product; this prediction's frozen `context.band` is null, the ordinary interim
shape, so no flag). For the reader: the committed statpack's strictly-prior
pool is OT2025 (178/16) plus OT2024 (47/14) — 225 resolved, 30 granted,
≈ 13.3%, clearing the 50-case floor. `claim_scores` is likewise the harness's
(`interim-v1`), and `vote_accuracy` is omitted: interim votes are elicited,
never scored.

## Scores

- **correct = 1.** Predicted `denied`; actual `denied`. Exact label match.
- **brier_score = 0.09.** `(0.30 - 0)**2`.
- **reasoning_quality = 0.92.**

## What drove reasoning_quality

The strongest rationale of the panel, and the closest number. Its virtues:

- **Resolver-aware from the start.** It decomposed the outcome space
  explicitly (outright denial ~40%, partial relief ~27% resolving denied under
  the denial-first rule, unqualified grant ~30%, withdrawn ~2%) and understood
  that the relief-shape question, under the denial-first collapse, moves the
  scored label more than the win/lose question does — the exact structure of
  this event, and the analysis the outcome vindicated.
- **Baseline discipline.** It pooled the statpack rate correctly (225/30,
  13.3%, floor cleared) and carried the section's own cautions — the
  right-censored escalation counts and the scored population sitting higher on
  the escalation ladder than the pooled cohort — rather than just quoting the
  number.
- **Both directions argued.** Upward: same-day response request, the parallel
  Solicitor General application, post-CASA scope skepticism, stakes. Downward:
  weak merits for the applicants (no textual source of presidential authority
  over election administration; a constitutional-ground injunction; the First
  Circuit's strong language), Purcell equities read the correct way (a stay
  would inject a new regime, not preserve one), and the residual risk that
  relief issues only on the government's parallel application.
- **Calibrated self-report.** It stated its sensitivity (±0.10 on the
  relief-shape axis), said where a reader with different priors should sit,
  and disclosed a post-cutoff headline it declined to pursue.

The small remaining gap to a top score: the retrieval base under the
case-specific judgments was modest (two web searches; the one corpus query
returned unusable analogues, as it candidly reported), so the merits and
equities assessments rest more on summarized coverage than on primary
documents a deeper pull could have supplied. The claims block and its
increments are the harness's to score and played no part in this number.

## Leakage

Forward mode, confirmed against the log: created 2026-08-20, before the
2026-08-24 resolution, so no outcome existed to retrieve. The candidate's own
disclosure is the notable item — one web result dated 2026-08-12 (post-cutoff)
headlined another injunction in *parallel* mail-voting litigation; it was not
opened and disclosed nothing about this application's disposition. On a
forward cell that is legitimate signal in any event, and the unprompted
disclosure counts *for* the cell's integrity. Nothing in the reasoning reads
as already-decided. `influenced_prediction = not_applicable`,
`leakage_suspected = false`.

## Big case

My independent read is 0.9 (formed from the case posture: a twelve-state
application beside the Solicitor General's parallel one, seeking to stay a
nationwide injunction against a presidential election-administration order
months before the midterms). Recorded in `big_case`; no agreement number is
computed here by design.
