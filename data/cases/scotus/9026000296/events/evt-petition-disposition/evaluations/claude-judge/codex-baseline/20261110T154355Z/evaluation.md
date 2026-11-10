# Evaluation — codex-baseline — scotus/9026000296, evt-petition-disposition

**Cell.** Cert stage, forward. No. 26-296, *Sethi v. U.S. Court of Appeals for the Ninth Circuit*, is a paid petition challenging a published six-month suspension from the Ninth Circuit bar over AI-fabricated citations. The federal respondents waived their response, the petition was distributed once for Nov. 6, 2026, and it was **denied on Nov. 9, 2026** with no noted dissent and no CVSG.

**Scores.** The predicted disposition was `denied` and the actual was `denied`, so `correct` = 1. With P(grant) = 0.025, `brier_score` = 0.000625. This is the highest Brier of the three candidates, but still very small. The segment base rate and skill score are stamped by the harness, and I quote none of my own.

**Reasoning (`reasoning_quality` 0.85).** This is the most careful analysis of the three:
- **A reproducible anchor.** It pools the prior-Term `baseline` risk set, states its method and does not mix in the current Term.
- **Close engagement with the record.** It notes that the Nov. 4 show-cause order already set out the fabricated citations and the candor duties, warned of suspension and offered a hearing, which Sethi did not request. That correctly undercuts the petition's *Ruffalo* framing.
- **Checks on the petition's own arguments.** It sees that QP 2 is complicated by the order's disclaimer of sanctioning AI use itself, and that the petition's cited split is not square on either QP.
- **A calibrated reading of the waiver.** It treats the waiver as a routine first-distribution posture rather than a concession, which is more accurate than reading it as a merits signal.
- **It retrieved *Ruffalo*'s text to check the doctrinal premise rather than taking the petition's word for it.**

Its 2.5% is somewhat high given how many of its own counterweights point to denial. The cut from roughly 5% to 2.5% is modest for a waived petition that has drawn no call for a response. That is a calibration point, not an error in the analysis.

**Leakage.** Forward mode, and the prediction (Oct. 15) predates the resolution. The log shows:
- shell reads of the provisioned record and the statpack;
- two generic web attempts about Rule 10, whose results were not observed;
- CourtListener lookups of *In re Ruffalo* (1968) only.

There was no qp-topics read and no lookup of this petition's disposition or later docket, and its retrieval.md says the same. Grade: `not_applicable`, with `leakage_suspected` false.

**Big case.** My own read is 0.12. The case is topical, but the outcome (a routine denial with no writing) and the fact-bound questions point to low stakes.

## Predicted reasoning

Grade: **0.65**. The central claims were:
1. Denial after the first conference on Nov. 6.
2. Zero further distributions, with a stated 12% chance of at least one more.
3. No CVSG.
4. A routine unexplained denial with no noted writing.

All four were borne out, and they come with specific probabilities. Its grant-branch analysis (a narrowed QP 1; 45% summary versus 55% plenary) applied only if the petition was granted, which did not happen, so it earns neither credit nor penalty. As with the other candidates, the claims that held are the modal outcome for this posture, so few readers would have called them differently. That keeps the grade off the top anchor.
