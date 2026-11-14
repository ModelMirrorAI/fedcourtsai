# Evaluation: codex-baseline, Robinhood Markets, Inc. v. Sodha (No. 25-944), `evt-brief-sg-disposition`

**Outcome.** Cert stage. On November 13, 2026 the Court granted the petition "limited to the following question", which is the Solicitor General's reformulated Question 1 (Section 11(a) misleading-omissions liability on materiality "without an additional inquiry" into misleadingness). `outcome.json` records `actual_disposition: granted`, `actual_granted: 1`, route `plenary`.

**Scores.** Probability 0.84 against a grant: Brier 0.0256. `correct` = 0. The prediction's label is `granted-in-part` and the outcome's is `granted`, so the exact-label rule gives 0. The candidate chose that label because it expected the grant to be limited to Question 1, which is what the order did; the miss is on label convention, not on the forecast, and I flagged it in `flags.json` as a warning. The segment base rate, its basis and the skill score are the harness's to stamp; I wrote none of them. `vote_accuracy` is omitted (cert cell). No `semantic_grades` block (cert cell, no declared semantic set).

## Reasoning (`reasoning.md`): 0.90

The strongest rationale of the three. It anchors on the CVSG cut and on the `high` band pooled over Terms strictly before the case's own, and it says plainly that the move from about 35% to 0.84 is judgment about this filing, not a fitted statistic, because the pack has no recommendation-conditioned table. It also notes that the Court's invitation and the SG's recommendation are not independent signals.

Its account of the SG brief is accurate where the others slip: conflict with the Third, Tenth and Eleventh Circuits, the Second Circuit treated more cautiously, the First Circuit's approach not resolving the distinction. I checked that against the staged brief. The vehicle discussion is balanced (BIO's half-truth and interlocutory arguments, the reply, the SG's reformulation as "a plausible cure, not proof"), and the surviving Item 303 theory is handled as an incomplete-relief concern the SG had answered. The *Macquarie* analogy is used with appropriate limits. It also caught and worked around a mis-extracted questions file.

It put most of the remaining mass on denial and said so. 0.84 was the best-calibrated number here. The prose is heavy with caveats that do no forecasting work, which is the only reason this is not higher.

## Predicted reasoning: 0.90

Central claims, all borne out:

1. Grant limited to Question 1 as the SG reformulated it, Item 303 question not taken. The order grants "limited to" that question.
2. The question will carry the "additional inquiry" concept. It does, in those words.
3. Plenary review. Route is `plenary`.
4. One further distribution, then zero or one true relist; no new CVSG. Distributed for 11/6, relisted once to 11/13, granted.
5. No separate writing expected. None noted.

Specific and correct on scope, wording, route and path. Short of 1.0 for the same reason as the others: the document followed the SG's recommendation, the expected call. The conditional merits ground is untested and earned nothing either way.

## Leakage

Forward cell, predicted October 26, resolved November 13. The staged log holds eight captured shell reads of the provisioned BIO and reply. The candidate's `retrieval.md` discloses more than that log shows: a statpack read, a failed web search and fetch for the 2024 *Macquarie* opinion, and two CourtListener calls on it. I flagged the partial log (`info`). None of the disclosed calls concerns this petition's outcome, and *Macquarie* predates everything here. `not_applicable`.

## Big case: 0.60

A technical Section 11 question with real consequences for every registered offering and for IPO litigation; SEC and industry amici engaged. Low public salience.
