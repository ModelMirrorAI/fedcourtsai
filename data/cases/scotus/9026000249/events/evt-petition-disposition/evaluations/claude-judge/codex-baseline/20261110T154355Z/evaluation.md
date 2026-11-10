# Evaluation: codex-baseline

**Cell.** Cert stage, scotus/9026000249 (Quaid v. Granet, No. 26-249), event `evt-petition-disposition`. Outcome: **denied**, resolved 2026-11-09, one distribution, no CVSG, no noted dissent. Forward prediction made 2026-10-15 against the 2026-10-15 snapshot, band `baseline` (sal-v4), frozen in `context.band`. So the harness pools the anchor on the risk set of that band. Votes are not scored at the cert stage. The segment base rate and skill score are left to the stamp, so this note refers only to "the stamped segment base rate".

**Scores.** P(grant) 0.005, predicted `denied`: correct = 1, Brier = 0.000025.

## Reasoning quality: 0.85
This is the strongest rationale of the three. It anchors correctly on the bracketed baseline `reached` risk-set rate for the frozen band (Terms 2017–2025, strictly before OT2026). That matches the build the candidate was placed against (I rebuilt it with `statpack-at`). It then gives four discrete reasons for going far below the anchor, and each one is supported by the record:
- the question is predominantly state law (§ 47(b));
- the Ninth Circuit memorandum is unpublished;
- the vehicle is weak, because the petition itself carves out the Government Claims Act and service rulings;
- the petition does make a real doctrinal point (Kimmel's communicative/noncommunicative line), but the district court addressed it.

It deliberately avoids leaning on pro se status or the petitioner's identity. It is candid that the cert reply was unreadable. The denial bears out the analysis. Small deduction: the tenfold cut from the anchor is a judgment call, though the rationale says so openly.

## Predicted reasoning: 0.6
Central claims: denial with no further distribution, an orders list in November, no CVSG, no noted dissent. All of them were borne out, and the claims are specific: a 4% relist chance and a dated timing call. But for a paid pro se baseline petition on its first distribution, a competent reader would almost certainly have made the same calls, so the document earns little for discrimination. The conditional content (narrowed question presented, 35% summary route) depends on a grant that did not happen and is neither credited nor penalized.

## Leakage
Mode `forward`; not_applicable. The web calls were generic Supreme Court Rules queries. The CourtListener calls retrieved Kimmel v. Goland (1990). Nothing in the log or the reasoning reflects this petition's disposition, and there was no qp-topics read.
