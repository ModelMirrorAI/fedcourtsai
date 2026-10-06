# Evaluation: codex-baseline

## Outcome and arithmetic

The event is cert-stage. The supplied outcome records denial on October 5, 2026, with actual_granted = 0. The prediction assigns 0.22 to a grant and names denied: correct = 1 and Brier = (0.22 - 0)^2 = 0.0484. The denial resolves the label but does not reveal the Court's reasons.

The frozen context supplies elevated, sal-v4, and Term 2025. The matching table in committed metrics/statpack.md shows all 10 of 10 Terms. I pool all displayed strictly prior rows, 2017–2024, using the bracketed reached rates and weighted resolved denominators: (0.179*336 + 0.175*354 + 0.190*300 + 0.205*342 + 0.161*397 + 0.138*334 + 0.159*347 + 0.175*400)/2810 = 0.17237935943060498. This is the risk_set basis and a denial-reweighted live/historical-slice estimate from the committed pack, not newly queried corpus state. The rounded-table numerator 484.386 is approximate, not an integer count. The candidate's stated 484/2810 comes from its reported unrounded JSON calculation; that tiny difference is not an analytical defect. This evaluation follows the rendered markdown surface. Skill is 1 - 0.0484/(0.17237935943060498)^2 = -0.6288265382018607. A correct label can still lose to a lower-probability baseline on this event; neither fact establishes aggregate calibration.

## Reasoning quality: 0.90

The analysis carefully separates a claimed conflict from a demonstrated conflict and distinguishes search identification from administrative-search reasonableness. It addresses the opposition, the reply's preservation answer, the conceded regulatory status of the fishery, and the limited inference warranted by the two distributions. The supplied opposition, printed pages 12–19, confirms that the concessions and distinctions among vessels, daycare homes, and municipal tire chalking are central contested issues. The candidate does not convert those adversarial submissions into certain findings.

It also reports targeted reading of the lower-court opinion and expressly marks inference and source limitations: the supplemental brief's description of Richards is not represented as an independently verified holding, and the reply reduces rather than conclusively eliminates preservation concerns. The rationale keeps terminal relist statistics separate from incremental probabilities and uses the relevant frozen-band anchor. This combination of counterargument, provenance, and uncertainty supports a strong quality score independent of the correct label.

The remaining weakness is quantitative judgment: the upward move from approximately 17.2% to 22% is plausible but not estimated from comparable cases, and attention signals may partly duplicate information already represented by the elevated band. Selected opinion passages rather than a full independent review also limit confidence. The outcome does not establish that the candidate's account of the legal obstacles explains the denial.

## Leakage and scoring boundaries

The harness records forward mode and 33 captured results out of 34 calls. All calls occur on September 17, before the supplied October 5 resolution. The sole unobserved call targets the July 20 reply; it is assessed by that query, not credited as a failed or empty result. Other case-specific fetches target the September 9 supplement and the November 18, 2025 First Circuit opinion. The candidate's reasoning contains no result disclosure or presupposition of a decided petition. There is no evidence of outcome retrieval or forward mis-provision: retrieved_outcome_material = false, influenced_prediction = not_applicable, and leakage_suspected = false. Null retrieved-document dates alone are not evidence of absence.

The named forecast was read for context, not graded. Quantitative claims are reserved for the harness and are excluded from reasoning_quality. Cert-stage vote accuracy is omitted. No semantic set is declared here, so no semantic_grades block is written. No independent big-case score is supplied.
