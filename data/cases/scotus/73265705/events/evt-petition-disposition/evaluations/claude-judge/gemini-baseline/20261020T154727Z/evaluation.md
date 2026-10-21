# gemini-baseline — Google LLC v. VirtaMove (25-1230), cert disposition

**Outcome:** denied on 2026-10-19 (`actual_granted` 0), with no noted dissent.
**Prediction:** `denied`, P(grant) = 0.12. **Correct:** 1. **Brier:** 0.0144.

This is a cert-stage cell with a frozen `elevated` (sal-v4) band, so the harness stamps the base rate, the skill and the basis, and I left them null. For comparison, see the stamped segment base rate.

## Reasoning quality: 0.45
The number was well calibrated in hindsight, but the analysis behind it is thin.

**What it got right:**
- It cited the elevated-band anchor and the statpack's one-relist bucket. My check of `metrics/statpack.md` shows that bucket at about 13.4% grant plus GVR.
- It identified § 314(d)'s "final and nonappealable" bar as the central vehicle problem.

**Weaknesses:**
- It treated distribution count 2 as "exactly one relist." It did not notice that the first distribution was followed by the Court's request for a response, and the pack itself warns that a redistribution can be a reschedule before the first conference. So the main anchor rests on a misread signal.
- It does not engage with the opposition briefs: the mandamus posture, the government's opposition, or the dispute over the factual premise. It also does not engage with the response request or the amici.
- The claim that the Court "has recently strongly enforced" § 314(d) is asserted without any authority.
- The whole rationale is one paragraph, with no account of what was read.

The low Brier score is not credit for the analysis.

## Leakage
Forward cell. The prediction was made 2026-09-30, and the petition was resolved 2026-10-19. The log shows two CourtListener searches on the case caption that were not captured. The petition was pending at the time, so no outcome material could exist. Graded `not_applicable`.

## Semantic grading
This is a cert cell, so no `semantic_grades` block is written.
