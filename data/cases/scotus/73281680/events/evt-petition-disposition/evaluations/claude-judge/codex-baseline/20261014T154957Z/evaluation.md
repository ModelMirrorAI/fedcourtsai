# Evaluation — codex-baseline

**Cell:** scotus/73281680, `evt-petition-disposition`, stage `cert`. Outcome: **denied** (2026-10-13), one distribution, no CVSG, no noted dissent from denial.

**Prediction:** denied, P(grant) = 0.06. **Correct:** 1. **Brier:** (0.06 − 0)² = 0.0036.

**Base rate:** the prediction froze band `baseline` under `sal-v4`, so the harness stamps the segment base rate and skill (risk-set anchor); I left them null. Compare against the stamped segment base rate.

**Votes:** cert-stage; noted votes are never scored, so `vote_accuracy` is omitted. **Semantic grades:** none (cert cell).

**Leakage:** forward mode, made 2026-10-03, before the conference. The log and prose show nothing about this petition's own disposition → `not_applicable`, not suspected.

**Reasoning quality (0.75):** Correct denial at 0.06. Carefully bounded reasoning: a transparent pooled baseline-band anchor (~5.1%), honest about what was missing (petition, BIO), correctly treats response extensions as not relists, and correctly says that an unresolved question is not a circuit split. The small upward adjustment was reasonable but not decisive. It missed the most informative comparator (the Shaiban denial) and the state of contrary circuit authority.

**Big case (0.3):** Doctrinally meaningful but narrow immigration-reviewability question: whether 8 U.S.C. 1252(a)(2)(B)(ii) bars district-court review of eligibility findings underlying discretionary asylee adjustment, a point Bouarfa reserved. Low public salience, an individual petitioner, no amici; denied at the first conference without noted dissent.
