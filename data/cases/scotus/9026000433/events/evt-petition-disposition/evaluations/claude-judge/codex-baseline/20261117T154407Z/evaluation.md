# Evaluation: codex-baseline

**Outcome:** petition denied on 2026-11-16, after one distribution (Nov 13 conference), with no response called for, no CVSG and no noted dissent.

**Scores:** `correct` = 1 (predicted `denied`, actual `denied`). Brier = (0.12 - 0)^2 = 0.0144, the weakest of the three candidates. This is a cert-stage cell; the segment base rate, basis and skill are the harness's to stamp and are left null. No votes are scored on a cert cell, and no semantic set is declared.

## Reasoning (`reasoning_quality` 0.64)

The method is careful. The rationale computes the prior-Term `baseline` risk-set anchor from the statpack's exact fields, excludes the own-Term row, and correctly labels the relist, CVSG and amicus cuts as terminal-count comparisons that are not independent multipliers. It is explicit about what it did not read (the truncated appendix remainder, the amicus brief's text) and does not treat absent material as evidence.

The legal analysis is accurate on the points I checked against the staged record: the Third Circuit decision is non-precedential, and the judgment rests on qualified immunity, with the panel assuming the historical-pedigree point in petitioner's favour and still finding no clearly established right. The candidate also read DeMarcus (11th Cir. 2025), one of the petition's split cases, and found that it too was resolved on clearly-established grounds. That is the most useful piece of independent work in any of the three rationales, and it cuts against the petition.

The weakness is the conclusion drawn from all this. Having found that the vehicle is non-precedential, that the judgment rests on an immunity ground the question presented may not disturb, and that the split is less clean than the petition says, the rationale still moves the probability to more than double its anchor on the strength of the alleged conflict, the dissent and one amicus brief. Its own findings pointed down, and the first-conference denial without a response request bears that out. The analysis was sound and the weighing was not.

## Predicted reasoning (`predicted_reasoning_quality` 0.65)

I treated as central the disposition without a writing, the path (denial after the first conference without another distribution, against a 32% chance of redistribution) and the CVSG call. All resolved in the document's favour. The document states the modal path plainly, and that path is what happened. It hedges about a third of its weight onto a redistribution branch and commits to nothing more specific than the modal path, so it sits between the generic and specific anchors. The conditional-on-grant content and the author forecasts are unresolved and earn neither credit nor penalty.

## Leakage

Forward cell, predicted 2026-10-30 while the petition was pending. The log shows provisioned inputs, statpack arithmetic, a generic corpus query, CourtListener reads of DeMarcus (a cited authority), and one hosted web search whose result was not captured; its queries targeted Lewis and DeMarcus, not this petition. The only legible document date is 2026-10-22. `influenced_prediction` = `not_applicable`.

## Big case

My read is 0.25: a recurring doctrinal question across circuits, but an individual damages suit that ended in a routine first-conference denial.
