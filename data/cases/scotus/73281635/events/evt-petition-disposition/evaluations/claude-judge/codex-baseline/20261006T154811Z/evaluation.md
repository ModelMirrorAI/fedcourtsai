# Evaluation of codex-baseline — scotus/73281635, evt-petition-disposition

**Cell.** Cert stage (`event.yaml` `stage: cert`, moment `distribution`), forward mode. Pesavento v. Bolden, No. 25-1146: whether prejudgment interest is unavailable as a matter of law on noneconomic damages, arising from a Section 1983 wrongful-conviction verdict against Chicago officers. Outcome: **denied** on the October 5, 2026 order list after the September 28 long conference, no noted dissent (`outcome.json`: `actual_disposition` denied, `actual_granted` 0, `distribution_count` 2).

**Prediction.** `denied`, P(grant) = 0.10, created 2026-09-17 against the 2026-09-17 snapshot.

## Scores

| Field | Value | How |
| --- | --- | --- |
| `correct` | 1 | `denied` == `denied` |
| `brier_score` | 0.01 | (0.10 − 0)² |
| `segment_base_rate` | 0.1724 | sal-v4 `elevated`, bracketed *reached* figures, Terms 2017–2024 pooled resolved-weighted (n = 2,810) |
| `base_rate_basis` | `risk_set` | the prediction froze `band: elevated` **and** `salience_version: sal-v4`; the statpack heading is sal-v4 |
| `brier_skill_score` | 0.6635 | 1 − 0.01 / 0.1724² |
| `reasoning_quality` | 0.84 | see below |

Base-rate detail: the rendered table shows "Most recent 10 of 10 Term(s)", so the rendered window is the pack's window and no divergence from the in-code lookback arises. Pooling the rendered rounded percentages gives 0.1724 (the predictor's own 17.24% is the same computation); the harness's unrounded pool gives 0.1722, immaterial.

No `vote_accuracy` (cert stage), no `judgment_correct`, no `semantic_grades` (no semantic set on a cert event), and `claim_scores` is the harness's.

## What the prediction got right

Denial at the first actual conference with no further distribution, no CVSG, and no separate writing: every element of the forecast path was borne out. The rationale pools the right base-rate rows (Terms 2017–2024, excluding the case's own Term and 2026, and declining to substitute the terminal figures), then adjusts downward for reasons that are accurate to the record: the Third Circuit "authority" is Poleto dicta in a FELA case; White v. Chafin is an abuse-of-discretion affirmance, which the candidate verified by reading the Tenth Circuit opinion through CourtListener; and the question as framed spans all of federal law while the BIO's preservation point goes to the narrower Section 1983 question. Its treatment of Gilliam is the most careful of the three candidates: it read the passage and concluded the Fourth Circuit's reasoning is less uniformly favourable to respondent than the BIO suggests, leaving a genuine but narrow difference in approach, which is a fair reading. It correctly distinguished the response-request redistribution from an ordinary post-conference relist, and treated the BIO's forfeiture argument as advocacy rather than a found fact.

## What drove the reasoning_quality score

- **Right anchor, right adjustment logic, verified authorities.** The two cited opinions were checked against their text rather than taken from the briefs' characterizations, and the limits of what was checked (Poleto not independently verified, reply and amicus not read) are stated.
- **Minor misreading of the event record.** The rationale says the event "has no express stage or moment"; `event.yaml` carries `stage: cert` and `moment: distribution`. The conclusion drawn (ordinary cert-disposition contract) is right anyway, so this is a slip in describing the inputs, not in the analysis.
- **Judgmental final step.** Moving from 17% to 10% is described candidly as a judgmental adjustment rather than a fitted ratio, which is honest, but the reasoning gives no sense of how much each negative factor is worth. The outcome suggests the downward adjustment, if anything, could have been larger, though a 10% call on a called-for-response paid petition with municipal amicus support is defensible.
- **Prose.** Dense and at times procedural (tooling notes about the uv cache belong in `tooling.json`), but complete and well sourced to page ranges.

A careful, well-verified analysis with one small input-description error: 0.84.

## Leakage

Forward mode per the log (`mode: forward`), confirmed genuine: the petition was pending on 2026-09-17 and decided 2026-10-05. `result_capture_coverage` 0.96. The single `web-search` row is unobserved and is graded on its two queries, which are precedent lookups (White v. Chafin; Poleto) and not this petition. The CourtListener calls (captured) fetched the 2017 White opinion and the 2023 Gilliam opinion, both prior precedent. One shell command contained `find data -name AGENTS.md -not -path 'data/qp-topics/*'`: the forbidden path appears only inside an exclusion pattern, so nothing from that tree could surface; I record it for transparency and grade it clean. `retrieved_outcome_material` false, `influenced_prediction` not_applicable, `leakage_suspected` false.

## Big-case read

My own read is 0.25: a recurring but dry remedies question with real municipal dollar stakes (a $7.6M interest award on a $25M verdict, IMLA support) and an institutional petitioner, but no constitutional-liability question, a unanimous published opinion below, and a quiet denial. Formed from the petition, BIO and docket; the predictor's own score sits in its `prediction.json` and I did not use it.
