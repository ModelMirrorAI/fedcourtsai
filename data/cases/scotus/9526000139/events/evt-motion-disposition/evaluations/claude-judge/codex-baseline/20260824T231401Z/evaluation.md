# Evaluation — codex-baseline, evt-motion-disposition (interim)

## The cell and what is scored

This is an **interim**-stage cell (`event.yaml` stage: `interim`): a
stay application at the arrival moment in *Alabama, et al. v. California, et
al.* The outcome resolved **denied** on 2026-08-24 with `actual_granted = 0`
(`disposition_basis: standard`; the realized escalation signals were response
requested, referral to the Court, and two amicus briefs).

`segment_base_rate` and `brier_skill_score` are the **harness's** on an
interim cell — `stamp-cell` pools the statpack's interim section over
application-Terms strictly before OT2026 — so I wrote neither, and
`base_rate_basis` stays null structurally (the interim pool is no salience-band
product; this prediction's frozen `context.band` is null, the ordinary interim
shape, so no flag). For the reader: the committed statpack's strictly-prior
pool is OT2025 (178 resolved substantive applications, 16 granted) plus OT2024
(47 resolved, 14 granted) — 225 resolved, 30 granted, ≈ 13.3%, clearing the
50-case floor — so a stamped null would indicate the pack changed under the
stamp. `claim_scores` is likewise the harness's (`interim-v1`), and
`vote_accuracy` is omitted: interim votes are elicited, never scored.

## Scores

- **correct = 1.** Predicted `denied`; actual `denied`. Exact label match.
- **brier_score = 0.1681.** `(0.41 - 0)**2`.
- **reasoning_quality = 0.85.**

## What drove reasoning_quality

The rationale is disciplined and genuinely evidence-driven. Strengths: it
pooled the statpack baseline correctly (225/30, 13.3%, floor stated); it did
real retrieval work on the lower-court record, pulling the First Circuit's
July 25 order and its partial dissent, and built the case-specific analysis on
what it found — in particular the observation that even the dissent would have
granted only *partial* relief and found no substantive defense of the Postal
Service provisions. Crucially, it understood the resolver: the scored event is
an *unqualified* grant and a mixed order reads denial-first, so the
substantial partial-relief mass belongs on the denied side — that is the
analytical move the outcome vindicated. It also honestly named its main
blind spot (no application or response text provisioned).

What keeps it below the top of the range: the net number, 0.41, sits three
times above the 13.3% baseline — a large upward adjustment resting mostly on
attention signals (same-day response request, stakes, a partial dissent) that
the statpack itself warns are not conditioned into the rate; the outcome
suggests the adjustment overshot, though the direction of every qualitative
argument it made (partial relief likelier than full; the parallel federal
application reducing this application's independent need) pointed toward
denial. A tighter link between its own arguments and its final number would
have earned more.

## Leakage

Forward mode, confirmed against the log: the prediction was created
2026-08-20, before the 2026-08-24 resolution, so no outcome existed to
retrieve. Every CourtListener call is date-capped at or before the 2026-07-30
cutoff, all queries target the lower-court dockets rather than this
application's disposition, and the retrieval note states no web search and no
disposition lookup was run. Nothing in the reasoning reads as already-decided.
`influenced_prediction = not_applicable`, `leakage_suspected = false`.

## Big case

My independent read is 0.9 (formed from the case posture: a twelve-state
application beside the Solicitor General's parallel one, seeking to stay a
nationwide injunction against a presidential election-administration order
months before the midterms). Recorded in `big_case`; no agreement number is
computed here by design.
