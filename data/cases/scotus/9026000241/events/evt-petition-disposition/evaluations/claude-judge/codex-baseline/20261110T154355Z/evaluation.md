# Evaluation — codex-baseline — scotus/9026000241, evt-petition-disposition (cert)

**Outcome:** denied on Nov 9, 2026, after one distribution (Conference of Nov 6). No CVSG, no noted dissent. **Prediction:** denied, P(grant)=0.012. `correct`=1, Brier = 0.012² = 0.000144. The baseline and skill fields are the harness's to stamp. This is a cert cell, so no vote accuracy and no semantic grades are recorded. The prediction carries `semantic_claims: null`, which is expected at the cert stage.

## Reasoning quality: 0.85
This is the strongest analysis of the three. It anchors on a stated sal-v4 reached rate for the frozen `baseline` band, pooled over prior Terms only, and then gives reasons for moving well below it. All of those reasons come from the record:
- the Fifth Circuit's forfeiture holding at App. 6a on the Price-testimony and comparator arguments;
- the district court's actual engagement with Gonzalez at App. 27a–31a;
- the unpublished posture;
- a reading of Murphy v. Schmitt itself showing it was decided at the pleading stage, so the claimed split is not square.

It correctly notes that the bar-check claim rests on a separate pleading ground. The point it underweights is the respondents' waiver with no response called for. That is the strongest single denial signal for a paid petition, and the rationale mentions it only in passing. Without it, the analysis leaves the number higher than it should be (1.2%, against a terminal no-relist rate it cites as ~1.7%). The figure is still small and defensible. The rationale is clear about what it could and could not verify.

## Predicted reasoning: 0.6
I treated four claims as central:
1. Denial following the Nov 6 conference, on a November order list.
2. Zero further distributions.
3. No CVSG.
4. No separate writing.

All four were borne out. Its conditional content (how the QP would be narrowed, and a 55/45 split between summary disposition and plenary review if granted) is unresolved because no grant happened. The document is specific, but a waived-response paid petition from an unpublished affirmance gave a competent reader little reason to forecast anything else. Its central calls therefore have low discriminating value, which puts it a little above the generic midpoint and well short of the top.

## Leakage
The prediction ran forward. Its retrieval was limited to Gonzalez and Murphy lookups filtered before 2026-10-13, plus the provisioned record and statpack. One `find` excluded `data/qp-topics/*` by `-not -path`, which is not a read. No material on this petition's outcome was retrieved. Graded `not_applicable`.

## Big case
My own read is 0.12: a recurring doctrinal question in a poor, fact-bound vehicle.
