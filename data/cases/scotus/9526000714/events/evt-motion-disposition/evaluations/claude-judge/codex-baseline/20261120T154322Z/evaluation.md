# Evaluation: codex-baseline, scotus/9526000714, evt-motion-disposition

**Stage: interim** (a stay application). The outcome records the finer reading: `interim_reading: withdrawn`, `interim_granted: 0`. The cell is scored on that. The segment base rate and skill are the harness's to stamp and are left null here, as is `base_rate_basis`. No `vote_accuracy` and no semantic grades on this stage.

## Scores
- Predicted `granted` at 0.95. The application was withdrawn the day after filing, which sits on the ungranted side. `correct` = 0, `brier_score` = (0.95 - 0)^2 = 0.9025.

## Reasoning (`reasoning_quality` 0.30)
The merits analysis is competent. The base-rate figures match the committed pack, the two earlier stays are read from primary sources, and the document engages the respondents' side by retrieving the Alliance's supplemental brief on the extension-cancellation theory, which the other record material did not supply.

The failure is structural. The number is stated as conditional "on the application remaining live", but only moot dispositions leave the scored set; a withdrawal stays in and scores as ungranted. The document never considers withdrawal at all, and the 5% it leaves is allocated to denial or narrower relief. It also had the Ninth Circuit docket open (it read an entry there dated Nov. 10) and noted that the emergency rested on the administrative stay lapsing Nov. 20, yet did not ask what would happen to the application if the Ninth Circuit removed that deadline. Going from a 68% reference cell to 95% on merits strength alone, with no procedural-exit path priced, is overconfidence that the outcome exposed directly.

## Predicted reasoning (`predicted_reasoning_quality` 0.00)
The document is short and commits to a specific sequence: response call and referral, one or two amicus filings, an administrative stay by Nov. 20, then a full-Court stay within about two weeks, with Justice Jackson the likeliest separate writer. Every resolvable step failed: no response call, no referral, no amicus brief, no administrative stay, no order. The writer claim is unresolved because no order issued. The document names no alternative path. Specific central claims that failed is the 0.0 anchor.

## Leakage
Forward cell, graded `not_applicable`. Capture coverage is partial (0.42), so the unobserved calls are graded on their queries; none reaches past the event. The candidate's own retrieval note says the live docket showed no new entries when checked, and the reasoning treats the application as pending. The prediction predates the withdrawal on the same day.

## Big case (0.60)
High human stakes, but a settled legal question and an application withdrawn without any ruling.
