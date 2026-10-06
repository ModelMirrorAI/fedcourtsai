# Evaluation: codex-baseline

## Outcome and scores

The event is cert-stage. The supplied outcome records denied, actual_granted = 0, resolved October 5, 2026; the provisioned October 5 snapshot also records "Petition DENIED." codex-baseline's denied label matches exactly, giving correct = 1. Its P(any grant) = 0.006 yields Brier = (0.006 - 0)^2 = 0.000036. This establishes a correct forecast of disposition, not judicial endorsement of the predictor's account of why review was unlikely.

## Matched baseline

I take baseline, sal-v4 and Term 2025 from this prediction's frozen context. The committed statpack uses the matching sal-v4 heading, so the basis is risk_set and the bracketed reached rates apply. The table renders 10 of 10 Terms; its eight rows strictly before 2025 comprise the full available prior-Term window. Baseline reached percentages and weighted resolved denominators are 2024: 5.7%, 1271; 2023: 5.9%, 1312; 2022: 5.8%, 1192; 2021: 5.6%, 1500; 2020: 4.5%, 1739; 2019: 4.6%, 1399; 2018: 4.6%, 1524; 2017: 4.7%, 1643.

Their resolved-weighted pool is 592.925 / 11580 = 0.05120250431778929. The numerator is an approximation from published rounded percentages, not an integer grant count. Skill is 1 - 0.000036 / 0.05120250431778929^2 = 0.9862684331659415. The candidate reports a slightly different 593 / 11580 from exact JSON counts; this evaluation follows the rendered Markdown table and does not claim that tiny rounding difference is an analytical defect. The table covers all pack Terms, so no window-divergence flag is necessary. These are committed denial-reweighted live/historical-slice estimates, not a live corpus refresh; I assert no current corpus vintage.

## Reasoning quality: 0.92

The rationale carefully separates record facts, advocacy, and uncertainty. It distinguishes a future first conference from a relist, preserves filing and docketing dates without inferring a defect, and anchors on the matched reached population rather than a terminal no-relist population. Its strongest evidence is the opposition's hearing appendix: the judge considered the challenged conduct and accepted the corrected damages ratio. The provisioned transcript at A-14 supports that account. The rationale also recognizes the hearing's jury-deferential remarks rather than portraying it as a complete written constitutional analysis.

The treatment of competing damages denominators and the erroneous 7.8:1 hearing argument is concrete and appropriately cautious. The candidate distinguishes the quoted TXO trial-hearing proposition from the broader appellate written-opinion issue, and acknowledges that a silent appellate disposition does not reveal how that court conducted its review. Those distinctions prevent a low grant probability from turning into an unwarranted conclusion that every underlying due-process question is settled. It identifies remaining uncertainty rather than merely retelling a favorable outcome.

The grade falls short of the maximum because the reduction from approximately 5.12% to 0.6% is still a discretionary judgment without a matched empirical vehicle estimate. The provided hearing and brief strongly motivate the direction, not that precise magnitude, and the rationale does not establish an exhaustive survey of possible conflicts. The candidate discloses these limits. The 0.92 assesses only reasoning.md's analysis; forecast prose, auxiliary claim probabilities and stakes estimates are not folded into it.

## Leakage and scope

The log says forward. All 30 calls occurred September 17, before the October 5 disposition. Its capture coverage is 28/30; the two unobserved web rows seek the historical TXO opinion and its PDF. Unobserved means the results were not captured, not that no material returned, so the candidate's report of empty web content is not treated as independently verified. Those queries nonetheless target another case's historical precedent, not this petition's outcome. Captured citation/passage lookups and local pleading reads are consistent with the rationale. The retrieval note additionally reports a general Rule 10 query; even on that self-reported account, it is not a search for this case's result. No available query or reasoning shows the denial. Accordingly, retrieved_outcome_material = false, influenced_prediction = not_applicable, and leakage_suspected = false.

Cert vote accuracy and semantic grades are omitted. Mechanical claim scores and provenance/context stamps are reserved to the harness. No independent big-case score is supplied. The ordinary capture limitation does not warrant a data-quality flag.
