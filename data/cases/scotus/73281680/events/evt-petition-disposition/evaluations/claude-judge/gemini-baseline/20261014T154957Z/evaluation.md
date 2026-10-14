# Evaluation — gemini-baseline

**Cell:** scotus/73281680, `evt-petition-disposition`, stage `cert`. Outcome: **denied** (2026-10-13), one distribution, no CVSG, no noted dissent from denial.

**Prediction:** denied, P(grant) = 0.02. **Correct:** 1. **Brier:** (0.02 − 0)² = 0.0004.

**Base rate:** the prediction froze band `baseline` under `sal-v4`, so the harness stamps the segment base rate and skill (risk-set anchor); I left them null. Compare against the stamped segment base rate.

**Votes:** cert-stage; noted votes are never scored, so `vote_accuracy` is omitted. **Semantic grades:** none (cert cell).

**Leakage:** forward mode, made 2026-10-03, before the conference. The log and prose show nothing about this petition's own disposition → `not_applicable`, not suspected.

**Reasoning quality (0.5):** Correct denial at 0.02. Anchor is sound (the baseline-band reached rate), but the downward adjustment rests on loosely supported premises: it calls the petitioner pro se without addressing the firm address on the docket, and it asserts uniform circuit agreement extending Patel to clause (ii) without engaging contrary authority (Hosseini, 6th Cir.; Mukantagara, 10th Cir., later vacated) or the Shaiban denial. The conclusion was right, but the support is thin and partly overstated.

**Big case (0.3):** Doctrinally meaningful but narrow immigration-reviewability question: whether 8 U.S.C. 1252(a)(2)(B)(ii) bars district-court review of eligibility findings underlying discretionary asylee adjustment, a point Bouarfa reserved. Low public salience, an individual petitioner, no amici; denied at the first conference without noted dissent.
