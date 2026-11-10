# Reasoning — GEO Group v. Ferguson, No. 26-71 (relist moment)

**P(any grant, GVR included) = 0.55.**

## Inputs read
- Snapshot `record/snapshots/2026-11-09.json`. It shows a reply-triggered distribution for 10/16, a "Rescheduled" entry on Oct 6, a distribution for the 11/6 conference, and a distribution on Nov 9 for 11/13. That last one is a true relist after a conference sat on the case. `context.json` gives `distribution_count` 3 and `band` "high" under sal-v8, with `cert_anchor.rate` 0.348 (pooled reached rate over 10 prior Terms).
- QP, petition, BIO and cert reply (`record/documents/`). The decision below is the published CA9 opinion by W. Fletcher, J., in No. 24-2815, which matches the petition. The lower-court docket shows rehearing en banc denied on 2026-02-11 with a dissent noted. The reply says eight judges dissented.
- `same-question.json` has an empty list. The companion case is named in both briefs instead.

## Anchor and adjustments
- The anchor is the high band's reached rate, 0.35. As a cross-check, the statpack relist cut (paid segment) has a grant family of about 41% at bucket 2 (n=495 resolved) and about 37% at 3+ (n=483). Both buckets count the pre-conference reschedule as a relist, so they read low for a petition the Court truly relisted.
- **The companion case is the decisive factor.** I read GEO Group v. Nwauzor, No. 25-828, on the Court's live docket (supremecourt.gov). It has the same petitioner, the same counsel (Clement), the same facility and the same doctrines (intergovernmental immunity and the reduced protection the Ninth Circuit gives contractors). The Court called for the SG's views on 2026-05-18. The United States filed on 2026-09-15 and, per the cert reply, urged a grant and cited this case twice as a logical companion. Nwauzor was distributed for 11/6 and relisted for 11/13 on exactly the same days as this petition. This petition's Oct 6 reschedule moved it into lockstep with Nwauzor. That strongly suggests the Court is weighing the two together. A Nwauzor grant looks likely given a CVSG plus an SG recommendation to grant.
- **Ways this petition can count as "granted":** (a) a grant alongside Nwauzor; or (b) a hold for Nwauzor followed by a GVR if GEO wins there. Given this Court's intergovernmental-immunity precedent (United States v. Washington, 2022), a GEO win is plausible.
- **Points against:** the posture is interlocutory (a vacated preliminary injunction, with the discrimination claim remanded). The BIO notes that a second PI appeal under a new ICE contract is pending in CA9. The Court could take only Nwauzor and deny this one outright. It could also hold this case and then deny it even after a GEO win, because the remand already moots part of the case. The BIO's vehicle argument has real force.
- Net: I move from 0.35 up to 0.55. Most of the grant mass is an outright grant now. A meaningful share is a hold followed by a GVR, which is why `summary-disposition-route` is 0.40.

## Uncertainty
I have not read the SG's Nwauzor brief or the Sept 29 supplemental briefs myself. Their content comes from the cert reply's characterization. The supplemental briefs reportedly address ICE's revised $1/day standards, which might give the Court a vehicle concern in Nwauzor. If Nwauzor is denied, this petition probably falls with it. I did not use the CourtListener MCP.
