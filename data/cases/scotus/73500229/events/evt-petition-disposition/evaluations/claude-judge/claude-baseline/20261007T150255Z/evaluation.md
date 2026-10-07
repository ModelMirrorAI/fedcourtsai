# Evaluation of claude-baseline — scotus/73500229, evt-petition-disposition

## Outcome and headline score

The event is a **cert** cell (`event.yaml` `stage: cert`, `moment:
distribution`). `outcome.json`: `actual_disposition: denied`,
`actual_granted: 0`, resolved 2026-10-05 after the September 28, 2026
conference, one counted distribution, no CVSG, no noted dissent from denial.

claude-baseline predicted `denied` at P(grant) = 0.04. `correct` = 1 (exact label
match). `brier_score` = (0.04 − 0)² = **0.0016**.

## Base rate and skill

The prediction's frozen context carries `band: baseline` **and**
`salience_version: sal-v4`, and the committed statpack's table heading is
"Segment base rate by salience band (sal-v4)", so the `risk_set` basis
applies. The case's Term is 2025 (frozen `context.term`, docket 25-1327). I
pooled the bracketed `reached` figure for `baseline`, resolved-weighted, over
every rendered Term strictly before 2025 (2017–2024; the caption states the
table renders all 10 of 10 Terms the pack holds, so the rendered window is the
pack's window and the in-code 10-Term lookback reaches no row this table does
not show):

| Term | reached | n |
| --- | ---: | ---: |
| 2024 | 5.7% | 1271 |
| 2023 | 5.9% | 1312 |
| 2022 | 5.8% | 1192 |
| 2021 | 5.6% | 1500 |
| 2020 | 4.5% | 1739 |
| 2019 | 4.6% | 1399 |
| 2018 | 4.6% | 1524 |
| 2017 | 4.7% | 1643 |

`segment_base_rate` = **0.0512** (n = 11,580; approximate because the
rendered percentages are rounded), `base_rate_basis` = `risk_set`.
`brier_skill_score` = 1 − 0.0016 / 0.0512² = **0.39** — the forecast beat the
naive band-rate baseline.

## Reasoning quality: 0.88

What drove the score:

- **Anchor handled exactly as the contract asks.** It matched the band to the
  sal-v4 heading, pooled the bracketed `reached` figure over the prior Terms
  (its 5.1% agrees with my 0.0512), and labelled the relist-0 and circuit cuts
  as terminal context rather than substitute anchors.
- **The decisive adjustment was the right one and was verified.** It found
  that the Ninth Circuit's unpublished memorandum rests entirely on the
  published Curtis v. Inslee, then confirmed from the June 1, 2026 order list
  itself that the Court denied Curtis after one conference with no response
  requested and no writing, and that the same list denied the sibling
  petitions Sweeney and Horsley. Reading the called-for response against that
  backdrop as "one chambers wanting the respondents' account before denying"
  rather than four votes in prospect is the sound inference, and it is what
  happened.
- **Vehicle and merits analysis is specific and correct.** No circuit split
  (every circuit to reach the EUA-versus-licensed theory has rejected it);
  QP1 is a preemption claim recast as due process; QP2 was not the ground of
  decision below; damages-only posture with unreached qualified-immunity and
  state-actor grounds; petition-quality defects named concretely.
- **Information-set discipline.** It identified that the BIOs were not
  provisioned, fetched them as permitted forward retrieval, and disclosed the
  related-case signal as the largest input.

Where it loses points: the CFR multiplier rests on web-sourced "roughly nine
times" literature with no committed figure behind it (the candidate says so
in "Where to discount me"); the write-up is longer than its number needs; and
a small internal inconsistency ("`moment: distribution`" beside "the event
carries no `moment` field") is harmless but sloppy. The forecast document and
the `claims` block were read for context only and are not scored here.

## Leakage: forward, not applicable

`retrieval_log.json` records `mode: forward`, 49 calls, capture coverage 1.0.
The prediction was created 2026-09-17; the petition was pending for the
September 28 conference and was denied October 5, so no outcome existed to
retrieve. I checked for this case's own disposition surfacing anyway: the
fetches of this docket are the two BIOs (Aug 24) and the reply (Sep 14), both
pre-resolution; the order list fetched is June 1, 2026 (Curtis, a different
docket); the docket pages fetched are Nos. 25-1119, 25-1280, 26-220 and
26-268, not this one; the web searches target Curtis, Boysen and CFR
statistics. Nothing names `data/qp-topics/`. The reasoning does not
presuppose the result. `retrieved_outcome_material: false`,
`influenced_prediction: not_applicable`, `leakage_suspected: false`. Related-
case rulings that predate the event are legitimate forward signal, and the
candidate's own disclosure of them is a point for the cell.

## Big case

My independent read, formed before looking at the candidate's score: 0.18. A
damages-only suit over a past COVID-era healthcare-worker mandate, controlled
by a published decision the Court had already declined to review, on theories
every circuit has rejected and with no noted dissent on denial. The
candidate's `big_case_score` (0.35) is recorded by the harness for
rank-agreement; I compute no agreement figure.

No `semantic_grades` block: a cert cell declares no semantic set.
