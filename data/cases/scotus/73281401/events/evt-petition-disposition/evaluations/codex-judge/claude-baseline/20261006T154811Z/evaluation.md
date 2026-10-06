# Evaluation: claude-baseline

## Outcome and numerical scores

The cert outcome is denial on October 5, 2026, with `actual_granted = 0`. The predicted `denied` label matches exactly: `correct = 1`. At P(any grant) = 0.10, Brier loss is 0.01.

The prediction's frozen Term 2025, `elevated` band, and `sal-v4` version select the matching bracketed reached rates in committed `metrics/statpack.md`. In ascending Term order, the eligible 2017–2024 rows are 17.5%/400, 15.9%/347, 13.8%/334, 16.1%/397, 20.5%/342, 19.0%/300, 17.5%/354, and 17.9%/336 (rate/weighted resolved n). Pooling the published rounded rates gives 484.386/2,810 = 0.17237935943060498. This is a `risk_set` baseline, not a terminal-band rate; 484.386 is a weighted numerator from rounded percentages, not an observed grant count. Skill is `1 - 0.01 / baseline^2 = 0.6634655912806072`.

The table renders 10 of 10 pack Terms. All eight shown rows strictly before 2025 enter the calculation; 2025 and 2026 do not. There is no caption-indicated window truncation. These figures describe the committed pack, not a newly refreshed remote corpus; no corpus freshness claim is made.

## Reasoning quality: 0.85

The rationale identifies the two strongest record-based reasons to discount the reached-band anchor: the second distribution followed a pre-conference response request rather than an established substantive relist, and the lower court's alternative video analysis reduces the payoff from resolving the alleged methodological split. It connects Questions 2 and 3 to that factual and procedural difficulty instead of treating each question as an independent opportunity for review. Its account of the changed complaint is supported by the provisioned opposition. It acknowledges that its broad corpus queries yielded little usable information and did not move the number.

The analysis is less careful where it treats missing docket materials as proof of no amicus support, infers reduced cert prospects from counsel's identity, and characterizes the split's strength without independently inspecting the strongest contrary opinion. Those secondary adjustments are not quantified or well established by the staged evidence. Its confident assertion that the initial conference would not consider the petition is plausible from the response-request chronology but stronger than what the docket entries alone prove. The net adjustment to 10% is reasoned but remains judgmental, not a calibrated case-level model. The favorable Brier score does not independently validate those assumptions or identify the Court's reason for denial.

## Leakage and scope

The harness log identifies a September 17 forward run, before the October 5 denial; all 35 calls carry captured results. The November 2025 opinion below and the case's docket metadata were retrieved. The latter has a March 23, 2026 document date, and the candidate reports the docket still open with a July 29 modification date. A date extracted from docket metadata is not a complete chronology, but neither the log nor the rationale shows this petition's ultimate disposition. Other searches and corpus queries concern priors, not a later resolution of this case. The status-output exclusion involving labeling artifacts is not a read of their contents.

There is no affirmative evidence of outcome retrieval or mis-provisioning an already-decided case: `retrieved_outcome_material = false`, influence `not_applicable`, leakage not suspected. The forecast prose and mechanical claims are not included in the reasoning-quality grade. Cert votes and semantic grades are omitted; claim scoring and provenance stamps are left to the harness. No independent big-case assessment is supplied.
