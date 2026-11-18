# Evaluation: gemini-baseline

**Outcome:** petition denied on 2026-11-16, after one distribution (Nov 13 conference), with no response called for, no CVSG and no noted dissent.

**Scores:** `correct` = 1 (predicted `denied`, actual `denied`). Brier = (0.008 - 0)^2 = 0.000064, the best of the three candidates. This is a cert-stage cell; the segment base rate, basis and skill are the harness's to stamp and are left null. No votes are scored on a cert cell, and no semantic set is declared.

## Reasoning (`reasoning_quality` 0.5)

The structure of the argument is the strongest of the three. It starts from the prior-Term `baseline` risk-set anchor and then conditions on the fact that matters most at this moment: both respondent groups waived, so a grant requires a call for a response and a second distribution first. It decomposes the headline into P(response called or relist) times P(grant given that), which is the right model for a waived petition, and it lands well below the anchor. The outcome (first-conference denial, no response requested) matches that reading. Its points about the non-precedential opinion and the qualified-immunity ground check out against the staged appendix.

The grade is held to the middle by a factual defect in one of its four stated reasons. The rationale says that "Pet. 27 explicitly concedes" that "Petitioner did not challenge the fundamental-rights prong of the shocks-the-conscience standard below," and presents that as a quotation. I searched the staged `petition.txt` and found no such sentence. Page 27 says the opposite: "The issue was pressed and passed upon at every stage," citing the court of appeals briefs. The appendix does show the panel analysing the claim under a two-part framework and discussing Favish as the source of a rooted right, so an inference that preservation is contestable would have been fair. A quoted concession attributed to the petition is a different thing, and it is not in the record I was given. The rationale rests a "sharp" downward adjustment partly on it.

Smaller record errors: it dates the amicus brief October 29 and calls it post-distribution, where the docket I hold shows it filed October 27, the day before distribution. (I hold only the 2026-11-16 snapshot, not the one the candidate read, so I cannot rule out that its snapshot differed.) Its pooled anchor count differs trivially from the other candidates' and I did not mark it wrong.

So the number was the best and the framework was right, but part of the support for it was a quotation the record does not contain. I weighted that heavily because `reasoning_quality` measures soundness, not the result.

## Predicted reasoning (`predicted_reasoning_quality` 0.85)

I treated as central the four things the document commits to flatly: denial at the November 13 conference, no call for a response and no relist or redistribution, no noted writing, and no CVSG. All four are borne out by the docket and `outcome.json`. This is the most specific of the three forecasts. It rules out the response-request branch that a competent reader could have backed (the other candidates gave it 32-40%), and that call was right.

It does not reach the top anchor because the document's stated reason for the Court declining to call for a response leans on the same unsupported "concededly never raised" premise. The Court's reasons for a bare denial cannot be resolved from the record, so that claim is `unresolved`, not a miss, but a forecast whose stated mechanism rests on a premise the petition contradicts is not fully specific-and-borne-out. The conditional merits outlook (affirmance if granted) depends on a grant that never happened and earns neither credit nor penalty.

## Leakage

Forward cell, predicted 2026-10-30 while the petition was pending. Every call in the log is `outcome_only`, so I graded on the queries: provisioned record, schemas, statpack and docket metrics, pipeline source files, a corpus query on this docket's own number while it was open, and a glob for the candidate's own earlier prediction files on other dockets. None reaches an outcome for this petition, and nothing under `data/qp-topics/` was touched. `influenced_prediction` = `not_applicable`.

## Big case

My read is 0.25: a recurring doctrinal question across circuits, but an individual damages suit that ended in a routine first-conference denial.
