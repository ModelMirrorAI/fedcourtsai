# Evaluation — gemini-baseline

## The cell and the outcome

This is an **interim-stage** cell (`event.yaml` stage: `interim`): the disposition
of stay application 26A124, *Trump v. California*, forecast after Justice Jackson
called for a response on the filing date. The Court **granted** the application on
2026-08-24 (`actual_disposition: granted`, `actual_granted: 1`), referring it to
the full Court the same day. gemini-baseline predicted `denied` at probability 0.25,
so `correct = 0` and `brier_score = (0.25 - 1)^2 = 0.5625` — the furthest of the
three candidates from the event.

## Baseline and skill are the harness's

Because the cell is interim, `segment_base_rate` and `brier_skill_score` are
stamped by the harness from the committed statpack, and `base_rate_basis` stays
null structurally (an application freezes no band). For the reader: the statpack's
interim table supports a strictly-prior pool for a Term-2026 application of
Terms 2025 (178 resolved substantive, 16 granted) + 2024 (47, 14) = 30/225 ≈ 13.3%,
which clears the 50-resolution floor, so a stamped rate near 0.133 is expected
rather than a null. `claim_scores` is likewise the harness's (`interim-v1`).
Note this candidate's frozen context differs from the other two: it was
provisioned a **truncated** 2026-07-28 snapshot (`amicus_briefs: 0`,
`cutoff: 2026-07-28`), so its increment claims condition on the state at the
moment the response was requested, not on the 2026-08-16 state the others saw.

## Reasoning quality: 0.45

Strengths:

- **It anchored on the right pooled rate** (13.3% over Terms 2024–2025) and
  correctly recognized that a government applicant seeking to lift a nationwide
  injunction historically runs well above that baseline.
- The referral call (0.95, realized) and the expectation of heavy amicus interest
  (realized: thirteen filings) were correct reads of the case's shape, formed from
  a much thinner snapshot than the other candidates had.

Weaknesses:

- **The rationale is thin** — five sentences of analysis against claude-baseline's
  structured brief. The step from a "typical executive-branch success rate" down
  to 0.25 rests on two invocations, one of which is misapplied: the **major
  questions doctrine** is a canon about agency statutory authority on the merits,
  not a stay-stage equity, and its presence here reads as pattern-matching rather
  than analysis. Purcell was at least the right register, though the Court did not
  share the reading.
- **A mislabeled exclusion rule.** It says Term 2026 is excluded because it "has
  not cleared the 50-application floor." The registered rule excludes the case's
  own Term regardless; the floor governs whether the *prior* pool is usable at
  all. The pooled number was right, so this cost nothing here, but the stated rule
  would generalize wrongly.
- **The caption is inverted** ("State of California, et al. v. Trump, et al.") —
  the applicant is the President; California leads the respondents. Cosmetic, but
  of a piece with the general looseness.
- 0.25 sits below even its own premises: having granted that the applicant class
  runs at a majority success rate and that the case would be treated as major, a
  landing point below the midpoint of baseline and that rate needed more argument
  than two doctrinal gestures.

## Leakage

Forward mode, run 2026-08-20, resolved 2026-08-24: no outcome existed at
retrieval time. The one hosted web search names the case and the First Circuit
docket; its results are uncaptured, so it is graded on its query, which seeks
lower-court context rather than a disposition, and the prose shows background
(EO 14399, mail-in voting) with no trace of a known outcome — it predicted denial
against an actual grant. `not_applicable`.

One caveat recorded in the cell's `flags.json` rather than against the candidate:
a forward cell provisioned a truncated 2026-07-28 snapshot but retrieving freely
on 2026-08-20 can observe docket developments (the amicus wave, completed
briefing) that postdate its frozen conditioning state, which makes its
`amicus-increment: 0.99` closer to an observation than a forecast. That is a
provisioning-shape question for a maintainer, not misconduct — forward retrieval
is unrestricted by design.
