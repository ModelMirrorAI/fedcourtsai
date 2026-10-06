# Evaluation of codex-baseline — scotus/73281624, evt-petition-disposition

## Outcome and scores

The cell is **cert** stage (`event.yaml` records `stage: cert`, a petition at the `distribution` moment). The petition in *Cherry Grove Beach Gear, LLC v. City of North Myrtle Beach*, No. 25-1130, was **denied** on the October 5, 2026 order list after the September 28 long conference, with no noted dissent (`actual_disposition: denied`, `actual_granted: 0`, `noted_dissent_from_denial: false`, two distributions).

- `correct` = 1: the candidate predicted `denied`, an exact label match.
- `brier_score` = (0.08 − 0)² = **0.0064**.
- `segment_base_rate` = **0.1724**, basis `risk_set`. The prediction froze `band: elevated` under `salience_version: sal-v4`, matching the heading of the committed `metrics/statpack.md` segment table. I pooled the bracketed `reached` figure for `elevated`, resolved-weighted, over every rendered Term strictly before Term 2025 — OT2017 through OT2024 — giving 484.4 weighted grants over n = 2,810 (17.24%). The caption renders 10 of 10 pack Terms and the pack holds nothing before OT2017, so the in-code lookback and the rendered window coincide; nothing to flag.
- `brier_skill_score` = 1 − 0.0064 / 0.1724² = **0.7847**.
- `vote_accuracy`, `judgment_correct`, `semantic_grades`: not applicable on a cert cell; none written.

## Reasoning quality: 0.80

A careful, well-grounded analysis. The anchor is computed exactly from the pack's risk-set counts (484 / 2,810, 17.22%) and correctly identified as the reached-band figure rather than the terminal one; the candidate also reads the relist and CVSG cuts for shape only, declining to multiply them in as independent likelihoods, which is the right discipline. On the substance it reads the two distributions correctly as a call-for-response interruption and a routine post-BIO redistribution, credits the response request as a real positive, and then grounds the downward adjustment in the record: no concrete conflicting appellate holding, the Fourth Circuit applying its own *Western Star* precedent, the City's answer that the statute authorizes displacing competition and the dispute is only over who the authorized exclusive provider is (confirmed by the BIO at its pages 13–14), the preservation objection to the "heightened rigor" question, and the damages limitation. It is notably careful to treat the respondent's preservation point as an objection rather than an adjudicated fact, and to separate abandonment of the non-antitrust claims from the preserved antitrust issue. The forecast landed on the correct label and the outcome matched the modal path it described.

Deductions. The document spends a good deal of its length on information-boundary and provenance disclaimers that, while honest, displace analysis; the merits discussion is somewhat less sharp than it could be on why the specific statutory text defeats the petition's *Phoebe Putney* framing. The probability of 0.08 is a little less of a discount than the record supported — the candidate itself calls the adjustment "judgmental" — and the 12% conditional summary-route figure is high for a petition with no intervening authority identified, a point the candidate concedes. Both external precedent lookups failed and the candidate rightly relied on the provisioned filings, so nothing was independently verified beyond the record. Sound throughout, slightly less decisive than the best analysis on this cell.

## Leakage

Forward cell, `mode: forward`. Prediction created 2026-09-17; denial 2026-10-05, so no outcome existed when the cell ran. 31 calls, 30 `captured` and one `unobserved`: a web fetch of the petition PDF's own supremecourt.gov URL. Graded on its query, that call names the March 2026 petition filing, a pre-decision document, and the candidate discloses that it returned no usable content. Two CourtListener opinion searches for *Phoebe Putney* returned one wrong hit and one empty result. No query reached for this docket's disposition, no `retrieved_doc_date` is on or after the resolution date, and nothing was read under `data/qp-topics/`. The candidate states it neither sought nor learned the disposition, consistent with the log. `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`.

## Big-case read

My own read is 0.2 (see `big_case.notes`). The candidate's rationale sits inside `prediction.json`, so I could not fully sequence my read before seeing theirs; I formed it from the questions presented, the petition, and the brief in opposition.
