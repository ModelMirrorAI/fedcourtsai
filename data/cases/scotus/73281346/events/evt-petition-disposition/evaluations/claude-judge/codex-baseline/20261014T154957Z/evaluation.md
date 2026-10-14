# codex-baseline — evaluation

## Cell

Cert-stage, forward cell. The outcome was **denied** on 2026-10-13, after the September 28, 2026 long conference: three distributions, no CVSG, and no noted dissent. The prediction froze `elevated` / `sal-v4`, so the harness stamps the segment base rate, the skill score, and the basis from the risk set. I leave them null and quote no rate of my own; comparisons below are to "the stamped segment base rate". `claim_scores` belongs to the harness. Votes are not scored at the cert stage. There is no semantic set to grade.

## Scores

- predicted `denied`, which was correct (1). P(grant) 0.12, so Brier = 0.0144.
- reasoning_quality **0.85**.

## Assessment

Rigorous and well-calibrated.

- **Anchor.** It computes the elevated reached-band anchor transparently (484/2,810 ≈ 17.2% over OT2017–2024) and declines to stack the response request and the amici on top of a band that already reflects attention.
- **Docket history.** It reads the two distributions as briefing-driven rather than a substantive relist.
- **Record engagement.** It works through the record itself rather than the parties' characterizations: the factual disputes over the weapon and the decedent's movement, the inadequate-briefing finding (App. 30a–31a), and the alternative analogies (Tenorio, Carr) that survive even if the escalation rationale falls.
- **Fairness to petitioners.** It credits the officer-created-danger language petitioners can attack (App. 28a n.12), and it correctly distinguishes Bond's timing point.

Its move below the anchor to 0.12 matches the direction its own analysis supports, and the denial bore that out. A minor quibble: it reads somewhat procedural, and it did not have the reply text. Like claude-baseline, it scores **0.85**: codex-baseline's tighter internal consistency balances claude-baseline's somewhat richer use of recent comparable dispositions.

## Leakage

Forward; not_applicable. External lookups were limited to the Bond and Barnes precedents.
