# Evaluation: codex-baseline

## Outcome and arithmetic

This is an interim, response-filed application-disposition event. The supplied outcome records `granted`, `actual_granted: 1`, resolved September 30, 2026. codex-baseline predicted `granted` at 0.78, so exact-label correctness is **1** and Brier loss is **(0.78 - 1)^2 = 0.0484**. Grant means granting the Warden's application to vacate the lower-court execution stay, not granting the prisoner's request for protection.

## Reasoning quality: 0.91

The rationale distinguishes the relevant interim axis from certiorari, uses a strictly prior-Term anchor, and explicitly labels its large upward adjustment as judgment rather than an estimated subgroup success rate. It connects the adjustment to a concrete alternative-prejudice argument and the distinction between reopening a merits determination and challenging the integrity of federal habeas proceedings. The provisioned application, printed pages 3–4 and 8–10, supports the attribution of those arguments to the State; it does not independently establish that the State is correct.

The analysis is notably balanced: it describes the competing integrity theory, the irreversibility of execution, and possible lower-court action, while distinguishing advocacy from established record facts. Its retrieval note and logged queries support its account of seeking the opposition, reply, and historical precedent. Its reported correction of a quotation in the reply is a useful source-critical explanation, but the reply and precedent result bodies are not staged here, so I do not independently certify that correction. Limitations include the unreviewed underlying motion and full habeas record, and the absence of empirical calibration for the particular 78% adjustment. The realized grant establishes the outcome match, not the truth of the proposed rationale.

This score assesses `reasoning.md` alone. The court-reasoning forecast and quantitative claims were read for context but not graded into this score.

## Baseline and scoring boundaries

The baseline and skill are harness-owned on this interim stage, so neither field is written. The committed interim table supports a prior-Term pool for the prediction's application Term 2026: 14 + 17 grants over 70 + 226 resolved substantive applications in 2024–2025, clearing the 50-resolved floor. Earlier displayed prior Terms contribute no resolved substantive cases. This is committed-pack context, not a fresh corpus claim; no corpus-wide or per-case pull vintage was established. The pool is selected for machine-matchable resolutions, counts withdrawn/dismissed cases as ungranted and mixed dispositions denial-first, has uneven parsing coverage, and is broader than the escalation-selected predicted population. Its skill comparison alone is not evidence of forecast skill. No baseline has yet been stamped in this evaluation.

`base_rate_basis` remains null. Votes are never scored on interim events. Judgment accuracy, semantic grades, and mechanical claim scores are not supplied; the latter belong to the harness.

## Leakage assessment

The captured log labels this prediction forward. It has 28 captured calls out of 30 marker-bearing calls. The two unobserved web calls cannot be credited as failed or empty merely because the candidate says they yielded no usable content. Their visible targets, however, are a linked opposition filing and historical precedent, not this application's disposition. The explicit exclusion of the forbidden labeling path in a directory search is not evidence of reading those artifacts. No visible query or reasoning passage shows knowledge of the target outcome; prior denials in separate Pike proceedings are not this event's resolution.

The prediction timestamp and date-only resolution both fall on September 30. This does not establish whether the Court acted before or after the forecast; the evaluator's decided record cannot reconstruct the prediction's baseline. There is no concrete evidence warranting a mis-provisioned-forward finding. I retain `not_applicable`, with `leakage_suspected: false`, subject to those audit limits.
