# Evaluation — claude-baseline, evt-motion-disposition (interim)

## The cell and the outcome

This is an **interim**-stage cell: an application to stay lower-court
injunctions in *Trump v. California* (26A124), filed 2026-07-27 and submitted
to Justice Jackson. On 2026-08-24 the application was **referred to the full
Court and granted** — an unqualified grant on the standard basis
(`actual_disposition: granted`, `actual_granted: 1`). The outcome's
`interim_signals` record `response_requested: true`, `referred_to_court: true`,
and `amicus_briefs: 6`.

Because the cell is interim, the baseline and skill are the harness's:
`segment_base_rate` and `brier_skill_score` are stamped by `stamp-cell` from
the committed statpack's interim section, and `base_rate_basis` stays null
structurally (an application freezes no band). The pack supports a stamp here:
pooling application-Terms strictly before 2026 gives OT2025 (178 resolved
substantive, 16 granted) plus OT2024 (47 resolved, 14 granted) = 225 resolved,
30 granted ≈ 13.3%, above the pre-registered 50-resolution floor — the same
pool this candidate computed for itself. The `claim_scores` block over the
declared `interim-v1` set is likewise the harness's. No semantic set is
declared on an interim cell, so no `semantic_grades` block is written.

## Scores

- **correct = 0.** The prediction named `denied`; the Court granted.
- **brier_score = 0.5625** — (0.25 − 1)².
- **vote_accuracy** — omitted: never scored off the merits stage.

## Reasoning quality: 0.78

This is the most rigorous rationale on the panel, and the score reflects that
even though its number was further from the outcome than codex-baseline's:

- The docket read is detailed and accurate: application number, Circuit
  Justice, the same-day response call, the briefing sequence through the
  August 12 supplemental briefs, the amicus lineup and its lean, and the
  companion application.
- The baseline work is exemplary — the correct strictly-prior pool (225/30,
  13.3%), computed from the section with the floor checked, and carried with
  the pack's own caveats (uneven parse coverage, denial-first mixed orders,
  the scored population sitting higher on the escalation ladder).
- The probability is built transparently: roughly 0.45 for any relief, halved
  for the unqualified-grant collapse, with the sensitivity of the final number
  to that split stated outright. That decomposition is exactly how this event
  should be reasoned about, and it flagged where its inputs were general
  knowledge rather than a committed cut.
- The claims ladder is handled well: 0.02 on the fired response-request rung,
  0.9 on referral (which occurred), and a mechanically argued 0.15 on the
  amicus increment resting on a sharp diagnosis of the counter discrepancy
  (the six singular-captioned "Brief amicus curiae" entries match the frozen
  count; plural "amici" entries are missed) — a diagnosis consistent with the
  outcome's count staying at 6.

Where it lost, given the outcome: both discretionary judgments broke against
it. It rated the merits posture "unusually weak for a government application"
and gave Purcell controlling weight, while the Court granted in full; and its
P(unqualified | any relief) ≈ 0.5 halving — grounded in the plausible
partial-relief shape of a multi-provision EO — cut a defensible ~0.45
"any relief" estimate down to 0.25 when the realized order was unqualified.
It saw the strongest countervailing signal (this Court's recent rate of full
interim relief for the federal government) and discounted it. Sound process,
directionally wrong weights on the two calls that mattered most.

## Leakage

Forward cell; the case was genuinely unresolved at prediction time
(2026-08-16 against a 2026-08-24 resolution), so `influenced_prediction` is
`not_applicable`. Confirmed against the log: the only dated retrieval is a
corpus query whose newest document date is 2026-08-14, the single
CourtListener call failed on HTTP 429 with no content, and nothing in the
prose reads the outcome off anything. The log also records a read of a
committed `prediction.json` from a different case (scotus/73279700),
apparently as a schema/format reference; it is another agent's committed
output rather than this case's outcome material, so it is not leakage —
noted in `leakage.notes` for the record.

## Big case

My independent read is 0.97 — formed from the record before consulting the
candidate's own `big_case_score`: a presidential emergency application
against a state over election administration, granted weeks before a federal
midterm, is close to the ceiling of interim-docket significance.
