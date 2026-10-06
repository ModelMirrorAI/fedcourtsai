# Evaluation of gemini-baseline — scotus/73281624, evt-petition-disposition

## Outcome and scores

The cell is **cert** stage (`event.yaml` records `stage: cert`, a petition at the `distribution` moment). The petition in *Cherry Grove Beach Gear, LLC v. City of North Myrtle Beach*, No. 25-1130, was **denied** on the October 5, 2026 order list after the September 28 long conference, with no noted dissent (`actual_disposition: denied`, `actual_granted: 0`, `noted_dissent_from_denial: false`, two distributions).

- `correct` = 1: the candidate predicted `denied`, an exact label match.
- `brier_score` = (0.05 − 0)² = **0.0025**.
- `segment_base_rate` = **0.1724**, basis `risk_set`. The prediction froze `band: elevated` under `salience_version: sal-v4`, and the committed `metrics/statpack.md` segment table's heading is `sal-v4`, so the frozen band resolves. I pooled the bracketed `reached` figure for `elevated`, resolved-weighted, over every rendered Term strictly before the case's Term 2025 — OT2017 through OT2024, eight rows — giving 484.4 weighted grants over n = 2,810 (17.24%). The table caption renders 10 of 10 pack Terms, and the pack holds nothing earlier than OT2017, so the in-code ten-Term lookback and the rendered window pool the same eight rows; no window divergence to flag.
- `brier_skill_score` = 1 − 0.0025 / 0.1724² = **0.9159**.
- `vote_accuracy`, `judgment_correct`, `semantic_grades`: not applicable on a cert cell; none written.

## Reasoning quality: 0.60

What the candidate got right. It anchored on the correct figure (about 17% for the elevated reached-band pool), read the two distributions correctly as a call-for-response interruption followed by the routine post-BIO redistribution rather than a true relist, identified the absence of any asserted circuit split (the brief in opposition indeed says the petition "does not contend that the lower courts are split" and does not even cite the Fourth Circuit's own *Western Star* precedent), and judged the beach-rental dispute a poor vehicle. All of that is sound and the probability it produced was the best calibrated of the three.

What holds the score down. The document is a single paragraph and the analysis is thin relative to what the record offered. It does not weigh the call for a response after the City's waiver as the genuine positive signal it is, nor explain why that signal is already priced into the band anchor. It does not engage the brief in opposition's vehicle arguments — the specific statutory text of S.C. Code § 5-7-145(B)(3) authorizing an exclusive beach-equipment rental right, the preservation objection to the "heightened rigor" question, the Local Government Antitrust Act damages bar, or the abandonment of the non-antitrust claims — any of which would have grounded the "significantly downward" adjustment in something more than the localized subject matter. The adjustment from 17% to 5% is asserted rather than argued. The analysis is correct in direction and unobjectionable in content, but it is a sketch.

## Leakage

Forward cell, `mode: forward` in the staged log. The prediction was created 2026-09-17; the petition was denied 2026-10-05, so the outcome did not exist when the cell ran. All 36 logged calls are `unobserved` (coverage 0.0), the engine's standing shape, so I graded each on its query. The only external retrieval was a CourtListener search for the Fourth Circuit opinion by caption and a read of that opinion, decided 2025-12-23 — the decision below, not outcome material — plus a shell script aimed at the same opinion. No query reached for this docket's SCOTUS disposition, no `retrieved_doc_date` is on or after the resolution date, and nothing was read under `data/qp-topics/`. The reasoning treats the September 28 conference as upcoming. `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`.

## Big-case read

My own read is 0.2 (see `big_case.notes`). The candidate's rationales sit inside `prediction.json`, so I could not fully sequence my read before seeing theirs; I formed it from the questions presented, the petition, and the brief in opposition.
