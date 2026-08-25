# Evaluation — codex-baseline, evt-motion-disposition (scotus/9526000139)

## The cell and the outcome

This is an **interim**-stage cell (`event.yaml` stage: `interim`): stay
application 26A139, Alabama, et al. v. California, et al., submitted to
Justice Jackson 2026-07-29, seeking a stay of the D. Mass. nationwide
injunction against the President's election-administration executive order.
The outcome records `actual_disposition: denied`, `actual_granted: 0`,
resolved 2026-08-24. The docket text shows the shape of that denial: the
Court **granted** the full stay on the Solicitor General's companion
application 26A124 (per curiam, Sotomayor joined by Kagan and Jackson
dissenting) and denied this duplicative states' application **as moot**. I
read `actual_granted` as recorded; the denial-first/ungranted reading of a
moot denial is the registered resolver's, and the scored axis is this
application's own disposition.

Because the cell is interim, `segment_base_rate` and `brier_skill_score` are
the **harness's**, stamped by `stamp-cell` from the committed statpack, and
`base_rate_basis` stays null structurally (the interim pool is no salience-band
product). For the reader: the committed statpack's interim table currently
supports the strictly-prior pool — OT2024 (47 resolved, 14 granted) plus
OT2025 (178 resolved, 16 granted) = 225 resolved, 30 granted ≈ 13.3%, above
the 50-resolved floor — so I expect a stamped rate rather than a null.
`claim_scores` is likewise the harness's (`interim-v1` set); nothing here
estimates it.

## Scores

- **`correct` = 1.** Predicted `denied`; actual `denied`. Exact label match.
- **`brier_score` = 0.1681** — (0.41 − 0)².
- **`reasoning_quality` = 0.85.**

## What drove the reasoning grade

This is disciplined, well-sourced forward work. The candidate anchored on the
correct strictly-prior statpack pool (225/30, 13.3%) and stated the floor. It
then did real retrieval: it located the First Circuit docket (26-1774), read
the federal defendants' emergency stay motion, and — decisively — retrieved
the July 25 First Circuit order and its **partial dissent**, all with queries
date-bounded to the 2026-07-30 cutoff. From that primary material it built the
argument that matters for this event's semantics: the scored claim is an
*unqualified* grant, the registered resolver reads a mixed order denial-first,
the appellate dissent itself would have granted only partial relief, and "a
separate federal application could also reduce the need to grant this
intervenor-state application independently." That last channel is very nearly
what happened — relief issued on the companion 26A124 and this application was
denied as moot — so the analysis identified the correct mechanism, not just
the correct label. Honest uncertainty accounting (the missing application and
response text) rounds it out.

What holds it below the top of the range: the final number (0.41) put nearly
even odds on an unqualified grant of *this* application even while the
candidate's own analysis — partial-relief risk plus the parallel federal
application — argued that a large share of the "applicants win" mass would
resolve as ungranted here. Its sibling analysis drew that inference through to
a lower number; this one stopped partway. A modest calibration criticism, not
a soundness one.

The `predicted_reasoning.md` forecast (referral, rising amicus count,
disposition within about a week of the response — referral and amici both
realized, timing close: resolved three weeks after briefing) was read for
context only and is not scored, per the contract.

## Leakage

Forward mode, and genuinely so: the prediction was created 2026-08-20, four
days before the application resolved, so no outcome existed to leak. The log
confirms it — every CourtListener call is bounded at or before the cutoff, no
`retrieved_doc_date` is at or after 2026-08-24, no web search appears, and
nothing touches `data/qp-topics/`. `influenced_prediction` = `not_applicable`.

## Not written, and why

- `segment_base_rate`, `brier_skill_score`, `base_rate_basis` — harness's on
  an interim cell (above).
- `vote_accuracy` — never scored off a merits stage; the prediction noted no
  votes anyway.
- `judgment_correct` — null; no judgment axis on an interim cell.
- `semantic_grades` — no block: an interim event declares no semantic set.
- `claim_scores` — harness-computed (`interim-v1`).
