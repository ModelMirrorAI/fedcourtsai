# Evaluation: codex-baseline

## Outcome and numerical scores

This is a cert-stage disposition. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`. The predicted label is `denied`, so `correct = 1`; at P(any grant) = 0.12, Brier loss is `(0.12 - 0)^2 = 0.0144`. A correct denial forecast does not establish why the Court denied review.

The prediction froze Term 2025, band `elevated`, and version `sal-v4`. The committed `metrics/statpack.md` heading matches that version. I use its bracketed reached rates, not terminal rates or the evaluator's decided-docket context. The strictly prior rendered rows are 2017–2024: 17.5%/400, 15.9%/347, 13.8%/334, 16.1%/397, 20.5%/342, 19.0%/300, 17.5%/354, and 17.9%/336 (rate/weighted resolved n). Their resolved-weighted sum is 484.386 over 2,810, giving `segment_base_rate = 0.17237935943060498`, on the `risk_set` basis. The numerator reflects rounded published percentages, not an integer grant count. Skill is `1 - 0.0144 / baseline^2 = 0.5153904514440745`.

The caption renders all 10 of 10 pack Terms; excluding 2025 and 2026 leaves eight prior rows, with no rendered-window truncation to flag. The candidate's 484/2,810 anchor used unrounded companion-artifact data according to its rationale; the small difference from this evaluation is publication rounding, not a different population. These are committed-pack estimates, not a claim about current remote-corpus freshness. No live corpus was queried.

## Reasoning quality: 0.91

The rationale separates a potentially consequential video-evidence disagreement from the case's suitability for resolving it. It identifies the alternative video analysis below, the respondent's reported amendment, and the dependence of the immunity question on contested facts. The provisioned opposition supports those vehicle concerns, including its account of the amended complaint and the alternative analysis. The candidate distinguishes a party's account from an independently established fact, and does not claim to have watched the video.

It also avoids equating two distributions with two substantive conference examinations: the May response request intervened before the scheduled conference. Retaining the frozen band while discounting that signal is more defensible than silently reclassifying the petition. Its treatment of the split is balanced, and it explains why the questions are not independent chances of review. The adjustment from approximately 17.2% to 12% remains subjective rather than empirically estimated; uncertainty about the video's content and the amendment's effect remains unresolved. Those limitations keep the analysis short of a near-certain assessment. The score grades this rationale, not the correct outcome alone.

## Leakage and scope

The captured log labels this a forward prediction made September 18, before the October 5 resolution. External queries target the petition's March appendix, the November 2025 lower-court decision, and an older precedent. No surfaced date, query, or rationale establishes access to this petition's eventual disposition. Coverage is 41/44 captured calls. The three unobserved web calls cannot be credited as failed or empty on the strength of null metadata; their targeted pre-decision queries nevertheless supply no affirmative evidence of outcome retrieval. The explicit exclusion of the labeling-artifact path in a directory search is not a read of its contents.

Accordingly, outcome material is not shown as retrieved, influence is `not_applicable`, and leakage is not suspected. The forecast document was read only for context. Cert votes and semantic claims are not scored; mechanical claim scores and provenance stamps remain for the harness. No independent big-case assessment is supplied.
