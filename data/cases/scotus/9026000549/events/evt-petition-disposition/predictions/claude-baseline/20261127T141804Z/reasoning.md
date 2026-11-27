# Reasoning — scotus/9026000549 (No. 26-549, Allyn-Feuer v. Doe), evt-petition-disposition

**P(grant) = 0.05; call: denied.**

## What I read
- Snapshot `2026-11-27.json`: paid petition filed Oct 19 2026 from the Fifth Circuit (No. 25-40204, judgment May 8 2026, rehearing denied June 22 2026); the United States **waived** its response on Nov 19; distributed once, for the Dec 11 2026 conference. No amicus briefs, no CVSG, no call for a response.
- `questions-presented.txt` and `petition.txt` (with the appendix bound in). No brief in opposition exists (waiver), so I have only the petitioner's side plus the opinion below in the appendix.
- `lower-court-docket.txt` records no opinion on CourtListener and no en banc read; I relied on the petition appendix instead, which shows an unpublished per curiam (Stewart, Graves, Oldham; Oldham concurring only in the judgment) and a denial of rehearing en banc.
- `context.json`: mode `forward`, band `baseline` (sal-v9), `distribution_count` 1, `cert_anchor.rate` 0.0518, `cert_amicus_line` (arm `none`) 0.0269.

## Anchor and adjustments
- Anchor: the frozen baseline-band reached rate, 5.2%. The no-amicus arm is 2.7%. The statpack relist cut shows petitions ending with no relist are granted (grant family) about 1.8% of the time (n=10,311 resolved).
- **Down:** the respondent waived and the Court has not (yet) called for a response; a petition almost never is granted without a response, so a grant requires first a call for response and then a second conference. The decision below is unpublished. The asserted split is thin: one 1994 Ninth Circuit decision (Gasho), in which the point was apparently conceded by the government and which the Fifth Circuit's own precedent (Jeanmarie) described as consistent with its rule. A 1–1 split of that vintage, with the Solicitor General likely to argue the cases are reconcilable, is usually not enough. No amici.
- **Up:** the petition is professionally done (UVA Supreme Court Litigation Clinic); the question is purely legal, decided on the pleadings, and outcome-determinative; the panel itself called the consequence "troubling," and one judge concurred only in the judgment; the Court has shown recent interest in FTCA law-enforcement-proviso questions (Martin v. United States, 2025) and took Ali from an unpublished opinion; Egbert leaves no Bivens alternative. These make a call for response reasonably plausible (I put it near one in three), and a grant conditional on a called-for response perhaps 12–15%.
- Net: roughly 0.33 × 0.14 ≈ 0.05, which lands on the band anchor. I am not claiming an edge over the anchor in either direction; the waiver posture and the petition's quality roughly offset.

## Other claims
- `relist-increment` 0.33: a further distribution happens essentially only if a response is called for (the petition is then redistributed) or the Court relists; otherwise it is denied on the Dec 14 order list.
- `cvsg-increment` 0.01: the United States is the respondent, so its views would come through a called-for response, not a CVSG.
- `summary-disposition-route` 0.12 (conditional on grant): no pending case I know of would prompt a GVR; a small chance of a summary action or a GVR on an SG confession-of-error.
- `dissent-from-denial` 0.04 (conditional on denial): slightly above the usual rate because the consequence is one some Justices (Sotomayor, Gorsuch, Jackson) have written about, but separate writings on first-conference denials after a waiver are rare. `order-writers` is consistent with that.

## Uncertainty / discounts
- I did not verify the petition's characterization of Gasho or the Fifth Circuit precedents against the opinions themselves, nor look for other circuits' decisions on § 2680(c) and persons-vs-property claims; a deeper split than the petition claims is unlikely (petitioner would have cited it), a shallower one is possible.
- Corpus query used only for a generic look at recent grants; it did not inform the number. No CourtListener MCP or web retrieval was made.
