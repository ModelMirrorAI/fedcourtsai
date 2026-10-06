# Evaluation of claude-baseline — Gasper v. Wisconsin, No. 25-1191 (evt-petition-disposition)

## Cell and outcome

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`). The petition was **denied on 2026-10-05** after the September 28 long conference, with no noted dissent (`outcome.json`: `actual_disposition` `denied`, `actual_granted` 0, `noted_dissent_from_denial` false, two distributions under `dist-v2`). The docket: petition filed April 14, Wisconsin waived April 21, distributed May 5 for the May 21 conference, response requested May 8, BIO June 1, one amicus June 8, redistributed June 17 for September 28, denied October 5.

## Scores

| field | value | how |
| --- | --- | --- |
| `correct` | 1 | `denied` == `denied` |
| `brier_score` | 0.0064 | (0.08 − 0)² |
| `segment_base_rate` | 0.1724 | elevated band, `sal-v4`, bracketed `reached` figures pooled resolved-weighted over Terms 2017–2024 (n = 2810) |
| `base_rate_basis` | `risk_set` | the prediction froze `band: elevated` with `salience_version: sal-v4`, and the statpack table heading is `sal-v4` |
| `brier_skill_score` | 0.785 | 1 − 0.0064 / 0.1724² |
| `reasoning_quality` | 0.90 | below |

Base-rate detail. The prediction's frozen `context` carries both `band` (`elevated`) and `salience_version` (`sal-v4`), Term 2025, so the risk-set basis applies. The "Segment base rate by salience band (sal-v4)" table renders 10 of 10 Terms; the Terms strictly before 2025 that carry data are 2017–2024. Pooling the bracketed `reached` rate × `n` across those eight rows: 484.4 weighted grants over 2810 weighted resolved = 0.17238. The in-code ten-Term lookback is shortened by the pack's coverage to the same eight Terms, so there is no window divergence to flag. `vote_accuracy` is omitted (cert stage). No `semantic_grades` (cert event). `claim_scores` and `process_version` are the harness's.

## What the prediction got right and wrong

Right: the label, the anchor (its own pooled table reproduces 17.2% over 2017–2024, n = 2810, with a five-Term alternative shown beside it), and the structure of the adjustment. It identifies the 28 U.S.C. § 1257(a) finality problem as the single largest driver, cites Florida v. Thomas as the near-identical posture, and works through why none of the Cox Broadcasting exceptions fits comfortably. It adds the alternative-ground problem (the two Wisconsin dissenters would not have suppressed either, on good faith or on independent probable cause), the record problem on subjective expectation of privacy, and the petition's own weaknesses (two of three questions not decided below, no citation of the most favorable recent circuit authority, counsel without Supreme Court experience visible on the docket). It then credits the real upward signals: a conceded and deepening split, a call for a response after waiver, an amicus from experienced counsel. It correctly reads the two distributions as a CFR cycle rather than a relist, which the first-conference denial bears out.

Its one retrieval beyond the record, the Seventh Circuit's August 20, 2026 decision in United States v. Braun, was used well: as forward signal that the split had widened to six circuits, and as an illustration of the "CyberTip alone supplies probable cause" route that makes a petitioner's private-search win unlikely to matter. That is legitimate forward material predating the snapshot and it was disclosed in both `reasoning.md` and `retrieval.md`.

Weaknesses, minor. The 8% sits a little above the other low number on this cell and the candidate explains why (the strength and maturity of the split pulls back up), which is a defensible calibration rather than a flaw. The reporter citations for the Fourth and Eleventh Circuit decisions are taken from the BIO and from Braun; I did not verify them and they do not bear on the grade. The uncertainty section is unusually honest about where the forecast could be wrong (a Justice eager to reach the question reading Cox generously; an undetected pending companion petition).

## Reasoning quality: 0.90

The most complete analysis on the cell: correct anchor, the right main driver with the controlling authority named, cumulative vehicle problems, fair weight to the upward signals, one well-used piece of forward retrieval, and candid uncertainty. Scored on soundness; the silent denial at the first full conference is what this analysis said the modal outcome would be.

## Leakage

`mode` forward; `retrieved_outcome_material` false; `influenced_prediction` not_applicable; `leakage_suspected` false. The prediction was created 2026-09-16 from the 2026-09-15 snapshot, when the petition stood distributed for the 2026-09-28 conference, so the case was genuinely open; not a mis-provisioned decided case. Log: 41 calls, `result_capture_coverage` 1.0, `throttled_calls` 0. Twenty-six shell calls read the prompt, schemas, the provisioned record, and the statpack, and ran one `fedcourts query` with structured filters (disclosed with its `ranged corpus reads` line). Nine CourtListener searches on topical terms and companion-case names (Lowers, Maher, Braun), two cluster fetches and three opinion reads, all of United States v. Braun (7th Cir.). Retrieved document dates: 2025-10-02 (the Braun docket), 2026-01-14 (the Wisconsin Supreme Court decision below, surfaced by an opinion search for "Gasper Snapchat 'private search'"), and 2026-08-20 (the Braun opinions). All precede the 2026-10-05 resolution and none concerns this petition's disposition; the one hit on the Gasper name is the decision under review, which the provisioned petition appendix already carried. No SCOTUS docket query for this petition, no web search, nothing under `data/qp-topics/`.

## Big case

My independent read is 0.45. The underlying question (whether an officer may open a hash-matched CyberTip file no human at the provider has viewed) is a genuine, respondent-conceded, six-circuit split governing a nationwide investigative pipeline, and a grant would have been a significant Fourth Amendment case. The vehicle was an interlocutory state criminal suppression ruling with a facial finality defect, one amicus, no CVSG, and a silent denial. Big issue, modest case. Disclosure: I printed the staged `prediction.json` files whole before writing, so the predictor's `big_case_score` was visible before I fixed my number; the read above is formed from the record.
