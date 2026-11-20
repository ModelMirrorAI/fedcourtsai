# Reasoning — Tedford's Tenancy, LLC v. City of New York (No. 26-110)

**P(grant) = 0.02; call: denied.**

## Inputs read
Snapshot `2026-11-19.json`; `questions-presented.txt`; `petition.txt` (QP, introduction, statement); `brief-in-opposition.txt` (both the City's and the State's briefs — QP, vehicle sections, merits-alternative section); `appendix.txt` (opening of the Appellate Division order); `record/related/26-107.json` (relation `vided-amicus`, 3 shared briefs); `context.json`; `same-question.json` (empty list — nothing scored above threshold). No reply brief is on the docket yet.

## Anchor
`context.json` freezes band `baseline` (sal-v8), `cert_anchor.rate` = 0.052, and an amicus line (arm `some`, 5 briefs) of 0.163. The statpack relist cut (terminal count 1: granted 8.3% + gvr 5.2%, n=2,539 resolved) is a shape check only; this petition's coming second distribution is the mechanical one that follows a called-for response, not a true relist.

## Why well below the anchor
1. **Vehicle mismatch on QP1.** The petition asks whether takings final-decision ripeness is jurisdictional (Article III) or prudential. The case comes from New York state court. Both BIOs make the point that Article III justiciability rules do not bind state courts (ASARCO v. Kadish), so the federal circuit split the petition describes is not presented by a state court applying its own ripeness doctrine. I find this persuasive as a vehicle objection.
2. **Preservation.** The State's BIO says the jurisdictional-versus-prudential argument was never raised or passed on below; the Appellate Division's order is a short memorandum that does not discuss the distinction.
3. **Independent alternative ground.** The Appellate Division also held the complaint fails to state a Lucas or Penn Central taking (the property still earns regulated residential and market commercial rent). The petition concedes this in a footnote and argues it is curable by amendment. An alternative merits holding makes the ripeness question non-dispositive.
4. **Decision below.** A short intermediate state appellate order, with leave denied by the New York Court of Appeals; QP2 (futility) is largely fact-bound application of Pakdel.
5. **Companion signal.** No. 26-107, Walls v. Prince George's County (same Pacific Legal Foundation counsel, a ripeness takings petition from the Fourth Circuit, sharing three VIDED amicus briefs) drew the same call for a response and was **denied on 9 Nov 2026** at its first post-response conference, with no relist. I read that docket rather than assume it; it is a text/brief-sharing link, not the Court's own Vide link, but the shared counsel, shared amici and same-day handling make it a real companion. If the Court passed on the federal-court vehicle for this family of questions, a state-court vehicle with an alternative holding is weaker still.

## What cuts the other way
- A response was requested after both respondents waived — someone in chambers wanted to see one. But that bar is low, and Walls got the same treatment and was denied.
- Five amicus briefs and experienced cert-stage counsel; several Justices have shown interest in rent-stabilization takings claims and in cleaning up takings ripeness after Knick and Pakdel. The amicus-line rate (16%) overstates here: the briefs are largely joint filings covering both this case and Walls.

Net: I put this at about 2%, below the 5.2% band anchor.

## Other claims
- `relist-increment` 0.96: the docket shows one distribution (conference of 28 Sept 2026) followed by the call for a response; the BIOs were filed 10 Nov, so redistribution for a December or January conference is near-certain barring withdrawal.
- `cvsg-increment` 0.01: no federal interest.
- `summary-disposition-route` 0.15 (conditional on grant): a grant here would most plausibly be plenary; a GVR would need an intervening decision I do not see pending.
- `dissent-from-denial` 0.03: Justices Thomas and Gorsuch are the plausible writers, but Walls was denied with no noted writing.

## Uncertainty / discounts
I did not read the Walls petition, so I cannot say how closely its QP matches. I did not read the full amicus briefs. No MCP or web retrieval was used; the forecast rests on the provisioned record and the statpack.
