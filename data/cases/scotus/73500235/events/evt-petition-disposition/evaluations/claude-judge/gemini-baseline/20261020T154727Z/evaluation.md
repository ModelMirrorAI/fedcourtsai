# Evaluation — gemini-baseline

**Cell:** scotus/73500235 (Walid bin ‘Atash v. United States), `evt-petition-disposition`, stage `cert`. **Outcome:** `denied` on 2026-10-19 (`actual_granted` 0, no noted dissent from denial, three distributions).

**Baseline:** the scored prediction froze band `elevated` under `sal-v4`, so the segment base rate, skill score and basis are the harness's risk-set stamp; I left them null and quote only "the stamped segment base rate". `correct` and `brier_score` are written as my independent read; the stamp recomputes both. Votes are not scored on a cert cell, and no semantic set is declared, so no `semantic_grades` block is written. The claims block is scored in code and is not graded here.

**Prediction:** `denied`, P(grant) = 0.28. **correct** = 1, **Brier** = (0.28 − 0)² = 0.0784.

## Reasoning quality: 0.40

Right direction, thin analysis. It takes a single Term's elevated rate (OT2024, 17.9%) as the anchor instead of pooling the prior Terms. The difference is small here, but the method is weaker. It then moves *up* to 0.28 on the stakes, the 2–1 panel and the mandamus framing. But:
- It never engages the brief in opposition's central points: the repealed court-martial rule, exclusive D.C. Circuit jurisdiction, so no recurring conflict, and the claim that the dispute concerns how the mandamus standard was applied rather than the standard itself.
- It never addresses the *Dean* conflict on which the petition's cert-worthiness rests.
- It notes the interlocutory posture cuts against review, then argues the capital consequences overcome it, without support.
- It does not read the two distributions as reschedules. It also attributes the expected further distribution to Justices needing time on a complex record, which is speculation.

The 0.50 dissent-from-denial estimate ("very likely given the 2-1 split") overweights a panel split. The denial was silent. The document is short and sets out conclusions more than it argues for them.

## Leakage

Forward. Two web searches named this case and its 2026 certiorari status. Both rows are `unobserved` (log coverage 0.0, the engine's standing shape), so I graded them on their queries. They ran on 2026-10-05/06 while the petition was pending (resolved 2026-10-19), so no disposition could surface, and the reasoning treats the case as undecided. This is ordinary forward retrieval: `not_applicable`, not suspected.
