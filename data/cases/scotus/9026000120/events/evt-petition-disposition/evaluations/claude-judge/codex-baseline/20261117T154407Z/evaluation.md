# Evaluation: codex-baseline

Cert-stage cell (`stage: cert`, moment `distribution`). Outcome: petition **denied** on 2026-11-16, no CVSG, two distributions in total, no noted dissent.

## Scores

- Predicted `denied` at P(grant) = 0.22. `correct` = 1; `brier_score` = (0.22 - 0)^2 = 0.0484.
- The segment base rate, its basis and the skill score are the harness's to stamp; I wrote none of them. `vote_accuracy` is omitted (cert cell). No `semantic_grades` (no semantic set on a cert cell).

## Reasoning (`reasoning_quality` 0.68)

The analysis is careful and honest about its limits. It read the decision below from the petition appendix instead of relying on the parties, noted that Judge Carson concurred in the judgment, weighed the opposition's account of the split without dismissing the acknowledged contrary language in *Minton*, and checked *Consumers Union* directly to see that it cuts both ways. Its key procedural observation is right: the second distribution followed a pre-conference reschedule, so the petition had never been conferenced and relisted, and the elevated band overstates the attention it had received.

What holds the grade down is that the conclusion does not follow that observation far enough. Having found that the main signal behind the elevated band was an administrative reschedule, that the split was contested, and that the panel was unanimous on the judgment, the document moved only from the stamped anchor of about 0.25 to 0.22. Its own cited cross-check (the one-relist bucket) pointed materially lower. The direction was right and the denial call was right, but the weight of its own evidence supported a larger discount, and that shows in the highest Brier of the three. It also did not pick up the district court's alternative mootness ground, a vehicle point visible in the opposition.

Base-rate figures were checked against the committed statpack. They differ from it by a few counts (for example resolved n in the relist and amicus tables), which is consistent with a refresh after the candidate ran; I did not rebuild the earlier pack and did not mark any figure wrong.

## Predicted reasoning (`predicted_reasoning_quality` 0.75)

Central claims, in the document's order of weight: denial without a separate writing; no further distribution on the modal path, with disposition in the order cycle after the November 13 conference; no CVSG. All three were borne out by the docket (denied November 16, no later distribution, no CVSG, no noted dissent). The conditional-on-grant content (plenary route, QP1 framing) is unresolved and earns neither credit nor penalty.

The document committed to a clear modal path and a timing, which is more than the bare outcome, so it sits above the generic middle. It does not reach the top because a quiet denial is the most common path for a petition in this posture, and the document's stated reasons for denial are general.

## Leakage

Forward cell, predicted 2026-11-09, a week before the denial. The log shows provisioned-record reads, the statpack, one corpus query returning unrelated granted cases, CourtListener lookups of the 1980 *Consumers Union* opinion, and two web-search rows whose results were not observed; graded on their queries, both targeted that precedent and *Minton*, not this petition. Nothing surfaced this case's disposition. `influenced_prediction` = `not_applicable`.

## Stakes

My own read is 0.4: real doctrinal questions on a salient speech subject with four advocacy-group amici, but confined to state legislative committee procedure, a unanimous judgment below, and a denial without any writing.
