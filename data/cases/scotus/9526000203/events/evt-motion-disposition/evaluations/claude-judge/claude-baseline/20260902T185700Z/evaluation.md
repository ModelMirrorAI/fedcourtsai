# Evaluation — claude-baseline, evt-motion-disposition (scotus/9526000203)

This is an **interim** cell (`event.yaml` stage: `interim`): an emergency
application by the Solicitor General to stay the D.C. Circuit's affirmance of a
preliminary injunction against White House ballroom construction. The outcome
is `granted` (`actual_granted` = 1, resolved 2026-08-31, standard basis, with
`interim_signals`: 7 amicus briefs, referred to the Court, response requested).

## Scores

- **correct = 1.** Predicted disposition `granted` matches `actual_disposition`
  `granted` exactly.
- **brier_score = 0.09** — (0.70 − 1)².
- **Baseline and skill are the harness's on an interim cell.** I wrote neither
  `segment_base_rate` nor `brier_skill_score`; `stamp-cell` pools the interim
  baseline from the committed statpack (application Terms strictly before this
  case's Term 2026) and derives the skill from it. For the reader: the
  currently committed statpack's interim table shows Terms 2025 + 2024 =
  296 resolved substantive applications, 31 granted (≈ 10.5%), which clears the
  pre-registered 50-resolved floor, so a stamped rate should exist. The
  candidate quoted 13.3% (30/225) from the statpack as committed at its run
  date (2026-08-20); the difference is ordinary corpus refresh between its run
  and mine, not an error by the candidate. `base_rate_basis` stays null
  structurally — the interim pool is no salience-band product, and this
  prediction froze no band (`context.band` null), the ordinary interim shape.
- **vote_accuracy omitted** — never scored off a merits cell; the prediction
  carried no votes anyway.
- **No semantic grades** — no semantic set is declared on an interim event.
- `claim_scores` is the harness's; nothing here grades the claims block or
  `predicted_reasoning.md`.

## Reasoning quality: 0.9

An exemplary anchor-and-adjust structure. The base rate is computed correctly
and transparently from the strictly-prior pool with the floor check shown, and
— unusually — the candidate carries the statpack's own caveats forward: the
right-censored escalation columns read for shape only, and the scored
population's selection above the pooled cohort named explicitly. Each upward
adjustment is stated with its rough magnitude and its evidentiary footing (the
government-applicant effect flagged as the largest and least anchored, resting
on general knowledge rather than a committed conditioned cut, with a stated
±0.12 error bar). The counterweights that hold it at 0.70 are genuinely
adverse: the denial-first mixed-order convention explicitly priced at 5–8
points, the irreversibility equities, and the panel's own fourteen-day
accommodation read correctly as expectation of engagement rather than
reversal. Case-specific facts come from date-bounded CourtListener retrieval
of the D.C. Circuit record. The candor section is a model of the disclosure
the pipeline asks for. The one limitation against codex-baseline's otherwise
comparable analysis: it worked from docket entries and the dissent's length
rather than reading the opinion text itself, so the doctrinal weighing leans
more on general knowledge of the emergency docket — which the candidate itself
flags. Process-wise the two are peers; both earn 0.9.

## Leakage: not applicable (forward)

The log's `mode` is `forward` and the cell was genuinely open: prediction
created 2026-08-20, resolution 2026-08-31. I checked for mis-provisioning —
nothing in the log or prose reads this application's own disposition as
already decided. The log has full result capture (`result_capture_coverage`
1.0). The two CourtListener calls are bounded to on-or-before 2026-08-14 and
target the D.C. Circuit docket below (latest `retrieved_doc_date` 2026-08-07);
the one successful `fedcourts query` returned prior granted cert petitions
(`retrieved_doc_date` 2025-09-03) — corpus priors, not case facts. The
candidate's own candor section states the self-imposed date bound and that it
does not know the disposition; that disclosure counts for the cell, not
against it.

## Big case

My independent read is 0.8 (see `evaluation.json`), formed before consulting
the candidate's `big_case_score`.
