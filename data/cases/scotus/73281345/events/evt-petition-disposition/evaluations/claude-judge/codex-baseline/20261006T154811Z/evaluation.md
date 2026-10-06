# Evaluation — codex-baseline

**Cell.** Cert stage (`event.yaml` stage `cert`, moment `distribution`), Holly Ann Elkins v. United States, No. 25-1061, Term 2025. Outcome: petition **denied** on 2026-10-05 after two distributions, no CVSG, no noted dissent (`outcome.json`: `actual_disposition` `denied`, `actual_granted` 0). The candidate's prediction ran forward on the 2026-09-17 snapshot.

## Scores

| Field | Value | How |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` `denied` == `actual_disposition` `denied` |
| `brier_score` | 0.0049 | (0.07 − 0)² |
| `segment_base_rate` | 0.1722 | elevated band, bracketed `reached` figure, pooled resolved-weighted over Terms 2017–2024 |
| `base_rate_basis` | `risk_set` | frozen `context.band` `elevated` with `context.salience_version` `sal-v4`; the statpack table heading names `sal-v4` |
| `brier_skill_score` | 0.835 | 1 − 0.0049 / (0.1722 − 0)² |
| `reasoning_quality` | 0.85 | see below |

**Base rate detail.** The prediction's frozen context carries both a band (`elevated`) and a salience version (`sal-v4`), and the committed `metrics/statpack.md` "Segment base rate by salience band (sal-v4)" table matches that version, so the risk-set basis applies. The table renders all 10 Terms the pack holds (2017–2026); the Terms strictly before 2025 are 2017–2024, eight rows. Pooling the bracketed `reached` elevated figures by their `n` (from `statpack.json`'s `prefix_est_grant_rate` × `prefix_weighted_resolved`): 484 / 2810 = 0.17224. The shipped in-code lookback is 10 Terms, which would reach back to 2015, but the pack holds nothing before 2017, so the pack-bounded window and the rendered window coincide and no divergence needs flagging. Vote fields are omitted: a cert cell's votes are never scored.

## What the prediction got right and wrong

The candidate called the denial at 7%, well below the 17% risk-set anchor it correctly identified, and the petition was denied without a relist or a writing. Its subsidiary forecasts (no further distribution as the modal path, no CVSG with the United States already respondent, no separate writing) all matched. The forecast document and the claims block are not scored here; they are read only for context.

## Reasoning quality (0.85)

Strengths that drove the number:

- **Correct anchor and correct reading of it.** It took the frozen band rather than re-deriving one, pooled the bracketed reached figure over the strictly-prior Terms with explicit arithmetic (484 / 2810), and said plainly that the terminal relist and CVSG cuts were context rather than substitutes.
- **Primary-source check of the asserted split.** It pulled the Tenth Circuit's *Chavarria* opinion through CourtListener and confirmed from the text that the holding is confined to motor vehicles and expressly allows per se instrumentalities. That is the single most important fact in the brief in opposition, and the candidate verified it rather than taking the government's word.
- **Vehicle defect read correctly and attributed correctly.** It identified the alternative jurisdictional hooks (internet, email, GPS) as the government's representations rather than its own findings, and noted the petition's anticipatory answer, which is a fair account of what the record actually shows.
- **Procedural signal discounted for the right reason.** It recognized that the second distribution followed a call for response rather than a conference, so the raw count of two overstates how much the Court had looked at the petition.
- **Honest limits.** It said the reply brief was on the docket but not provisioned and that the number was judgmental rather than fitted.

What held it short of higher:

- The upward considerations are listed but not weighed against the strongest comparables in the record: the brief in opposition cites recent denials in *Smith* and *Stackhouse* on the same telephone question, and the candidate did not use them.
- The relist probability (22%) sits a little high for a petition whose only redistribution was briefing-driven, and the reasoning for it is thin relative to the rest of the document.
- The big-case rationale leans on the breadth of a hypothetical ruling more than on the realistic chance of one, but that is a stakes read and not a scoring issue.

## Leakage

`mode` `forward`; `retrieved_outcome_material` `false`; `influenced_prediction` `not_applicable`; `leakage_suspected` `false`. The prediction was created 2026-09-17 and the event resolved 2026-10-05, so the case was genuinely open. The log's 30 calls are prompt, schema, snapshot and provisioned-document reads, statpack reads, two unobserved web calls whose queries name only the 2025 Tenth Circuit *Chavarria* opinion, and three captured CourtListener calls on that same opinion. No `retrieved_doc_date` on or after resolution, no query for this petition's disposition, no read under `data/qp-topics/`. The reasoning states the snapshot carried no disposition and that nothing about the outcome was retrieved. No sign of a decided case provisioned forward.

## Big case

My own read is 0.3: a genuine Commerce Clause question with doctrinal reach across facility-of-interstate-commerce statutes, but a one-decision, non-telephone conflict, alternative jurisdictional hooks on the record, a private criminal petitioner, and a denial without any noted writing. Public stakes are low. The staged `prediction.json` carries the predictor's `big_case_score`, so that number was visible when I read the file; my read above rests on the substance of the record and the outcome, not on it.

## Semantic grades

None. This is a cert cell; no semantic set is declared and no opinion slot is staged.
