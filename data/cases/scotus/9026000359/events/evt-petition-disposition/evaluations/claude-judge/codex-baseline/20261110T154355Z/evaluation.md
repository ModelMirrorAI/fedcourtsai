# Evaluation: codex-baseline, scotus/9026000359, evt-petition-disposition

**Cell:** cert stage, forward, distribution moment. **Outcome:** `denied` (2026-11-09), one distribution, no CVSG, no noted dissent.

**Scores.** Predicted `denied` with P(grant) = 0.012, so `correct` = 1 and Brier = 0.000144. The segment base rate, basis and skill are stamped by the harness (frozen band `baseline`, sal-v4). Compare against the stamped segment base rate. Vote accuracy does not apply on a cert cell.

**Reasoning quality: 0.85.** This is the most closely record-engaged rationale of the three. It anchors on the band's risk-set rate and correctly limits the pool to Terms before the case's own. It treats the relist and CVSG cuts as shape only, not as hazards. It then works through each question presented against specific appendix pages:
- the discretionary-permit entitlement holding;
- the takings analysis, where the court assumed a property interest and addressed delay, bad faith and causation;
- the final-policymaker holding on First Amendment retaliation.

It reads the waiver correctly as a lack of an affirmative signal, not as a merits concession. Its slightly higher number (1.2%) is defensible given the published opinion and the takings-delay theme, though the waiver arguably warranted a lower figure. The prose is long, but length earned nothing here. The grade reflects the precision of the issue-by-issue analysis.

## Predicted reasoning

**Grade: 0.6.** The central claims are:
- denial without a separate writing, on an order list after the November 6 conference;
- zero additional distributions (7% on the alternative);
- no CVSG;
- no noted dissent or statement.

All four were borne out. The forecast is specific about timing and the scale of the alternatives, but the central call is the default for this posture. The conditional content (a narrowed QP4 takings question, 15% summary route) is unresolved.

## Leakage

The cell is forward, with `cutoff` null and a 2026-10-15 snapshot. The four web calls were unobserved, so they are graded on their queries. Each asked about Supreme Court Rule 10 or the Court's rules PDF, none named this case, and the candidate disclosed them, which counts in the cell's favour. Its find commands excluded data/qp-topics. `not_applicable`, not suspected.

## Big case

0.07. The case is a local, fact-bound permitting dispute, denied at its first conference.
