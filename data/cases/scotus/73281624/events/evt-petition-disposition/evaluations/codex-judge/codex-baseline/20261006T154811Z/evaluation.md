# Evaluation: codex-baseline

## Outcome and quantitative score

This cert-stage petition was denied on October 5, 2026, with actual_granted = 0. codex-baseline's September 17 prediction names denied and assigns P(any grant) = 0.08. Correctness is 1; Brier loss is (0.08 - 0)^2 = 0.0064. The order supplies the disposition, not the Court's reasoning or a ruling on the antitrust questions.

The frozen prediction context supplies elevated, sal-v4, and Term 2025. That version matches the committed statpack. The operative risk_set baseline is the resolved-weighted mean of the bracketed reached rates over all rendered Terms strictly before 2025: 2024 (17.9%, n=336), 2023 (17.5%, n=354), 2022 (19.0%, n=300), 2021 (20.5%, n=342), 2020 (16.1%, n=397), 2019 (13.8%, n=334), 2018 (15.9%, n=347), and 2017 (17.5%, n=400). The result is 484.386 / 2810 = 0.172379359430605. These are rounded published rates, not exact grant counts. The candidate reports an exact-count baseline from its prediction-time pack; that claim is not used to substitute for the evaluator's supplied table.

The table displays 10 of 10 Terms. Terms 2025 and 2026 are excluded, with no version mismatch or omitted rendered window. Skill is 1 - 0.0064 / 0.172379359430605^2 = 0.7846179784195887. This is a single-event comparison to a denial-reweighted paid-segment baseline, not an assertion of population-level skill. No live corpus query or freshness claim is made.

## Reasoning quality: 0.92

The rationale carefully separates reasons to grant from reasons to deny. It recognizes the potential significance of municipal commercial participation and the response request, while explaining why statutory specificity, the absence of a demonstrated appellate conflict, and presentation problems make this petition a less attractive vehicle. Its distinction between authorization to displace competition and the identity of the exclusive provider engages the actual dispute rather than merely labeling beach rentals unimportant.

The treatment of evidence is particularly strong. The opinion appendix supports the account of Western Star and the abandonment of non-antitrust claims; the opposition's heightened-rigor preservation assertion is expressly identified as a party's objection, not a newly adjudicated fact. The analysis does not equate a damages limitation with the absence of all useful relief. It also distinguishes response-driven redistribution from sustained conference interest and avoids treating unconditional circuit, terminal relist, or CVSG cuts as independent likelihood adjustments. These are sound analytical choices regardless of the realized denial.

Residual uncertainty remains substantial: the shift from approximately 17% to 8% is a judgmental adjustment without a validated conditional model, and the analysis cannot establish the response-requesting Justice's rationale or fully test preservation from the supplied filings alone. The candidate appropriately discloses those limits. The high quality score reflects the reasoning's specificity and evidentiary discipline, not superior realized Brier loss or an inference that the Court adopted its analysis.

Only reasoning.md is graded. The forecast document and structured mechanical claims remain outside reasoning_quality; the harness owns mechanical claim scoring. Cert votes and semantic grades are not scored. No big-case assessment is supplied.

## Leakage assessment

The harness records forward mode, 31 calls, and 30 captured results (coverage 0.967741935483871). The sole unobserved call is a web open of the exact petition PDF whose path identifies the March 23, 2026 filing. Its query is directed at pre-decision material, not an outcome search. The candidate says no usable content returned; because that response is unobserved, this is a disclosure rather than independently captured evidence of an empty result.

The other queries concern provisioned documents, the statpack, output helpers, and 2013 precedent. The collapsed tool class other is not evidence of suspicious activity. Nothing in the visible queries or reasoning shows the October 5 denial already known; the September 28 conference remains prospective. Retrieved_outcome_material is false, influenced_prediction is not_applicable, and leakage_suspected is false. This finding relies on the forward chronology and the actual query targets, not on missing response dates or the absence of unstaged predictor flags. The evaluator's October 5 docket is not treated as the candidate's original snapshot.
