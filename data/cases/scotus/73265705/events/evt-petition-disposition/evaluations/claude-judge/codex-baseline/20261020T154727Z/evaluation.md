# codex-baseline — Google LLC v. VirtaMove (25-1230), cert disposition

**Outcome:** denied on 2026-10-19 (`actual_granted` 0), with no noted dissent and two distributions.
**Prediction:** `denied`, P(grant) = 0.16. **Correct:** 1. **Brier:** 0.0256.

This is a cert-stage cell. The prediction froze band `elevated` (sal-v4), so the harness stamps the segment base rate, the skill and the basis from the frozen band's risk set. I left those fields null. For comparison, see the stamped segment base rate.

## Reasoning quality: 0.80
This is a well-disciplined analysis. The candidate anchored on the sal-v4 elevated-band reached rate for the Terms strictly before 2025, which is the correct cohort for this cell. It then moved off that anchor with reasons tied to the case:
- Pushing the rate up: the June response request, the seven amici and real cross-industry stakes.
- Pushing it down: the mandamus posture and the "clear and indisputable right" hurdle, the government's opposition, the nonprecedential decision below, and the factual dispute over whether the PTO used a categorical age rule or a holistic assessment.

It correctly saw that the two distributions overstate how much attention the Court had given the petition, because the first was effectively superseded by the response request. It also read Cuozzo's limit on review accurately and said plainly what it did not read: the reply, the appendix and the amicus briefs. Each of the downward factors is the kind that plausibly drives a quiet denial, and the net figure stayed near the anchor without overreaching. The score is not higher because the candidate did not get the reply (it was available on the public docket) and did not consider the overlapping companion petitions as a possible reason for a hold.

## Leakage
Forward cell. The prediction was made 2026-09-30, and the petition was resolved 2026-10-19. Nothing outcome-revealing could have existed when it was made. The log shows only provisioned reads, statpack reads, two web calls on statute text (not captured) and a Cuozzo lookup. Graded `not_applicable`.

## Semantic grading
This is a cert cell, so no semantic set is declared and no `semantic_grades` block is written.
