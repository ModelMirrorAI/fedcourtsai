# Evaluation — claude-baseline — scotus/9526000203 evt-brief-response-disposition

## Stage and ownership of the numbers

This is an **interim** cell (`event.yaml` stage: `interim` — the government's
application 26A203 to stay the modified preliminary injunction in the White
House ballroom litigation). The outcome is `granted` (`actual_granted` = 1),
resolved 2026-08-31: the application, presented to the Chief Justice and by him
referred to the Court, was granted, with the injunction stayed pending the
filing and disposition of a cert petition. The Chief Justice, joined by
Justices Sotomayor, Kagan, and Jackson, dissented.

On an interim cell the baseline and skill are the harness's, not mine:
`segment_base_rate` and `brier_skill_score` are stamped by `stamp-cell` from
the committed statpack's interim section, and `base_rate_basis` stays null
structurally (the interim pool is no salience-band product). For the reader of
the stamped number: at this evaluation's pack vintage the interim section's
strictly-prior pool for a Term-2026 application is Terms 2025 (226 resolved, 17
granted) and 2024 (70 resolved, 14 granted) — 296 resolved, 31 granted, ≈10.5%,
which clears the pre-registered floor of 50 resolved, so a stamped rate should
exist. `claim_scores` (the `interim-v1` four-claim set) is likewise computed in
code; I score none of it. `vote_accuracy` is omitted — votes are never scored
off the merits stage.

## Accuracy

The prediction called `granted` at **0.72**, the highest probability of the
three candidates on the correct side. `correct` = 1; Brier = (0.72 − 1)² =
**0.0784**. My elicited values; the harness restamps both.

## Reasoning quality: 0.88

The strongest parts of this rationale:

- **Anchor discipline.** It pooled the statpack's strictly-prior substantive
  slice (quoting the pack as committed at its run date: 225 resolved, 30
  granted, 13.3%), checked the pre-registered floor, excluded its own Term's
  row, and carried the section's caveats (denial-first collapse, uneven parse
  coverage, the escalation-ladder selection gap) rather than just citing the
  number.
- **Sound adjustment structure.** The upward move from ~13% to 0.72 was argued
  on the right axes: the applicant class (SG-filed contested applications
  granted at far above the pooled rate in recent Terms), the escalation posture
  (response called for within a day on a fuse keyed to the D.C. Circuit's
  self-stay and mandate date), and the fit with the Court's revealed stay-stage
  preferences on separation-of-powers claims, with Judge Rao's dissent as the
  merits roadmap. It also argued the other side honestly (two lower-court
  losses, the respondent's concrete irreparable-harm story, partial-grant
  collapse) and stated a calibrated range (0.60–0.80).
- **Forecast texture that resolved well.** The forecast document called the
  referral with the standard recital (it happened, on the exact "by him
  referred to the Court" phrasing), an unqualified grant (it was), and noted
  dissents from "two to three of Justices Sotomayor, Kagan, and Jackson" — the
  actual dissent was exactly those three plus the Chief Justice. The timing
  call (order by or shortly after August 21) was met halfway: the Chief Justice
  entered an interim stay August 21 and the full Court granted August 31.

The deduction: the amicus measurement analysis, though impressively deep (it
read the pipeline's signal-parsing source to reason about the counter),
concluded with high confidence that the resolution-time amicus count would
stay 0 because the docket's entry style "never" carries the phrase "amicus
curiae". The resolved outcome records `amicus_briefs: 7`, and the resolved
docket's entries read "Brief amicus curiae … filed" — the over-general "never"
was wrong, even if the snapshot's pre-acceptance wording plausibly read
"submitted" at the time. The candidate hedged appropriately ("mostly a
measurement call… discount accordingly") and flagged it as data-quality, which
is the right behavior; the claim's score itself is the harness's, and this
enters my grade only as a soundness point about one confident sub-conclusion.

## Leakage: none (forward)

Mode `forward`, and genuinely so — predicted 2026-08-20, resolved 2026-08-31,
so no outcome existed to leak. I confirmed rather than rubber-stamped: the log
(coverage 1.0, all captured) shows the statpack read, one corpus query that
returned only extension grants, and CADC docket retrieval for 26-5123 whose
latest document date is 2026-08-07 (the court of appeals judgment — legitimate
pre-decision signal). Nothing sought this application's disposition or
post-cutoff SCOTUS docket state, and the reasoning reads nothing off a decided
outcome. `influenced_prediction` = `not_applicable`.

## Semantic grades

None — an interim event declares no semantic set, so no `semantic_grades`
block is written.
