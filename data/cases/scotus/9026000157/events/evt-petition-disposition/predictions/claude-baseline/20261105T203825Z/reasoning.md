# Reasoning — Singh v. Second Judicial District Court of Nevada (No. 26-157)

**P(grant) = 0.20; predicted disposition: denied.**

## Inputs read
- Snapshot `record/snapshots/2026-11-05.json`; `record/context.json` (forward mode, band `baseline` under sal-v7, distribution_count 1, no CVSG, `cert_anchor.rate` = 0.0515).
- `record/documents/questions-presented.txt`, `petition.txt` (full text, not truncated), `appendix.txt` listed (Nevada Supreme Court opinion, 586 P.3d 858). There is no BIO yet: the response is due Nov 23, 2026.
- `record/same-question.json`: no petitions above the 0.5 threshold.
- `metrics/statpack.md`: modern cert disposition, relist, CVSG, amicus and salience-band cuts.

## Docket state
The petition was filed Jul 31, 2026. The private respondents waived a response on Aug 21. Three amicus briefs were filed in support of the petitioner: the Anglican Church in North America, former EEOC officials, and the Roman Catholic Archbishop of Las Vegas. The petition was distributed for the Oct 9 conference (Sep 16). **On Sep 22 the Court requested a response**, and the deadline was then extended to Nov 23. So the petition has one distribution, no relist and no CVSG.

## Anchor and adjustments
- Anchor: the frozen `cert_anchor` reached-rate for the `baseline` band is about 5.2%.
- **Up: the Court called for a response after a waiver.** That shows at least one Justice wanted a BIO. It is a low bar, since most called-for petitions are still denied, but it lifts this petition well off the floor.
- **Up: three amici at the petition stage.** The 2+ amicus bucket in the paid segment ends at about 18% granted and 4.5% GVR (n=1543 cases). That is a marginal cut correlated with the response call, so I do not stack it fully.
- **Up: an acknowledged split on a well-framed single QP.** The Nevada court itself said courts "are split." The petition lists CA2, CA8, CA9, CADC and four state high courts against CA5, CA6, CA11 and three state high courts, including the new CA5 *Lutheran Church–Mo. Synod v. Christian* (2026). Counsel is Sidley plus the Northwestern Supreme Court Clinic, a repeat Supreme Court team. Church autonomy has drawn the Court's recent attention (*Our Lady of Guadalupe*, *Catholic Charities* 2025).
- **Down: the Court just passed on a closely related question.** It denied *USCCB v. O'Connell* (No. 25-849) on May 26, 2026, and that petition included a neutral-principles QP (web search; I found no report of a noted dissent). The petition here distinguishes O'Connell on its federal appellate-jurisdiction threshold issues, which is plausible but not conclusive.
- **Down: finality under 28 U.S.C. § 1257 is a vehicle question.** The judgment comes from a state mandamus/prohibition writ that lets the trial proceed. The petition leans on *Atlantic Richfield v. Christian* (2020) and *Cox Broadcasting*. The BIO will likely press this point.
- **Down: the facts are a local intra-congregational bylaw dispute.** Some Justices may prefer a cleaner employment or tort vehicle.

Net: about 0.20. Most of the upside depends on what the BIO says and whether the petition then relists.

## Increments
- Relist increment 0.96: a BIO is due Nov 23, after which the petition is redistributed in the ordinary course. The residual covers withdrawal or settlement.
- CVSG increment 0.03: no federal party, and federal interest is limited, although the U.S. has filed in church-autonomy cases before.
- Summary route given a grant 0.05: no intervening decision invites a GVR. A summary reversal is conceivable but unlikely on a question of doctrinal scope.
- Dissent from denial given a denial 0.20: Justices Alito, Thomas and Gorsuch have written on religion-clause denials, but none was reported in O'Connell.

## Uncertainty
The biggest unknown is the BIO, which has not been filed. A strong finality or vehicle objection would pull this toward 10%. A weak BIO followed by relists would push it past 30%. My web searches were limited to two, and I did not consult CourtListener MCP.
