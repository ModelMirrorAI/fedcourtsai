# Evaluation — claude-baseline — scotus/73392441 evt-petition-disposition

## Cell

Cert-stage petition event (`stage: cert`, `moment: distribution`), forward mode. Outcome: certiorari **denied** on 2026-10-05 after a single distribution (for the September 28, 2026 conference), no CVSG, no noted dissent. `actual_granted = 0`.

## Scores

| Field | Value | Basis |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition: denied` == `actual_disposition: denied` |
| `brier_score` | 0.000049 | (0.007 − 0)² |
| `segment_base_rate` | 0.051209 | baseline band, bracketed `reached` figure, pooled resolved-weighted over OT2017–OT2024 (593 / 11,580) |
| `base_rate_basis` | `risk_set` | prediction froze `band: baseline` with `salience_version: sal-v4`; the statpack table heading is sal-v4 |
| `brier_skill_score` | 0.981315 | 1 − 0.000049 / 0.051209² |
| `reasoning_quality` | 0.85 | see below |

Base-rate detail: the prediction's frozen context carries both `band` and `salience_version`, and the committed `metrics/statpack.md` *Segment base rate by salience band (sal-v4)* heading matches, so the `risk_set` basis applies. The table caption renders 10 of 10 Terms, so the rendered window is the whole pack; the Terms strictly before the case's Term 2025 are OT2017–OT2024. The pooled rate from the unrounded `statpack.json` prefix fields is 593 / 11,580 = 0.051209; pooling the rounded percentages shown in the markdown table gives 0.051203, an immaterial difference. No window divergence to flag.

`vote_accuracy` omitted (cert stage, never scored). `judgment_correct` null (no judgment on either side). No `semantic_grades` block: no semantic set is declared on a cert event and the prediction carries none.

## What the prediction got right

Everything on the disposition axis. The candidate called an outright denial on the first October order list with no further distribution, no CVSG, and no separate writing, which is exactly what happened.

## Reasoning quality — 0.85

Strengths, as a matter of the legal analysis in `reasoning.md` rather than of being right:

- **Anchor handled correctly.** It identified the sal-v4 table, pooled the bracketed `reached` baseline figure over the right eight Terms (≈5.1%), and distinguished that risk-set rate from the ≈1% terminal rate, explaining why the former is the yardstick. That is the pre-registered reading of the table.
- **The decisive legal points are sound.** The Seventh Amendment has never been incorporated against the states, which guts QP 2 on its face in a Washington state-court case. The remaining due-process theory is a fact-bound complaint about one trial-court remark. The petition cites Anderson and Tolan, authorities that already state the rule the petitioner says was broken, so the petition is error-correction without a split. The vehicle is a state-law equitable reformation claim decided in an unpublished intermediate opinion. Each of these is accurate and each independently pushes toward denial.
- **Docket-reading insight.** Noting that the petition was distributed with neither a BIO nor a waiver and that no response had been called for is a genuine signal about the Court's lack of interest, correctly weighted.
- **Honest about evidence quality.** The counsel-history point is explicitly labeled as training recollection that could not be verified through the corpus or CourtListener, and is weighted lightly. The missing appendix is acknowledged as a limit on reading the record.

Deductions:

- The counsel-profile adjustment, even lightly weighted, rests on unverified recollection and does not belong in a forecast's downward adjustments; the candidate's own hedge mitigates but does not remove it.
- The originating-court point cites the statpack's state-court cut loosely ("roughly zero to one percent"); the table shows exactly that for the state intermediate courts listed, so it is fair, but no specific row is named.
- The statement that long-conference petitions are "overwhelmingly denied on the first October order list" is true but is a restatement of the base rate rather than case-specific evidence.

The number 0.007 sits well below the pooled anchor and the analysis justifies the gap. A strong, well-sourced analysis with one soft spot.

## Leakage

`mode: forward`. `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`. Forward cell; prediction created 2026-09-17, petition denied 2026-10-05 off the September 28 long conference, so the case was genuinely open. Log fully captured (coverage 1.0): 27 calls, all local reads of the provisioned record, prompt, schemas and statpack, one corpus query (granted petitions, 2020s, shape check), and four CourtListener calls scoped to this docket's header and counsel name. The only retrieved_doc_date is 2026-05-26 (the docket filing date) and the docket read back date_terminated null. No data/qp-topics path touched. No outcome material in the log or the prose. The candidate's own `retrieval.md` matches the captured log. I checked the forward mis-provisioning case: the prediction predates the conference by eleven days and the denial by eighteen, so the case was open when predicted.

## Big-case read

My independent read, formed before reading the candidate's score: 0.05. Independent read formed before looking at the candidates' scores: a private deed-of-trust reformation dispute from an unpublished Washington Court of Appeals decision after discretionary state review was denied; the questions presented recast one summary judgment ruling as a Due Process and Seventh Amendment attack on summary judgment itself. No response was called for, one distribution, denied without noted dissent. Stakes for anyone beyond the parties are negligible. The candidate's 0.12 is in the same low region and its rationale correctly separates the sweeping framing of the question from the trivial concrete stakes.
