# Evaluation: gemini-baseline

## Outcome and numerical scores

The supplied cert outcome is `denied` on October 5, 2026, with `actual_granted = 0`. The label prediction is correct (`correct = 1`). P(any grant) = 0.17 yields Brier loss `(0.17 - 0)^2 = 0.0289`.

The frozen prediction context supplies Term 2025, `elevated`, and `sal-v4`, matching the committed statpack table. The bracketed reached rates and weighted denominators for 2017–2024 are 17.5%/400, 15.9%/347, 13.8%/334, 16.1%/397, 20.5%/342, 19.0%/300, 17.5%/354, and 17.9%/336. Pooling gives 484.386/2,810 = 0.17237935943060498 on the `risk_set` basis. The noninteger numerator reflects the rounded percentages published in Markdown. Skill is `1 - 0.0289 / baseline^2 = 0.02741555880095481`: slightly better than that baseline on this denial, not evidence of general forecasting superiority.

The caption renders all 10 of 10 Terms in the pack, and all eight strictly prior rows enter this calculation. There is no rendered-window truncation or salience-version mismatch. I use committed-pack estimates only and make no claim about current remote-corpus freshness.

## Reasoning quality: 0.50

The rationale correctly selects a strictly prior, reached-band anchor and recognizes that a fact-bound vehicle can make an alleged procedural split less attractive. It forecasts denial without treating the favorable label as certainty and notes that the band already incorporates some trajectory information.

However, it calls the split clear on the strength of the petition's question framing, without confronting the opposition's distinctions or the lower court's alternative assessment of the videos. It repeats the officers' disputed version of the encounter without adequately distinguishing allegations from established facts. The suggestion that immunity could overdetermine the result is not developed into a concrete procedural or alternative-ground analysis. Most importantly, it describes a current relist as evidence of the Court considering the split, although the recorded sequence includes a response request before the first scheduled conference and a subsequent redistribution. Two distribution entries do not establish the deliberative history asserted in the rationale. The amendment and alternative video analysis, both reflected in the supplied opposition, provide more specific vehicle concerns than the general statement offered here.

The tiny adjustment from roughly 17.2% to 17% is asserted rather than explained. This is a plausible baseline-led forecast with material analytical gaps, not a demonstrated case-specific probability model. These limitations concern the content of `reasoning.md`, not brevity, missing telemetry, tool choice, or the unscored forecast document. The eventual denial does not supply a judicial explanation that repairs them.

## Leakage and scope

The harness marks a September 17 forward run, before the October 5 resolution. The query transcript shows local reads of instructions, context, questions presented, and the committed statpack, alongside directory listings, writes, and validation. It does not show a search for this petition's subsequent disposition or a read of forbidden labeling material. The prose is prospective.

All results are unobserved, so capture coverage is 0.0; this is not a defect and does not establish that any call returned nothing. The assessment rests on query targets, timing, and the rationale, not null result dates. No affirmative evidence shows outcome retrieval or an already-decided case provisioned forward. Outcome material is therefore assessed as not shown retrieved, influence `not_applicable`, and leakage not suspected, subject to that telemetry limitation.

Cert votes and semantic grades are omitted. The forecast prose is contextual only, mechanical claim scoring remains for the harness, and no provenance stamps or independent big-case grade are supplied.
