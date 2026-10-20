# claude-baseline — Google LLC v. VirtaMove (25-1230), cert disposition

**Outcome:** denied on 2026-10-19 (`actual_granted` 0), with no noted dissent. The petition was not held for the companion petitions.
**Prediction:** `denied`, P(grant) = 0.30. **Correct:** 1. **Brier:** 0.09.

This is a cert-stage cell with a frozen `elevated` (sal-v4) band, so the harness stamps the base rate, the skill and the basis, and I left them null. For comparison, see the stamped segment base rate.

## Reasoning quality: 0.60
This was the most thoroughly researched candidate.
- It used the same correct elevated-band anchor as the others.
- It read Google's reply. It noticed that the first distribution was superseded by the response request.
- It assembled the most relevant priors: the Court's denials of the earlier discretionary-denial challenges (Apple v. Optis, Mylan, Intel v. VLSI, Intel v. Vidal).
- It weighed the mandamus posture, Thryv/Cuozzo/Arthrex, the vehicle dispute and the lack of a circuit split.

The weakness is in how it combined those factors. Its own list of downward factors is long and well chosen, especially the uniform record of denials in this exact cluster. Even so, it nearly doubled the anchor, mostly on the strength of companion petitions and the general "climate." It also reached a two-stage estimate of 0.35–0.40 times 0.8 without grounding either factor. The companion-petition argument cut both ways. The candidate itself flagged that a denial on October 16 would make its figure too high, and that is what happened. Its "Where to discount me" section is honest and useful.

One small attribution gap: Tesla v. Granite (26-136) is cited as a companion petition, but no fetch of that docket appears in its retrieval record.

## Leakage
Forward cell. The prediction was made 2026-09-30, and the petition was resolved 2026-10-19. It fetched this case's own supremecourt.gov docket, Google's reply brief and the companion dockets. All of those calls were captured and all predate the resolution, and the candidate disclosed them in `retrieval.md`. That is legitimate forward signal. Graded `not_applicable`.

## Semantic grading
This is a cert cell, so no `semantic_grades` block is written.
