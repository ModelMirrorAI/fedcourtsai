# Reasoning — P(grant) = 0.04

**Inputs read.** I read snapshot `record/snapshots/2026-10-31.json` (forward mode, `cutoff: null`), plus `context.json` (band `baseline`, sal-v6, distribution_count 1, no CVSG, Term 2026, `cert_anchor.rate` 0.0519). I also read the provisioned petition, questions-presented and appendix (the Second Circuit's March 30, 2026 opinion on remand, 171 F.4th 575). No BIO was filed, since both respondents waived. `same-question.json` lists no similar petitions.

**Anchor.** The frozen cert anchor is 5.2%: the baseline band's pooled reached rate over the prior ten Terms. The statpack table shows that rate at roughly 4–6% per Term. I start there.

**Adjustments.**
- *Down:* There is no circuit split. The petition argues conflict with this Court's void-judgment and mandate-recall cases (Calderon, Pennoyer, Plaut) and points to no court that came out the other way on similar facts. The posture is unique, which makes the case important to the parties but cuts against cert-worthiness.
- *Down:* The 2d Cir. opinion shows that the plaintiffs moved to recall the mandate in 2018. This Court's 2020 GVR in No. 19-764 vacated the order denying recall in light of the PSJVTA, and the statute expressly applies to pending cases. So the "final, completed case" premise of the Plaut argument is contestable, and the Court itself sent the recall question back.
- *Down:* In Fuld v. PLO (2025), the Court unanimously upheld PSJVTA jurisdiction. The United States, a respondent here, waived a response, which signals that the government sees nothing worth fighting about.
- *Up:* The case carries real stakes: a $655.5M trebled judgment, foreign-relations sensitivity, sophisticated counsel, and a clean legal question about the limits of mandate recall that formalist Justices may find interesting. There is a realistic chance of a call for a response.

The net is slightly below the anchor, at 0.04.

**Claims.** I put relist-increment at 0.38: about 0.33 for a call for a response (which leads to a redistribution) plus a small chance of a plain relist. I put cvsg-increment near zero because the SG is already a party. Summary-disposition-route given a grant is 0.08, since no intervening decision exists. Dissent-from-denial given a denial is 0.04.

**Uncertainty.** Without a BIO I can't judge how well respondents would rebut the finality point. My call-for-response estimate is a judgment call, and no committed table conditions on it.

**Retrieval.** One malformed corpus query (bad `--era`) failed. Two docket-number lookups confirmed the prior related dockets (19-764, 24-151). I made no web or MCP calls.
