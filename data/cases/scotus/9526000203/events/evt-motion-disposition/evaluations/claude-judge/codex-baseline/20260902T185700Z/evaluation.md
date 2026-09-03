# Evaluation — codex-baseline, evt-motion-disposition (scotus/9526000203)

This is an **interim** cell (`event.yaml` stage: `interim`): an emergency
application by the Solicitor General to stay the D.C. Circuit's affirmance of a
preliminary injunction against White House ballroom construction. The outcome
is `granted` (`actual_granted` = 1, resolved 2026-08-31, standard basis, with
`interim_signals`: 7 amicus briefs, referred to the Court, response requested).

## Scores

- **correct = 1.** Predicted disposition `granted` matches `actual_disposition`
  `granted` exactly.
- **brier_score = 0.1024** — (0.68 − 1)².
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

The strongest feature is that the analysis is grounded in the primary source:
the candidate located the D.C. Circuit's August 7 opinion in RECAP and read
substantial portions of both the majority (congressional control of federal
property, 40 U.S.C. § 8106 express-authorization holding, the injunction's
below-ground/security carve-outs) and Judge Rao's dissent (standing, 3 U.S.C.
§ 105(d), security equities). The rationale then genuinely weighs both
directions — the response request, federal applicant, conservative dissent,
imminent mandate, and institutional stakes for a grant; the majority's
self-created-harm characterization, the 2028 completion date, and the tailored
security exception against — and explicitly prices the denial-first resolver
convention on mixed relief into the 0.68 complement. The base-rate anchor is
correctly taken from the strictly-prior pool with the floor checked, and the
vacuous response-requested increment is correctly identified from the frozen
context. This is a careful, well-sourced, two-sided forecast whose 0.68 is
argued rather than asserted; it sits a hair below the other strong candidate
only because its headline number ended slightly less calibrated to the
realized grant, which is outcome, not process — the process score reflects
that the marginal reasoning content is comparable.

## Leakage: not applicable (forward)

The log's `mode` is `forward` and the cell was genuinely open: prediction
created 2026-08-20, resolution 2026-08-31. I checked for mis-provisioning —
nothing in the log or prose reads this application's own disposition as
already decided. Beyond that, the candidate self-imposed replay-style
discipline it did not owe: every CourtListener query in the captured log is
bounded `filed_before: 2026-08-15`, and the SCOTUS docket 26A203 search
(similarly bounded) returned nothing. Roughly a third of the calls are
`result_capture: unobserved` (the MCP-side rows; coverage ≈ 0.64) and were
graded on their queries, all of which target the lower courts' pre-application
record. The final log entry is an `other` call whose payload is
`[redacted:fernet-token][redacted:opaque]` — the harness's credential-shaped
scrub at capture, read as removed text per the contract; I note it here for
completeness, not as evidence of anything.

## Big case

My independent read is 0.8 (see `evaluation.json`), formed before consulting
the candidate's `big_case_score`.
