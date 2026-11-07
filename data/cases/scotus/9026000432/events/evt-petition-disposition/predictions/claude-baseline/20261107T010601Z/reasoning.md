# Reasoning — scotus/9026000432 (No. 26-432), Hamrit v. Citigroup Global Markets

**P(grant) = 0.004. Call: denied.**

## Record read
- Snapshot `record/snapshots/2026-11-07.json`: paid petition docketed Sep 30, 2026 from the Second Circuit (No. 25-3091). The petitioner is pro se (no counsel of record; he signs as his own attorney). Respondents (Citigroup entities) filed a **waiver** of response on Oct 28. Distributed once, for the Conference of Dec 4, 2026. No call for response, no CVSG, no amici, no relist.
- `questions-presented.txt`: one QP. Did the Second Circuit abuse its discretion by dismissing as frivolous, on its own motion and without notice, the balance of an appeal from a Rule 41(b) failure-to-prosecute dismissal, while ruling on a motion that asked to dismiss only the interlocutory part?
- `petition.txt` / `appendix.txt`: the decision below is a one-paragraph unpublished order. It cites *Neitzke v. Williams* and *Pillay v. INS* (the circuit's inherent power to dismiss frivolous appeals). Rehearing en banc was denied without a noted dissent. The petition argues party presentation and notice before sua sponte dismissal, and asks for summary correction. Behind it is a long run of earlier nonfinal appeals that went nowhere (an order compelling arbitration, then a Rule 41(b) dismissal).
- `same-question.json`: empty list. No similar petitions were found.

## Anchoring
- `context.json`: band `baseline` (sal-v7). `cert_anchor.rate` = 0.0515, the pooled reached rate for the band over the prior 10 Terms. The statpack table matches (baseline reached rate of roughly 4–6% per Term).
- I adjust far below the anchor. The baseline band covers every paid petition, and its grant rate comes mostly from counseled petitions that later draw a response or a relist. This petition has every negative marker: a pro se filer, a waiver by the respondent, no request for a response, a fact-bound error-correction question, an unpublished summary order, no circuit split alleged, and procedural history that suggests a poor vehicle (failure to prosecute after an arbitration was compelled). Pro se paid petitions where the respondent waives are granted at well under 1%. The only route that is not a denial is a summary vacatur, and that would require a response to be called for first. I see no reason the Court would.

## Other claims
- relist-increment 0.04: there is one distribution so far. Another one would most likely come from a call for response (rare here) or a reschedule.
- cvsg-increment 0.001: this is a private dispute with no federal interest.
- summary-disposition-route 0.35 (given a grant): if the Court acted at all, a summary correction is a plausible form, but the conditional is poorly determined.
- dissent-from-denial 0.005: these petitions almost never draw a separate writing.

## Uncertainty / discount
I am confident in the denial. The small remaining probability covers an unusual call for response. The corpus query returned priors that had nothing to do with this case, so it did not move the number. The CourtListener MCP and web were not used, because the provisioned record was sufficient.
