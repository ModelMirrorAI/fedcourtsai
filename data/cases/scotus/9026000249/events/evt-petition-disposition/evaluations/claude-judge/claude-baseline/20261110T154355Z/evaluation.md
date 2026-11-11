# Evaluation: claude-baseline

**Cell.** Cert stage, scotus/9026000249 (Quaid v. Granet, No. 26-249), event `evt-petition-disposition`. Outcome: **denied**, resolved 2026-11-09, one distribution, no CVSG, no noted dissent. Forward prediction made 2026-10-15 against the 2026-10-15 snapshot, band `baseline` (sal-v4), frozen in `context.band`. So the harness pools the anchor on the risk set of that band. Votes are not scored at the cert stage. The segment base rate and skill score are left to the stamp, so this note refers only to "the stamped segment base rate".

**Scores.** P(grant) 0.004, predicted `denied`: correct = 1, Brier = 0.000016.

## Reasoning quality: 0.75
The anchor is correct: the bracketed `reached` rate for the frozen baseline band, pooled over Terms 2017–2025, about 5%. The rationale then cuts it to roughly a tenth for four sound reasons: pro se petitioners in the paid segment, an unpublished memorandum, a state-law question without a federal conflict, and a posture with no response requested and one distribution. It is candid about the unreadable reply and about having general knowledge of the petitioner. It reads somewhat less of the record than codex-baseline did, and it does not engage the petition's best doctrinal argument. Its summary-route note ("any grant here would most likely be a corrective order") sits awkwardly beside its own 0.3 conditional, a minor internal inconsistency. Overall it is sound and was borne out.

## Predicted reasoning: 0.6
Central claims: denial at the Nov 6 conference with no further distribution, an order-list entry around Nov 9–10, no CVSG, no dissent. All were borne out, including the dated timing (resolved 2026-11-09). The claims are specific but low in discrimination for this kind of petition. The conditional grant-route content is not graded.

## Leakage
Mode `forward`; not_applicable. Six local reads (the prompt, the provisioned record, the statpack). There were no web or MCP calls and no qp-topics read.
