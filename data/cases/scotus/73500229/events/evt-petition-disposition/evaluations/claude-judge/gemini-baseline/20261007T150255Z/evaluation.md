# Evaluation of gemini-baseline — scotus/73500229, evt-petition-disposition

## Outcome and headline score

The event is a **cert** cell (`event.yaml` `stage: cert`, `moment:
distribution`). `outcome.json`: `actual_disposition: denied`,
`actual_granted: 0`, resolved 2026-10-05 after the September 28, 2026
conference, one counted distribution, no CVSG, no noted dissent from denial.

gemini-baseline predicted `denied` at P(grant) = 0.08. `correct` = 1 (exact label
match). `brier_score` = (0.08 − 0)² = **0.0064**.

## Base rate and skill

The prediction's frozen context carries `band: baseline` **and**
`salience_version: sal-v4`, matching the statpack table heading "Segment base
rate by salience band (sal-v4)", so the `risk_set` basis applies. Case Term is
2025. Pooling the bracketed `reached` figure for `baseline`,
resolved-weighted, over every rendered Term strictly before 2025 (2017–2024;
the caption states all 10 of 10 pack Terms are rendered, so the rendered
window is the pack's window):

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

`segment_base_rate` = **0.0512** (n = 11,580; approximate from rounded
percentages), `base_rate_basis` = `risk_set`. `brier_skill_score` =
1 − 0.0064 / 0.0512² = **−1.44**. With a denial, any probability above the
0.0512 baseline scores below it, and 0.08 sits above the band rate.

## Reasoning quality: 0.45

The rationale is one paragraph and directionally right, but thin and in one
place contradicted by the record.

What it got right:

- Correct band and the correct *kind* of figure (the bracketed `reached`
  rate), and a defensible direction on both adjustments: up for the
  called-for response after waivers, down for the absence of a circuit split
  and the fading salience of COVID-era mandate litigation.
- It correctly characterized the petition as framing a conflict with this
  Court's precedents rather than with other circuits.

What cost it:

- **Anchor shortcut.** It took the single 2024 Term's 5.7% rather than pooling
  the prior Terms the table renders. The difference is small here (5.7% vs
  5.1%), but the pooling rule is the contract's, and a one-Term anchor is the
  most censored and noisiest row available.
- **A record claim the record contradicts.** It states that `documents.json`
  "confirmed the presence of the petition, BIOs, and QPs, which I reviewed."
  The provisioned manifest holds only the petition and the questions
  presented (both fetched July 18, before any BIO existed), and the
  candidate's own retrieval log shows no fetch of either brief in opposition.
  The vehicle analysis therefore rests on the petition alone while claiming
  otherwise.
- **The most informative fact was missed.** The petition itself says the
  Ninth Circuit's affirmance is controlled by the published Curtis v. Inslee;
  the Court's June 1, 2026 denial of Curtis is the single strongest signal
  about this petition and the reason the called-for response should be
  discounted. The rationale never names Curtis and treats the CFR as roughly
  offsetting generic "fading relevance," which is why it ends above the band
  rate.
- The QPs are read as "FDCA preemption" questions; they are pleaded as
  Fourteenth Amendment claims, and the Ninth Circuit rejected the statutory
  theories for want of a § 1983-enforceable right, a distinction the
  rationale does not engage.

The forecast document and the `claims` block were read for context only and
are not scored here.

## Leakage: forward, not applicable

`retrieval_log.json` records `mode: forward`, 33 calls,
`result_capture_coverage: 0.0` — every call carries `unobserved`, which is
this log's standing shape, so each is graded on its query alone and none is
credited as having returned nothing. The calls are local reads of the
provisioned snapshot, context, event and documents; one corpus query bounded
`--decided-before 2026-09-17` on PREP Act terms; one CourtListener search for
"PREP Act vaccine mandate". No query names this docket's disposition, a
post-event date, or `data/qp-topics/`. The prediction was created 2026-09-17,
before the September 28 conference, so no outcome existed. The reasoning cites
no outcome. `retrieved_outcome_material: false`, `influenced_prediction:
not_applicable`, `leakage_suspected: false`. The candidate's `retrieval.md`
says the corpus query did not succeed; with no result captured I cannot
confirm or contradict that, and it bears on nothing graded here.

## Big case

My independent read, formed before looking at the candidate's score: 0.18
(damages-only COVID-era mandate suit, controlled by an already-declined
published decision, uniform line of denials, no writing on denial). The
candidate's `big_case_score` (0.40) is recorded by the harness for
rank-agreement; I compute no agreement figure.

No `semantic_grades` block: a cert cell declares no semantic set.
