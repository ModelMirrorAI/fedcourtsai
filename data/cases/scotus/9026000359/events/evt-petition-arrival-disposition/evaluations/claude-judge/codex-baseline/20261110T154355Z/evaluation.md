# Evaluation — codex-baseline, evt-petition-arrival-disposition (scotus/9026000359, No. 26-359)

**Stage:** cert (arrival moment, forward). **Outcome:** denied 2026-11-09 after a single distribution (respondent waived 2026-10-09; distributed 2026-10-14 for the 11/6/2026 conference); no CVSG, no noted writing.

## Scores
- `predicted_disposition` denied vs. actual denied → **correct = 1**.
- P(grant) 0.012 vs. actual_granted 0 → **Brier = 0.000144**.
- Segment base rate, skill, and basis are the harness's; refer to the stamped segment base rate. No votes scored (cert stage).

## Reasoning quality — 0.85
Sound, well-documented analysis. It anchors on the pooled prior-Term `baseline` reached rate from the statpack under the matching salience version, then moves down for clearly stated reasons. It reads the five QPs correctly as error-correction framing with no clean split, and works through each theory (entitlement/delay, substantive due process, takings, Monell/retaliation) with page cites. It notes the internal tension in the petition's Agins discussion, and correctly uses Pembaur to show that the retaliation theory asks for an extension of municipal liability. It is honest about its limits (no opinion below, no BIO) and its retrieval. Small deductions: it carries an unnecessarily precise anchor figure, and it misses some vehicle and advocacy signals that were in the record (likely waiver by a municipal respondent, the §1257(a) jurisdictional miscitation, a unanimous panel below).

## Predicted reasoning — 0.8
Central claims: denial; one distribution followed by denial without a relist; disposition in Nov–Dec 2026; no CVSG; no separate writing. All held. The document was specific about path and timing, but it predicted the distribution would follow the Oct 16 response deadline. It did not foresee the waiver, which moved the distribution earlier. That is a secondary miss, and the November disposition still landed. The conditional question-selection and route content is untested.

## Leakage
Forward; created 2026-09-27, before resolution. Retrieval was the provisioned inputs, the statpack, generic Rule 10 web requests, and a CourtListener lookup of Pembaur (1986). Nothing about this petition's disposition. `influenced_prediction = not_applicable`, `leakage_suspected = false`.
