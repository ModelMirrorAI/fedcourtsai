# Evaluation of gemini-baseline — scotus/73281635, evt-petition-disposition

**Cell.** Cert stage (`event.yaml` `stage: cert`, moment `distribution`), forward mode. Pesavento v. Bolden, No. 25-1146: the City of Chicago officers' petition on whether prejudgment interest is unavailable as a matter of law on noneconomic damages. Outcome: **denied** on the October 5, 2026 order list after the September 28 long conference, with no noted dissent (`outcome.json`: `actual_disposition` denied, `actual_granted` 0, `distribution_count` 2).

**Prediction.** `denied`, P(grant) = 0.07, created 2026-09-17 against the 2026-09-17 snapshot.

## Scores

| Field | Value | How |
| --- | --- | --- |
| `correct` | 1 | `denied` == `denied` |
| `brier_score` | 0.0049 | (0.07 − 0)² |
| `segment_base_rate` | 0.1724 | sal-v4 `elevated`, bracketed *reached* figures, Terms 2017–2024 pooled resolved-weighted (n = 2,810) |
| `base_rate_basis` | `risk_set` | the prediction froze `band: elevated` **and** `salience_version: sal-v4`; the statpack heading is sal-v4 |
| `brier_skill_score` | 0.8351 | 1 − 0.0049 / 0.1724² |
| `reasoning_quality` | 0.55 | see below |

Base-rate detail: the rendered table shows "Most recent 10 of 10 Term(s)", so the rendered window is the pack's window and no divergence from the in-code lookback arises. Pooling the rendered rounded percentages gives 0.1724; the harness's unrounded pool over the same rows gives 0.1722, an immaterial difference I note for the record.

No `vote_accuracy` (cert stage; none predicted in any case), no `judgment_correct`, no `semantic_grades` (no semantic set on a cert event), and `claim_scores` is the harness's.

## What the prediction got right

The call and its direction were right: denial at the first actual conference, no further relist, no CVSG, no separate writing — all borne out. The rationale correctly identifies the two things that decided this petition: the asserted Third/Fourth/Tenth Circuit split rests on a FELA footnote (Poleto), a fact-bound reversal (Gilliam), and an abuse-of-discretion affirmance (White) rather than on any circuit adopting the categorical bar the petition sought, and the BIO's vehicle objection that no Section 1983-specific argument was made below. Both points are accurate to the provisioned petition and BIO. It also noted the response request and the IMLA amicus as the countervailing interest signals.

## What drove the reasoning_quality score

- **Wrong base-rate row.** The rationale anchors on "a baseline reached grant rate of ~13.5% (OT2025)". That is the case's own Term's row, which is a partial live slice that contains this petition; the statpack's own instructions and the scoring rule pool Terms strictly before the case's Term, which gives about 17%. The adjustment direction (downward) was right, but the anchor it was adjusted from was the wrong population. In a forward cell this is a methodological error rather than leakage.
- **Thin engagement.** The entire justification is one paragraph that restates the BIO's characterization of the split and the vehicle problem without testing either against the authorities themselves or the Seventh Circuit opinion reproduced in the appendix. The log shows only greps for "split" in the two briefs; nothing on Gilliam's actual reasoning, the apportionment remand, or why a call-for-response redistribution differs from a post-conference relist.
- **Unsupported attribution.** "Likely spurred by the IMLA amicus brief" is plausible but asserted without basis; the amicus was filed the same day as the waiver, sixteen days before the response request.
- **Plus.** The conclusion and the two load-bearing reasons are sound, and the predicted ancillary path (no relist, no CVSG, no writing) was exactly what happened.

A sound but shallow analysis built on the wrong anchor row: 0.55.

## Leakage

Forward mode per the log (`mode: forward`), confirmed genuine: the petition was pending when the prediction ran and was decided eighteen days later. `result_capture_coverage` is 0.0, so every call is graded on its query: provisioned-file reads, greps on the provisioned briefs, the statpack, and one generic corpus query (denied SCOTUS dispositions decided before 2026-09-17). No web, no MCP, no `data/qp-topics/` path. `retrieved_outcome_material` false, `influenced_prediction` not_applicable, `leakage_suspected` false.

## Big-case read

My own read is 0.25: a recurring but dry remedies question with real municipal dollar stakes (a $7.6M interest award on a $25M verdict, IMLA support) and an institutional petitioner, but no constitutional-liability question, a unanimous published opinion below, and a quiet denial. Formed from the petition, BIO and docket; the predictor's own score sits in its `prediction.json` and I did not use it.
