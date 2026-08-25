# Evaluation — codex-baseline, evt-motion-disposition (interim)

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
30 granted ≈ 13.3%, above the pre-registered 50-resolution floor. The
`claim_scores` block over the declared `interim-v1` set is likewise the
harness's. No semantic set is declared on an interim cell, so no
`semantic_grades` block is written.

## Scores

- **correct = 0.** The prediction named `denied`; the Court granted.
- **brier_score = 0.3025** — (0.45 − 1)². The highest probability of the three
  candidates, so the least penalized miss on the panel.
- **vote_accuracy** — omitted: never scored off the merits stage, whatever the
  votes field carries (here it was empty anyway).

## Reasoning quality: 0.72

What the rationale did well:

- Anchored on the correct pool: the strictly-prior OT2024–OT2025 substantive
  slice (225/30, 13.3%), not the pack-wide rate and not a cert rate, and said
  so explicitly.
- Adjusted upward substantially — to 0.45, the panel's highest — on the signals
  that in fact carried the day: the Solicitor General as applicant, the
  same-day response request, heavy amicus participation, and sustained
  briefing. Its structural weighting proved the best calibrated of the three.
- Handled the claims ladder correctly: 0.00 on the vacuous response-request
  increment (the rung had already fired), a well-reasoned 0.78 on referral
  (which occurred, in the disposing order itself), and it surfaced the frozen
  amicus-count discrepancy (context says 6, the snapshot carries 13
  amicus-captioned entries) rather than silently picking a side.
- Was candid about degraded inputs: no filing text provisioned, CourtListener
  throttled, and it said which adjustments that uncertainty suppressed.

What holds the score below the top band: the legal analysis is thin. The
rationale is almost entirely procedural-signal arithmetic — it never engages
the merits posture, Purcell, the status-quo direction of a stay, or the shape
of relief beyond one sentence on the partial-grant collapse. That
disengagement was disclosed (no filings were provisioned), and ex post the
light touch on Purcell served it well, but a rationale that reaches the best
number of the panel partly by declining the substantive analysis earns less
credit for soundness than one that does the analysis and weighs it. The
stated reason to stay below 0.50 — no referral yet on the docket — is also
weak evidence: a referral ordinarily becomes visible at disposition, as it did
here.

## Leakage

Forward cell; the case was genuinely unresolved at prediction time
(2026-08-16 against a 2026-08-24 resolution), so `influenced_prediction` is
`not_applicable`. I confirmed rather than rubber-stamped: no
`retrieved_doc_date` in the log is on or after the resolution, the one
CourtListener call for the First Circuit docket returned HTTP 429 with no
content, the corpus query was a broad prior-application slice, and neither
prose document reads the outcome off anything. One captured call is a
harness-redacted credential-shaped run (`[redacted:fernet-token]`); per the
contract that is removed text, not outcome material, and it is noted in
`leakage.notes` for completeness only.

## Big case

My independent read is 0.97 — formed from the record before consulting the
candidate's own `big_case_score`: a presidential emergency application
against a state over election administration, granted weeks before a federal
midterm, is close to the ceiling of interim-docket significance.
