# Evaluation: gemini-baseline

**Cell.** Cert stage, scotus/9026000249 (Quaid v. Granet, No. 26-249), event `evt-petition-disposition`. Outcome: **denied**, resolved 2026-11-09, one distribution, no CVSG, no noted dissent. Forward prediction made 2026-10-15 against the 2026-10-15 snapshot, band `baseline` (sal-v4), frozen in `context.band`. So the harness pools the anchor on the risk set of that band. Votes are not scored at the cert stage. The segment base rate and skill score are left to the stamp, so this note refers only to "the stamped segment base rate".

**Scores.** P(grant) 0.005, predicted `denied`: correct = 1, Brier = 0.000025.

## Reasoning quality: 0.5
The conclusion is right and the reasons given are valid: an unpublished memorandum, a state-law litigation-privilege question, no federal split, and a vexatious-litigant finding that makes the vehicle less clean. But the rationale is a single thin paragraph, and its anchor is misread. It cites "approximately 0.9–1.3%" as the baseline grant rate. That is the band's terminal rate in recent Terms of the build the candidate was placed against (rebuilt with `statpack-at`; 2025 0.9%, 2024 1.3%). A prediction carrying a frozen band faces the bracketed risk-set rate, about 4–6% per Term in the same table. The final number survives because the adjustment direction is right, but the yardstick was the wrong population. The rationale also does not engage the petition's actual argument, Kimmel and the noncommunicative-acquisition distinction, and it reads only part of the record: the questions presented and the head of the appendix, not the petition or the brief in opposition.

## Predicted reasoning: 0.5
The central claims were all borne out: no further relist, no CVSG, denial, no separate writing. They are stated generically, with no timing or probabilities, and they commit to little beyond the outcome itself. That puts the document at the "right but generic" anchor.

## Leakage
Mode `forward`; not_applicable. There was one CourtListener caption search (result unobserved), directed at the district-court docket. The reasoning shows no post-decision fact, and there was no qp-topics read.
