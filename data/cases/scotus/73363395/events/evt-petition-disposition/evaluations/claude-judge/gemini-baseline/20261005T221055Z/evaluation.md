# Evaluation — gemini-baseline

**Cell.** Cert-stage, forward-mode petition cell for Campo v. Uber Technologies, No. 25-1292 (Florida Third DCA). The outcome is a denial on the October 5, 2026 order list after the September 28 long conference, with one distribution, no CVSG and no noted dissent (`outcome.json`: `actual_disposition: denied`, `actual_granted: 0`, `distribution_count: 1`).

## Quantitative

- `correct = 1`: predicted `denied`, actual `denied`.
- `brier_score = 0.000025`: probability 0.005 against 0.
- `segment_base_rate = 0.051209`, `base_rate_basis = risk_set`. The prediction's frozen context carries `band: baseline` and `salience_version: sal-v4`, matching the statpack table heading, so the risk-set basis applies. Pooled bracketed `reached` figure for `baseline`, resolved-weighted, over the rendered Terms strictly before Term 2025 (2017–2024): 593 / 11,580. The caption renders 10 of 10 Terms, so the rendered window matches the in-code lookback. No divergence to flag.
- `brier_skill_score = 0.990467`: 1 − 0.000025 / (0.051209 − 0)².
- No `vote_accuracy` (cert stage). No `judgment_correct`.

## Reasoning quality: 0.50

The number landed in the right place and the rationale is not wrong, but it is a single short paragraph that asserts its conclusions rather than showing them.

What is sound:

- The anchor is the right table (`~5%` for a baseline private petition over prior Terms), and the direction and rough size of the adjustment are defensible.
- The respondent's waiver is correctly read as a weak-petition signal, and the characterization of the case as a routine state-court civil dispute with no split is accurate.
- The forecast of a denial at the first conference with no further relist was exactly what happened.

What held the score down:

- **The legal analysis is absent.** It says there is "no substantial federal question" but never says why. The decisive point in this petition, that the Seventh Amendment does not bind the States and the petition's own Florida authority concedes it, is not mentioned. Both other candidates found it, one by retrieving Walker v. Sauvinet and one by reading the petition's quoted authority. A reader of this rationale cannot tell whether the candidate knew the questions were foreclosed or simply pattern-matched on "Uber, state court, waiver."
- **A terminal cut is read as a forward anchor.** "The base rate for 0 relists is 1.2%" is the `granted` share of the terminal zero-relist bucket in the paid scored segment (the same bucket also carries `gvr 0.5%`, so even as a terminal figure the any-grant rate is 1.7%). A petition that is pending at its first conference has not ended in that bucket; the number describes petitions that were never relisted, which is only known afterward. The candidate then stacks this second anchor beside the 5% band rate without reconciling the two or saying which the 0.005 descends from.
- **Imprecise pooling.** The 5% figure is given as "~5%" with no statement of which Terms were pooled or whether the case's own Term was excluded. It happens to be close to the correct 5.12%.
- **Retrieval did not inform the number.** The one corpus query (2020s denied dispositions, first ten rows) is unrelated to this petition and the rationale makes no use of it.

The prediction is correct and well calibrated; the rationale is thin.

## Leakage

Mode `forward` per the staged log. The cell ran on September 16, 2026, nineteen days before the denial. The log's `result_capture_coverage` is 0.0 (every marker-carrying call `unobserved`), which is this engine's standing telemetry shape, not a defect, so each call is graded on its query. The 23 calls are reads of the prompt, contract, schema, snapshot, context, documents and statpack; one shell corpus query for 2020s denied dispositions generally (not this case); and the output writes and validate. No web search, no CourtListener call, no query for this docket or caption, no `retrieved_doc_date` at all. The reasoning forecasts the denial. `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, `leakage_suspected = false`.

## Big case (my independent read): 0.06

A single wrongful-death vicarious-liability suit that lost on summary judgment in Florida, brought on a Seventh Amendment theory that does not apply to state courts, denied at the first conference without a response or any writing. No reach beyond these parties. Disclosure: the candidate's `big_case_score` (null here) is a field of the staged `prediction.json`, which I had read for the probability before forming this read.
