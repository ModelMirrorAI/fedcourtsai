# Reasoning: P(grant) = 0.03

**Inputs read.** Snapshot `2026-11-15.json`; `context.json` (forward mode, band `baseline`, sal-v8, one distribution, no CVSG, 0 amicus briefs); `questions-presented.txt`; the opening of `petition.txt` (truncated at the cap; I read the QP and introduction, not the whole brief); `decision-below.txt` (matches the judgment the petition describes: D.C. Cir. No. 24-5243, June 2, 2026, unpublished judgment, Pillard/Wilkins/Katsas); `lower-court-docket.txt` (no rehearing petition found). No brief in opposition exists — the government waived.

**Anchors.** `cert_anchor.rate` for the baseline band is 5.2% (reached basis); the amicus-line `none` arm is 2.7%. The statpack relist cut shows petitions ending with no relist at about 1.8% grant-family. I sit between the amicus line and the anchor, at 3%.

**Why below the band anchor.**
- The Solicitor General waived a response and the petition was distributed on the waiver. The Court does not grant without a response, so the petition is denied at the Dec. 4 conference unless a Justice first calls for one. The baseline `reached` population includes petitions that drew a BIO or a called-for response; this one so far has neither.
- The decision below is an unpublished, non-precedential judgment. The preservation holding is one paragraph applying settled circuit law (Ponce).
- Vehicle problems the government would raise: the plaintiff is a federal employee, so the governing text is § 2000e-16(a), not § 2000e-2(a)/(m) on which the alleged split rests; the theory was not raised in the district court by a pro se plaintiff, and the panel declined to excuse the forfeiture on "this record"; the panel also found no evidence of pretext. The petition's own QP concedes "other circuits have issued conflicting opinions," i.e., a messy rather than square split.
- No amicus support.

**Why not lower.**
- Counsel of record is an experienced Supreme Court advocate at a top appellate practice, taking a formerly pro se case — a signal that specialists saw a real split (CA9/CA2 v. CADC/CA11) on a recurring question. Such petitions draw calls for a response at a meaningful rate; I estimate about 25%.
- Conditional on a called-for response, I put the grant chance near 10–12% (the Court has shown some interest in Title VII causation/McDonnell Douglas questions, but the vehicle is weak). 0.25 × ~0.11 ≈ 0.03.

**Other claims.** `relist-increment` 0.25 is essentially the call-for-response probability (redistribution after a response counts) plus a small reschedule chance. `cvsg-increment` near zero because the United States is a party. `summary-disposition-route` 0.2 conditional on grant: mostly a confession-of-error GVR scenario. `dissent-from-denial` 0.02; `order-writers` kept consistent with that.

**Uncertainty / discounts.** I did not read the petition's full split analysis, so my view of the split's depth rests on the QP and the panel's opinion. The call-for-response rate for this counsel class is my judgement; no committed table conditions on a waiver. I did not check the Court's live docket after the snapshot (creation date Nov. 13), so a response request issued since would not be reflected. The one `fedcourts query` I ran returned generic recent grants and did not shape the number. I have no knowledge of this case's outcome.
