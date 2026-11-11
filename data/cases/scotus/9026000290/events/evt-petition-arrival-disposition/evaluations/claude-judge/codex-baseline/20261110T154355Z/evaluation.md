# Evaluation — codex-baseline, evt-petition-arrival-disposition (scotus/9026000290)

**Stage:** cert (arrival moment, forward). **Outcome:** `denied` on 2026-11-09 after one distribution (conference of 11/6/2026). There was no CVSG and no noted dissent.

## Score

- Predicted `denied` with P(grant) = 0.004. `correct` = 1; Brier = 0.004² = 0.000016.
- The segment base rate, its basis and the skill score are left to the harness stamp. Compare against "the stamped segment base rate".
- No votes were predicted, and votes are never scored on a cert cell.

## Reasoning (`reasoning_quality` = 0.80)

This is a careful, well-sourced rationale. The anchor is the `baseline` band's bracketed reached rate under sal-v4, pooled over OT2017–OT2025, which comes to 638 / 12,720 ≈ 5.02%. I rebuilt the statpack the candidate ran against (`statpack-at`, build 2420d5dd72e1, the same for all three candidates) and its figure matches exactly. The candidate also correctly declined to use the terminal relist-0 bucket as an arrival anchor.

The downward adjustments are the right ones and are argued from the record:
- The claimed "conflict" is between the Court's own precedents, not a demonstrated appellate split.
- The judgment under review is an unexplained state writ denial following a demurrer to a seventh amended complaint, which raises finality and preservation questions.
- The presentation is broad and fact-bound.

The main omission is that the candidate never names the petitioner's pro se status. That is arguably the strongest single discount, and the rationale reaches a similar number without it. The reviewability discussion is appropriately hedged as a vehicle discount rather than a jurisdictional finding. The rationale states its limitations and statpack vintage candidly.

## Leakage

The cell is forward. The prediction was made 2026-09-27, before the distribution and the denial. The four web-search rows are unobserved, but their queries were general (Rule 10, § 1257) and did not name this case. retrieval.md discloses that they returned nothing usable. Nothing in the log or prose shows outcome material, so the grade is `not_applicable`.

## Big case

My own read is 0.03: a local, pro se code-enforcement dispute with no split and no institutional interest.

## Predicted reasoning (`predicted_reasoning_quality` = 0.70)

I treated these as the central claims, in the document's order:
1. Denial by unsigned order — **borne out**.
2. Exactly one initial distribution and no relist — **borne out**.
3. Denial timed for November or December 2026 — **borne out** (11/9).
4. No CVSG — **borne out**.
5. No separate writing — **borne out**.

Every central claim held, and the document commits to a timing window and to a distribution count. However, those are close to the modal path for any paid petition of this kind, so the document called little that a competent reader would have called otherwise. The two-month timing window is less tight than it could have been. Its "if granted" question reformulation is conditional on a grant that did not happen, so it earns neither credit nor penalty.
