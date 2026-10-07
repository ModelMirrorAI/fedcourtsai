# Evaluation of codex-baseline — scotus/73500229, evt-petition-disposition

## Outcome and headline score

The event is a **cert** cell (`event.yaml` `stage: cert`, `moment:
distribution`). `outcome.json`: `actual_disposition: denied`,
`actual_granted: 0`, resolved 2026-10-05 after the September 28, 2026
conference, one counted distribution, no CVSG, no noted dissent from denial.

codex-baseline predicted `denied` at P(grant) = 0.025. `correct` = 1 (exact label
match). `brier_score` = (0.025 − 0)² = **0.000625**.

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
percentages — the candidate's own 0.0512, n = 11,580 is the same
calculation), `base_rate_basis` = `risk_set`. `brier_skill_score` =
1 − 0.000625 / 0.0512² = **0.76**, the best skill of the three candidates.

## Reasoning quality: 0.84

What drove the score:

- **Anchor done exactly to the contract**, with the pooling shown as a table,
  the frozen band kept rather than reclassified, and the terminal relist and
  CVSG cuts explicitly labelled descriptive rather than prospective.
- **The right decisive fact, properly sourced and properly bounded.** It
  recovered the un-provisioned BIOs and reply from the snapshot's own URLs,
  found in the BIOs that the Court denied Curtis v. Inslee on June 1, 2026,
  recognized that the petition itself names Curtis as controlling its
  affirmance, and weighted that above the called-for response. It then said
  plainly that it used the denial "as reported in the pre-decision briefs"
  and did not independently verify it — honest about the evidentiary status
  rather than overstating it.
- **Vehicle analysis is concrete**: no asserted split, preservation
  objections, qualified immunity, the private respondents' state-actor
  defense, and the reply's answers to each, all with page cites. It treats
  respondents' assertions as advocacy, not findings.
- **Information-set discipline is explicit and matches the log**: the
  retrieval note lists every external request, states that none sought this
  petition's disposition, and the captured log agrees.

Where it loses points relative to the strongest possible rationale: it did
not verify the Curtis denial or check the sibling petitions (Boysen, Brock,
Boyd) whose status bears on the hold/relist path, so its related-case picture
is thinner than it could have been; and the prose spends some space on
methodological disclaimers that do not move the number. Neither is an error.
The forecast document and the `claims` block were read for context only and
are not scored here.

## Leakage: forward, not applicable

`retrieval_log.json` records `mode: forward`, 27 calls, capture coverage
0.93. The prediction was created 2026-09-17; the petition was pending for the
September 28 conference and was denied October 5, so no outcome existed to
retrieve. The external calls are direct fetches of this docket's two BIOs
(Aug 24) and reply (Sep 14), pre-resolution filings whose URLs sit in the
provisioned snapshot. The two `unobserved` web-search rows carry the State
BIO's URL as their query and are graded on that query, which names a
pre-resolution document and not a disposition. Nothing names
`data/qp-topics/`. The reasoning does not presuppose the result; the Curtis
denial it leans on is a different docket dated June 1, 2026 — legitimate
forward signal, disclosed by the candidate. `retrieved_outcome_material:
false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`.

## Big case

My independent read, formed before looking at the candidate's score: 0.18
(damages-only COVID-era mandate suit, controlled by an already-declined
published decision, uniform line of denials, no writing on denial). The
candidate's `big_case_score` (0.45) is recorded by the harness for
rank-agreement; I compute no agreement figure.

No `semantic_grades` block: a cert cell declares no semantic set.
