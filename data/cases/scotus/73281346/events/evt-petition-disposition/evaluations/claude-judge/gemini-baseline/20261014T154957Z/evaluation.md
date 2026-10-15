# gemini-baseline — evaluation

## Cell

Cert-stage, forward cell. The outcome was **denied** on 2026-10-13, after the September 28, 2026 long conference: three distributions, no CVSG, and no noted dissent. The prediction froze `elevated` / `sal-v4`, so the harness stamps the segment base rate, the skill score, and the basis from the risk set. I leave them null and quote no rate of my own; comparisons below are to "the stamped segment base rate". `claim_scores` belongs to the harness. Votes are not scored at the cert stage. There is no semantic set to grade.

## Scores

- predicted `denied`, which was correct (1). P(grant) 0.35, so Brier = 0.1225.
- reasoning_quality **0.45**.

## Assessment

The label was right, but it sits awkwardly beside the number and the prose. The rationale ends by calling the petition "a strong candidate for a grant or a GVR", then prices it at 0.35 and still predicts denial. It roughly doubles the ~17% pooled band anchor, and the support for that jump is thin:

- It relies on a generic "track record of summarily reversing" qualified-immunity denials.
- It counts the call for a response and the two police amici. The band already partly prices those signals.

It engages with none of the vehicle problems that actually drove the outcome: the summary-judgment fact disputes (an unarmed decedent on the facts taken in respondent's favor), the forfeiture and briefing issues the BIO raised, and the lack of a split. Those are exactly the reasons a per curiam correction was unlikely. One point is right and useful: the two distributions do not amount to a real relist, because the September 28 conference is effectively the first consideration. Overall the reasoning is short, one-sided toward a grant, and miscalibrated in the direction the outcome punished.

## Leakage

Forward; not_applicable. There was no outcome material (see the JSON notes).
