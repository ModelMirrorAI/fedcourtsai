# Evaluation — claude-baseline

**Cell:** scotus/73281680, `evt-petition-disposition`, stage `cert`. Outcome: **denied** (2026-10-13), one distribution, no CVSG, no noted dissent from denial.

**Prediction:** denied, P(grant) = 0.08. **Correct:** 1. **Brier:** (0.08 − 0)² = 0.0064.

**Base rate:** the prediction froze band `baseline` under `sal-v4`, so the harness stamps the segment base rate and skill (risk-set anchor); I left them null. Compare against the stamped segment base rate.

**Votes:** cert-stage; noted votes are never scored, so `vote_accuracy` is omitted. **Semantic grades:** none (cert cell).

**Leakage:** forward mode, made 2026-10-03, before the conference. The log and prose show nothing about this petition's own disposition → `not_applicable`, not suspected.

**Reasoning quality (0.85):** Correct denial at 0.08. The strongest analysis: a transparent anchor (~5.1%), the Bouarfa reservation identified, conflicting authority found (Hosseini; Mukantagara, now vacated after Mullin v. Doe), and the near-twin Shaiban denial correctly weighed as strong evidence the Court would pass. It also read vehicle and advocacy signals and the BIO. The upward adjustment over the anchor slightly overweighted grant signals that its own downward evidence largely offset, but the analysis tracks why the Court denied.

**Big case (0.3):** Doctrinally meaningful but narrow immigration-reviewability question: whether 8 U.S.C. 1252(a)(2)(B)(ii) bars district-court review of eligibility findings underlying discretionary asylee adjustment, a point Bouarfa reserved. Low public salience, an individual petitioner, no amici; denied at the first conference without noted dissent.
