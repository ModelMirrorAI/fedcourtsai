# Evaluation: codex-baseline

Cert-stage cell, forward mode. Outcome: certiorari granted on 13 November 2026, limited to Questions 1 and 2, after one relist; plenary route.

## Scores

- `correct` = 1: predicted `granted`, actual `granted`.
- `brier_score` = (0.86 - 1)^2 = 0.0196.
- Vote accuracy is not scored on a cert cell. The base rate, the skill score and the claim scores are the harness's.

## Reasoning (`reasoning_quality` 0.86)

This is the most careful rationale of the three. Strengths:

- **Anchor handled correctly.** It pooled the frozen `federal` band over Terms strictly before 2026, excluded its own Term, and said the sample was small and heterogeneous. I rebuilt the statpack it was placed against (`statpack-at`, build `a14b36a1e190`, no alternative build); its pooled count and denominator reproduce from that build's sal-v4 table.
- **No double counting.** It said government sponsorship is already in the federal anchor and took the upward adjustment from the question's importance instead.
- **Read all three briefs, including the reply.** It was the only candidate to pick up the reply's point that D.V.D. had been granted on the Section 1252(f)(1) question and that the government suggested a hold. I confirmed the passage in the provisioned reply.
- **Weighed the opposition on its terms.** It dealt with the Chenery objection, the unappealed vacatur as a limit on the injunction question, and the absence of a circuit split, and kept grant likelihood apart from the merits.

Weaknesses:

- The companion case led it to put 18% on a cert-order disposition and to float a hold into 2027. The Court granted plenary review within five weeks and took the Section 1252(f)(1) question in this case, so the companion pulled the forecast a little the wrong way.
- 0.86 was well placed, but the listed offsets were given more weight than the outcome suggests they carried.

## Predicted reasoning (`predicted_reasoning_quality` 0.8)

Central claims, in the document's order of weight: a plenary grant; one further distribution and a November-December grant; no CVSG; which questions; the hold alternative.

- The disposition, the route, and the timing were specific and borne out. "One further distribution before a grant" and "November-December 2026" were both exactly right, and a reader could have called either differently.
- On the questions, it named Question 1 as the core and was right. It left Questions 2 and 3 open together ("may also be taken, but a narrowing ... is plausible"), so the actual limitation to Questions 1 and 2 is consistent with the document but not called by it.
- The hold-into-2027 scenario did not happen; it was framed as an alternative, so it costs little.
- The conditional content on a denial earns neither credit nor penalty.

Specific and mostly borne out, with the question-selection claim hedged: a little above the 0.75 anchor.

## Leakage

Forward cell, genuinely open when predicted (prediction and snapshot dated 13 October 2026; resolution 13 November 2026). The log shows local reads of provisioned inputs and the statpack, and three web-search rows whose results were unobserved; graded on their queries, they sought the Court's rules pages and never named this petition. No read under `data/qp-topics/`. `influenced_prediction` = `not_applicable`.
