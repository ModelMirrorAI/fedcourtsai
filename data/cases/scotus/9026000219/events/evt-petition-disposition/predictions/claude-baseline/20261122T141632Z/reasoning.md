# Reasoning — scotus/9026000219 (No. 26-219, Johnson v. United States), evt-petition-disposition

**P(grant) = 0.04; call: denied.**

## What I read
- Snapshot `2026-11-22.json`: paid petition from the Court of Appeals for the Armed Forces (CAAF, judgment May 26, 2026), filed Aug 17, 2026. The United States waived its response (Aug 31); the petition was distributed for the Sept 28 conference (one distribution); the Court then **requested a response** (Sept 14, due Oct 14). The Solicitor General has taken two extensions, the response now being due Dec 7, 2026. No amicus briefs, no CVSG, no relist beyond the first distribution.
- `petition.txt` and `questions-presented.txt` (full text), and the CAAF opinion at the front of `appendix.txt`. No brief in opposition exists yet, so the government's side is unknown to me; I did not infer its content.
- `same-question.json` lists no matching petitions; no `related/` directory.
- `context.json`: band `baseline` (sal-v8), `cert_anchor.rate` 0.0518, amicus-line reference 0.027 (arm `none`).

## Anchor and adjustments
- Anchor: the frozen baseline-band reached rate, 5.2%. The statpack's relist-count cut (relist 0: 1.8% grant family, n=10311; relist 1: 13.6%, n=2546) and the no-amicus bucket (3.7%, n=11215) frame the range.
- **Up:** the Court called for a response after a waiver, so at least one Justice wanted to hear from the government. That takes the petition out of the dead-list mass that dominates the baseline band. The CAAF decision drew a dissent by Chief Judge Ohlson calling the search a "blatantly unconstitutional fishing expedition," and the facts (an eight-month, near-total search of two phones authorized by a commander with no prior experience, advised by the same prosecutor who helped draft the request) are sympathetic. My general understanding is that petitions with a called-for response are granted at a rate several times the paid average, but no committed table conditions on it, so this is judgement, not a quoted rate.
- **Down, and more heavily:** (1) The petition alleges no conflict among courts; it argues that military practice departs from *Leon*, which is an error-correction or systemic-critique pitch. (2) The question presented as framed — whether good faith can ever apply to an authorization by a legally untrained commander advised by the prosecution's lawyer — is broader than the issue CAAF granted and decided (whether possession of two phones could support the search; CAAF assumed no probable cause and applied the good-faith rule in Mil. R. Evid. 311(c)(3)). The government will very likely argue the categorical challenge was not pressed or passed on below, a serious vehicle objection. (3) Commander search authorizations are a long-settled feature of military practice codified in Mil. R. Evid. 315, and the Court takes CAAF cases rarely. (4) The petition is short (about 13 pages of body) with no amicus support and no specialist Supreme Court counsel. (5) The remaining dispute is largely fact-bound application of the good-faith standard.
- Net: slightly below the anchor, 0.04. The call for a response keeps me from going to the 1–2% a waived, undistributed-again petition of this kind would deserve.

## Other claims
- `relist-increment` 0.96: one distribution on the record (Sept 28 conference); the petition must be distributed again once the response arrives. The residual is a withdrawal/dismissal before redistribution.
- `cvsg-increment` 0.003: the United States is the respondent, so there is nobody to invite.
- `summary-disposition-route` 0.30 (given a grant): a grant here would most plausibly come either as plenary review of the military good-faith question or as a GVR if the Solicitor General concedes some error or an intervening decision lands; the two long extensions are weak evidence at most of internal deliberation, common for the SG's office.
- `dissent-from-denial` 0.07 (given a denial): the requested response and the strong dissent below make a statement or dissent more likely than usual, with Sotomayor, Gorsuch and Jackson the likeliest authors; still uncommon in absolute terms. The `order-writers` numbers are consistent with this.

## Uncertainty and discounts
- I have not seen the government's response; a confession of error or an acknowledgment of a recurring problem would move this up materially, and a strong preservation objection would move it down.
- I did not verify the petition's characterization of the record beyond the CAAF opinion in the appendix.
- Retrieval was limited to the committed statpack and one corpus query (generic granted priors, not informative for this case). No web or CourtListener lookups were made.
