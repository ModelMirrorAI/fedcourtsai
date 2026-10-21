# Evaluation — gemini-baseline, Utah v. Mullins (No. 25-1115), evt-petition-disposition

**Stage:** cert. **Outcome:** denied (2026-10-19, after three distributions, no CVSG, no noted dissent).
**Prediction:** denied, P(grant) = 0.05. **Correct:** 1. **Brier:** (0.05 − 0)² = 0.0025.

**Base rate.** The prediction froze band `state` (sal-v4), so the segment base rate,
skill score and basis are the harness's. They are left null here, and the comparison
is against "the stamped segment base rate".

## Reasoning quality — 0.60

The analysis is correct on the essentials:

- It starts from the ~23% state-band anchor.
- It identifies the §1257 finality defect as the main reason to deny, and explains why resentencing keeps the federal question open for later review.
- It notes the alternative youth-consideration ground as a vehicle flaw.

The resulting number is the sharpest of the three and the best-calibrated against the outcome.

The write-up is thin, though:

- It is one paragraph with no record citations.
- It does not engage the claimed split, the State's reply (which it did not read), the stakes facts (Utah's prospective abolition of JLWOP, few affected inmates), or the absence of amicus support.
- Its merits framing is stated as conclusion rather than argued: that the State's position "contradicts the core substantive holding" of Miller/Montgomery that Jones left intact. That framing is contestable, given that Jones held a discretionary scheme sufficient.

The very large downward adjustment (0.23 → 0.05) is defensible but under-justified. This score grades the reasoning, not the low Brier.

## Leakage
This is a forward cell, made 2026-09-16, before the resolution. It made no web or MCP calls and read only provisioned inputs and the statpack. Graded `not_applicable`.

## Semantic grades
Not a merits cell: no semantic set is declared, and no block was written.
