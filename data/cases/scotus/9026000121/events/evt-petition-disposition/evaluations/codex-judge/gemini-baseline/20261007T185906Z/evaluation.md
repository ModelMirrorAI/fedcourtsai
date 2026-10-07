# Evaluation: gemini-baseline

## Outcome and numerical scores

The event is cert-stage. The outcome records `denied` on October 5, 2026 and `actual_granted = 0`, consistent with the provisioned October 5 docket snapshot. The predicted denial earns **correct = 1**. P(any grant) = 0.001 gives Brier loss `(0.001 - 0)^2 = 0.000001`.

The prediction's own frozen context records Term 2026, `baseline`, and `sal-v4`; the evaluator's terminal context is not substituted. From the committed matching sal-v4 table, the bracketed reached rates for every displayed strictly-prior Term, OT2017–OT2025, pool to `637.385 / 12720 = 0.050108883647798745`, with basis **risk_set**. The numerator is the sum of published rounded percentages times weighted resolved denominators, so it is an approximate weighted numerator, not an integer grant count. The table shows 10 of 10 Terms; OT2026 is excluded and no rendered-window truncation applies. The baseline loss is approximately 0.002510900220428632 and skill is `0.9996017364641319`. This common evaluation baseline is available regardless of whether the candidate itself used it. These are committed-pack, denial-reweighted live/historical-slice estimates, not current remote-corpus measurements or proof of calibration.

## Reasoning quality: 0.50

The short rationale identifies relevant features: one distribution, response waiver, an individualized judicial-qualification dispute, a state statutory-fee issue, and no developed split. It treats denial as the likely selection outcome rather than claiming that the petitioner's underlying allegations are necessarily false. Those are useful grounds for a low grant probability.

The numerical justification is materially thinner than the confident 0.1% suggests. The rationale says a corpus query confirmed the baseline-petition grant rate, but gives no rate, denominator, Term window, or salience version. The visible commands are an attempted `--era modern` query and a general `--limit 5` query, neither a band-conditioned rate calculation; no committed-statpack read is shown. Since their results are unobserved, I do not claim to know what those rows contained, but this record does not substantiate the assertion of baseline verification. The roughly fiftyfold reduction from the published reached-band prior is not explained quantitatively.

The analysis also largely stops at the questions presented. It does not examine the disputed start date of the judge's employment, distinguish the constitutional threshold from state eligibility rules in any depth, or work through the state high court's procedural disposition. These are omissions in analytical support, not a penalty for brevity itself. The favorable realized Brier score does not establish that the probability was well founded. The score assesses only `reasoning.md`; neither the forecast prose nor auxiliary claim probabilities are graded here.

## Leakage and scope

The log marks forward, and the prediction predates the October 5 resolution by a day. All 25 logged calls have `result_capture = unobserved`; capture coverage 0.0 is a telemetry limitation, not a defect and not proof that the queries returned nothing. I assess the visible query targets and prose: provisioned files and general corpus context, no visible search for this petition's disposition, and a rationale describing unresolved proceedings. This supports influence `not_applicable` and no suspected leakage, with no outcome-revealing retrieval shown. Unseen result bodies were not audited, and absent disclosure alone is not the basis for this assessment.

No vote accuracy or semantic block is appropriate on this cert event. Claim scoring and provenance stamps are left to the harness. The optional independent stakes score is omitted after exposure to the candidate's stakes discussion.
