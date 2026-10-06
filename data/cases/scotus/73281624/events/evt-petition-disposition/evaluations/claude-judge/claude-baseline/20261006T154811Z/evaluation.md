# Evaluation of claude-baseline — scotus/73281624, evt-petition-disposition

## Outcome and scores

The cell is **cert** stage (`event.yaml` records `stage: cert`, a petition at the `distribution` moment). The petition in *Cherry Grove Beach Gear, LLC v. City of North Myrtle Beach*, No. 25-1130, was **denied** on the October 5, 2026 order list after the September 28 long conference, with no noted dissent (`actual_disposition: denied`, `actual_granted: 0`, `noted_dissent_from_denial: false`, two distributions).

- `correct` = 1: the candidate predicted `denied`, an exact label match.
- `brier_score` = (0.06 − 0)² = **0.0036**.
- `segment_base_rate` = **0.1724**, basis `risk_set`. The prediction froze `band: elevated` under `salience_version: sal-v4`, matching the heading of the committed `metrics/statpack.md` segment table. I pooled the bracketed `reached` figure for `elevated`, resolved-weighted, over every rendered Term strictly before Term 2025 — OT2017 through OT2024 — giving 484.4 weighted grants over n = 2,810 (17.24%). The caption renders 10 of 10 pack Terms and the pack holds nothing before OT2017, so the in-code lookback and the rendered window coincide; nothing to flag.
- `brier_skill_score` = 1 − 0.0036 / 0.1724² = **0.8789**.
- `vote_accuracy`, `judgment_correct`, `semantic_grades`: not applicable on a cert cell; none written.

## Reasoning quality: 0.85

This is the strongest analysis of the three. The anchor is computed explicitly and correctly (484 of 2,810 weighted, the same pool I used), the version match is checked, and the candidate then does the thing the band pool cannot: it separates the call-for-response redistribution trajectory from a genuine relist and says plainly that it is adjusting by judgment where the pack publishes no cut. The downward case is grounded in the record rather than in the subject matter alone — no split asserted and *Western Star* uncited (both confirmed by the brief in opposition), the "heightened rigor" question not raised below, the specific text of S.C. Code § 5-7-145(B)(3) contemplating an exclusive beach-equipment rental right (quoted in the BIO at its page 6 and 13), the Local Government Antitrust Act damages bar, the abandoned non-antitrust claims, and a fourth argued issue matching no question presented. The upward case is also handled honestly: the call for response after waiver is named as the one strong positive and then correctly treated as largely priced into the elevated band rather than added on top. The uncertainty section says exactly where to discount the forecast. The outcome bore all of it out — a silent denial at the first fully briefed conference.

Small deductions. The claim that the Court's only Parker merits cases since 2010 are the two FTC-brought cases is right but was verified by a search whose top hit was a false positive the candidate had to discard, a minor looseness. "The whole 0.06 is plenary grant" sits in slight tension with a 0.05 conditional summary-route claim; immaterial to the headline but an internal inconsistency. The counsel-quality and Fourth-Circuit-origin points are plausible marginal signals stated as such, fine, but add little. None of this disturbs a careful, well-sourced document.

## Leakage

Forward cell, `mode: forward`. Prediction created 2026-09-17; denial 2026-10-05, so no outcome existed when the cell ran. All 30 calls are `captured` (coverage 1.0). Two CourtListener searches carry legible dates — the decision below (2025-12-23) and a Parker-doctrine opinion search whose newest hit is 2021-04-22 — both long before resolution. One corpus `query` returned recent granted rows unrelated to this case, and the candidate reports its `ranged corpus reads` line. The candidate states it did not look up this docket's own CourtListener record, and the log agrees. One shell call listed the event's `predictions/` directory, a listing in the cell's own run rather than a read of any outcome material. No `retrieved_doc_date` on or after the resolution date, nothing under `data/qp-topics/`, and the reasoning says the conference is eleven days away. `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`.

## Big-case read

My own read is 0.2 (see `big_case.notes`). The candidate's rationale sits inside `prediction.json`, so I could not fully sequence my read before seeing theirs; I formed it from the questions presented, the petition, and the brief in opposition.
