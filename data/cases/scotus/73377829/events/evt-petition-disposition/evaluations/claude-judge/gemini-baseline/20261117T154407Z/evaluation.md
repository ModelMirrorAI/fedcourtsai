# Evaluation — gemini-baseline

**Cell:** cert stage, forward. Outcome: petition **denied** on 2026-11-16 (standard denial, no noted dissent, two distributions in total).

## Scores

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.15 − 0)² = 0.0225.
- Segment base rate, skill and basis are the harness's to stamp; left null.
- No vote accuracy on a cert cell; no semantic set is declared on a cert cell.

## Reasoning quality — 0.40

The direction is right and the structure is sensible: anchor on the baseline band, move up for the response request after waiver, move down for the absence of a circuit split and the Court's reluctance to review the Judicial Conference's internal machinery. Three things pull the grade down.

1. **Size of the adjustment.** Tripling the anchor to 0.15 on the strength of a response request is not argued for; the document calls it a signal of "at least one Justice's strong interest" and stops. A response request needs one Justice and is routinely followed by denial. The resulting number is the worst-calibrated of the three for a case that was denied at the first post-response conference without comment.
2. **A factual claim the record does not support.** The rationale says the petition is "supported by numerous amici including law professors, Members of Congress, and advocacy groups." The docket carries one motion for leave to file an amici brief (Georgia Association for Women Lawyers, et al.). That overstatement feeds both the probability and the big-case score.
3. **No engagement with the vehicle.** The petition's appendix shows the Fourth Circuit declined to reach the Title VII-exclusion challenge as unpreserved and rested the due-process holding on fact findings reviewed for clear error. The log shows only the first 100 lines of the petition were read, and none of this appears.

The 0.25 dissent-from-denial figure is likewise asserted from the gravity of the allegations rather than from any record signal. (The claims themselves are scored in code; this is a remark on the reasoning only.)

## Predicted reasoning — 0.20

Central claims as the document weights them: (1) at least two further distributions; (2) on denial, expect a dissent or statement from a liberal Justice; (3) no CVSG; (4) the framing of strong interest and significant amicus support. The document never states its own disposition — it gives an "if granted" and a "should the Court deny" branch — so what the outcome resolves is the procedural path and the denial branch.

- (1) failed: one further distribution (Oct 28 for the Nov 13 conference), then denial.
- (2) failed: bare denial, no noted dissent or statement.
- (3) held, but it was close to entailed by the SG's party role and earns little.
- The "if granted" content (QP 1 taken, CAA question left behind) is conditional on an event that did not happen: neither credit nor penalty.

Two specific central calls failed and the one that held was not discriminating; the document is not wrong in direction on the disposition only because it did not commit to one. Graded just below the 0.25 anchor.

## Leakage

Forward cell, predicted a month before resolution. The log shows provisioned inputs and the committed statpack only; nothing in the queries or prose touches the disposition. `not_applicable`, not suspected. All rows are `unobserved`, so this rests on the queries and the prose rather than on results.

## Big case

My read: 0.35 — institutionally sensitive and watched, but fact-bound, splitless, lightly supported by amici, and disposed of without comment.
