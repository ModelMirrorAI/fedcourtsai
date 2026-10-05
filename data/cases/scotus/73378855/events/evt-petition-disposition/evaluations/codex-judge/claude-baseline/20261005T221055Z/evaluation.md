# Evaluation: claude-baseline

## Outcome and scores

This is a cert-stage petition-disposition evaluation. The supplied outcome records denial on October 5, 2026, with actual_granted = 0; the October 5 snapshot independently contains the entry "Petition DENIED." claude-baseline predicted denied with P(any grant) = 0.01. The exact-label score is 1 and the Brier score is (0.01 - 0)^2 = 0.0001. A correct denial does not establish that the Court adopted the candidate's substantive analysis.

## Matched baseline

The prediction's own frozen context supplies baseline, sal-v4, and docket Term 2025. The committed statpack heading matches sal-v4. I use the bracketed reached population, not terminal-band rates or this evaluator's decided-docket context. The rendered table shows 10 of 10 Terms; all eight displayed Terms strictly before 2025 enter the pool, so there is no rendered-window truncation. In descending order, the baseline reached percentages and weighted resolved denominators are 2024: 5.7%, 1271; 2023: 5.9%, 1312; 2022: 5.8%, 1192; 2021: 5.6%, 1500; 2020: 4.5%, 1739; 2019: 4.6%, 1399; 2018: 4.6%, 1524; 2017: 4.7%, 1643.

Pooling these published rounded percentages gives 592.925 / 11580 = 0.05120250431778929, an approximate rate rather than an integer grant count. Thus base_rate_basis is risk_set and skill is 1 - 0.0001 / 0.05120250431778929^2 = 0.961856758794282. These are the committed table's denial-reweighted live/historical-slice estimates, not a fresh corpus query. No current corpus vintage is asserted. The candidate's rounded 5.1% anchor is consistent with this table.

## Reasoning quality: 0.78

The rationale is materially case-specific. It reads both sides, identifies the trial-hearing evidence undermining an assertion of no meaningful review, computes the approximately 2.2:1 damages ratio from the award figures, and recognizes that the single distribution is not a denial. The provisioned opposition's discussion at pages 2–3 and 6–7 and its hearing appendix support these central factual premises. Keeping a small nonzero grant probability and disclosing the lack of a search for a possible intervening decision are reasonable expressions of uncertainty.

Several steps are overstated or insufficiently supported. The opposition's quoted TXO passage concerns a trial judge after an adequate hearing; it does not by itself establish that the petition's distinct appellate-explanation question is wholly foreclosed. The rationale's "presumptively acceptable" description is stronger than the opposition's narrower statement that single-digit ratios are more likely to comport with due process. A filing-to-docketing interval alone does not substantiate the suggested defective submission. The small convenience sample of unrelated grants, including emergency applications, supplies no matched estimate. Finally, appealing to the terminal baseline range partly conditions on the future trajectory the forecast must predict; the case-specific weaknesses support a downward adjustment, but the exact 1% is judgmental, not estimated from those terminal rates. These limitations reduce the grade despite the correct headline result.

The grade concerns only the analytical rationale in reasoning.md. The forecast document was read for context, not scored, and quantitative claims were not graded.

## Leakage and scope

The harness log reports forward mode, 16 calls, and complete result-capture coverage. Calls ran September 17, before the recorded October 5 resolution. The only external corpus query sought other recent grants; its legible returned document date is September 10. Neither queries nor the rationale reveal this case's denial. The log's digests do not expose every result body, but the available evidence supports retrieved_outcome_material = false and the ordinary forward assessment not_applicable; leakage_suspected = false. The later evaluator snapshot was used only to confirm the outcome, not to reconstruct the predictor's input boundary.

Vote accuracy is omitted because cert votes are not scored. No semantic set is graded on this cert cell. Mechanical claim scores, process stamps and context stamps remain the harness's. No independent big-case assessment is supplied, and no durable data-quality flag is warranted.
