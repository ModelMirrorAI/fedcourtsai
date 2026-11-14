# Evaluation: claude-baseline, Robinhood Markets, Inc. v. Sodha (No. 25-944), `evt-brief-sg-disposition`

**Outcome.** Cert stage. On November 13, 2026 the Court granted the petition "limited to the following question", which is the Solicitor General's reformulated Question 1 (Section 11(a) misleading-omissions liability on materiality "without an additional inquiry" into misleadingness). `outcome.json` records `actual_disposition: granted`, `actual_granted: 1`, route `plenary`.

**Scores.** Probability 0.80 against a grant: Brier 0.04. `correct` = 0. The prediction's label is `granted-in-part` and the outcome's is `granted`, so the exact-label rule gives 0. The candidate chose that label because it expected the grant to be limited to Question 1, which is what the order did; the miss is on label convention, not on the forecast, and I flagged it in `flags.json` as a warning. The segment base rate, its basis and the skill score are the harness's to stamp; I wrote none of them. `vote_accuracy` is omitted (cert cell). No `semantic_grades` block (cert cell, no declared semantic set).

## Reasoning (`reasoning.md`): 0.82

Compact and sound. It uses the same two anchors (CVSG cut about 35%, `high` band about 35% over Terms strictly before 2025) and is candid that the 70–80% rate after an SG grant recommendation comes from background knowledge, not a committed table. The adjustments are the right ones: SEC on the brief, a pure question of law, cert-stage amici, the follow-on to *Macquarie*, against a partial recommendation, the adversity objection and the interlocutory posture. Its stated main risk (the Court doubting adversity on Question 1) was the right one to name.

What held it down:

- Its account of the split is loose. It says the SG found a conflict with the Second Circuit (*Stadnick*). The staged SG brief rests the conflict mainly on the Third, Tenth and Eleventh Circuits, says the Second Circuit "also appears to be in conflict" on the strength of *Time Warner* while its position is "less clear", and treats *Stadnick* as the case respondents cite and as ambiguous. The direction is right; the detail is not.
- The vehicle analysis is thinner than the other two; the BIO's arguments get one clause, and the surviving Item 303 theory is not weighed.

Its reading of why the SG would not take Question 2 (petitioners did not seek review of the separate materiality point, so the case is a poor vehicle for it) matches the brief.

## Predicted reasoning: 0.85

Central claims, all borne out:

1. Grant limited to Question 1, likely as the SG reformulated it. The order grants "limited to" that question.
2. SG wording most likely, Question 2 denied or not reached. The granted question is the SG's text.
3. Plenary review, no summary disposition. Route is `plenary`.
4. Redistribution for a November 2026 conference and a grant at the first or second post-CVSG conference. Granted at the second (11/13) after one relist, which the document called "plausible but not the main path".

Right on every central point and specific about timing. Slightly below the other two because the commitments are a little softer: "likely as reformulated", "denied or not reached", and a two-question grant named as the main alternative. The conditional merits ground and the spring 2027 argument timing are untested and earned nothing either way.

## Leakage

Forward cell, predicted October 26, resolved November 13. All eleven logged calls are captured reads of the prompt, the October 7 snapshot, the provisioned documents and the statpack. No web or MCP call, nothing under `data/qp-topics/`. `not_applicable`.

## Big case: 0.60

A technical Section 11 question with real consequences for every registered offering and for IPO litigation; SEC and industry amici engaged. Low public salience.
