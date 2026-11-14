# Evaluation: gemini-baseline, Robinhood Markets, Inc. v. Sodha (No. 25-944), `evt-brief-sg-disposition`

**Outcome.** Cert stage. On November 13, 2026 the Court granted the petition "limited to the following question", which is the Solicitor General's reformulated Question 1 (Section 11(a) misleading-omissions liability on materiality "without an additional inquiry" into misleadingness). `outcome.json` records `actual_disposition: granted`, `actual_granted: 1`, route `plenary`.

**Scores.** Probability 0.78 against a grant: Brier 0.0484. `correct` = 1. The label `granted` matches the outcome's. The segment base rate, its basis and the skill score are the harness's to stamp; I wrote none of them. `vote_accuracy` is omitted (cert cell). No `semantic_grades` block (cert cell, no declared semantic set).

## Reasoning (`reasoning.md`): 0.80

The analysis is sound and reaches the right place for the right reason. It starts from the statpack's CVSG cut (about 35% grant family) and the `high` band, recognises that both pool over deny recommendations, and treats the SG's and SEC's recommendation to grant Question 1 as the decisive update. It reads the reformulation correctly as the answer to respondents' no-adversity objection, and its two discounts (the OT2024 securities DIGs in *Facebook* and *NVIDIA*, and the Item 303 theory surviving on remand) are real vehicle concerns drawn from the briefs.

What held it below the top:

- The 70%–85% grant rate after an SG grant recommendation is presented as "the historical grant rate" with no source. The committed pack has no recommendation-conditioned table, so this is background knowledge stated as a statistic.
- The band rates it lists include OT2025, the petition's own Term, alongside prior Terms. The pooled 35%–37% it uses is about right, so nothing turned on it.
- It says petitioners and the SG both show a conflict with the First, Third, Tenth and Eleventh Circuits. The SG brief finds the conflict with the Third, Tenth and Eleventh and says the First Circuit's approach also lacks the additional inquiry. That overstates the SG's position.
- 0.78 was the lowest of the three probabilities on an outcome that happened, though well within a reasonable range.

## Predicted reasoning: 0.90

Central claims, all borne out against the staged docket and outcome:

1. Grant limited to a reformulated Question 1. The order grants "limited to" one question.
2. The SG's wording is adopted and Question 2 is not taken. The granted question is the SG's text nearly verbatim.
3. Plenary review, no summary disposition. Route is `plenary`.
4. One or two further distributions. There were two (conferences of 11/6 and 11/13).
5. No separate writing on a grant order. None is noted.

The document was specific where it could have been wrong: a two-question grant, the petition's own wording of Question 1, or a denial were all open. I stopped short of 1.0 because following a clear SG recommendation is the modal call. The conditional merits outlook (vacate or reverse on *Omnicare*/*Macquarie*) is untested and earned neither credit nor penalty.

## Leakage

Forward cell, predicted October 26, resolved November 13. Every logged call is `unobserved`, so I graded the queries: prompt, schemas, docs, pipeline source, the statpack and this case's provisioned record. Nothing sought the disposition and nothing was read under `data/qp-topics/`. `not_applicable`.

## Big case: 0.60

A technical Section 11 question with real consequences for every registered offering and for IPO litigation; SEC and industry amici engaged. Low public salience.
