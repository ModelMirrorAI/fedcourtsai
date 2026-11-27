# Reasoning — P(grant) 0.03

**Inputs read.** Snapshot `2026-11-26.json`, `context.json` (forward mode, band `baseline`, sal-v9, one distribution, no CVSG, zero amicus briefs), `questions-presented.txt`, the brief in opposition, the cert reply, `lower-court-docket.txt`, and parts of the petition. `same-question.json` lists no matching petitions. I relied on the BIO's and the lower-court-docket file's description of the decision below (unpublished per curiam, CA4 No. 24-4022) rather than reading `decision-below.txt` in full.

**Anchor.** `cert_anchor.rate` is 5.2% (baseline band, reached rate, prior ten Terms). The amicus-adjusted reference line for a no-amicus baseline petition is 2.7% (`cert_amicus_line`, arm `none`, n=10,350), which the prompt says is a floor since a brief could still arrive; with the petition already distributed after full briefing, I treat it as close to the right starting point. The statpack relist cut puts never-relisted paid petitions at about 1.8% granted or GVR'd (terminal bucket, so it understates).

**Adjustments up.**
- Question 1 rests on a real, acknowledged split: the Second Circuit requires reasonable foreseeability for conspiracy venue; the Third, Fourth, Sixth and Ninth do not. The decision below itself acknowledges the Second Circuit's rule.
- Experienced Supreme Court counsel (Paul Hughes, with the Yale Supreme Court Clinic).
- The Court recently decided a venue case (*Abouammo*, 2026) and has shown interest in venue (*Smith*, 2023); the petition asks for a GVR in the alternative, which adds a second grant route.
- The government took two extensions and filed a full opposition rather than waiving.

**Adjustments down.**
- The decision below is unpublished and per curiam, a poor vehicle.
- The split is lopsided and old, and the BIO lists a string of denials on the same question (*Renteria*, *Gonzalez*, *Iossifov*, and others). The Second Circuit's outlier rule favours defendants, so the government has not sought review of it.
- Per the BIO, the district court at sentencing found the North Carolina transactions reasonably foreseeable to petitioner (for loss calculation), and the court of appeals affirmed that finding. That gives the government a strong argument that the foreseeability question is not outcome-determinative here. The reply disputes the vehicle point, but it remains a serious obstacle.
- *Abouammo*, as the BIO describes it, restated the overt-act venue rule for conspiracy while declining to extend it, so a GVR would have little to act on. The Court seldom GVRs over the Solicitor General's opposition on such thin grounds.
- Question 2 is fact-bound error correction.
- No amicus support.

Net: about 3%, split roughly 1.6% plenary and 1.4% GVR. I set `summary-disposition-route` at 0.45 conditional on a grant.

**Other claims.** Relist increment 0.07: baseline petitions at first conference rarely relist, though a venue question could draw a Justice's interest. CVSG 0.002: the United States is a party. Dissent from denial 0.02.

**Uncertainty and discounts.** I did not independently verify *Abouammo*'s holding or date; my reading comes from the parties' competing characterisations, and the case postdates what I can confirm from memory. I did not read the petition's full split discussion. My retrieval was minimal (one corpus query that returned generic GVR priors not specific to this question), so this is essentially a base-rate forecast adjusted on the filings.
