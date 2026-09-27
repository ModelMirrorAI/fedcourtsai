# Rationale for the numbers

**P(unqualified grant) = 0.35; `predicted_disposition` = denied.**

## What I read

- **Provisioned baseline.** `record/snapshots/2026-09-17.json`: docket 26A370, one proceedings entry, "Application (26A370) for a stay, submitted to Justice Kagan" (Sept 16, 2026). Lower court CA9 Nos. 26-1746, 26-5060. Applicants Ryan Thornell et al. (Arizona DCRR), counsel of record Paul D. Clement; respondents Shawn Jensen et al., counsel of record Donald Specter (Prison Law Office). Not a capital case.
- **`record/context.json`.** Mode `forward`, `cut_kind` `arrival-position` at anchor index 0, cutoff 2026-09-17, `band: null`, `response_requested: false`, `referred_to_court: false`, `amicus_briefs: 0`, `term: 2026`. Band is null, as an interim cell's should be; I did not derive one and did not use the cert band table or the caption-class floors.
- **`record/documents/application.txt`.** The State's 189-page stay application, text extracted, `truncated: true` (the appendix beyond the Ninth Circuit order is cut; I read the full argument and the Ninth Circuit's Sept 1 order). The application seeks a stay of the Feb 19, 2026 receivership order and the July 17, 2026 appointment order, effective Oct 19, 2026, pending the expedited Ninth Circuit appeal (argument December 2026) and any cert petition. Its merits theory is PLRA least-intrusive-means / receivership-as-last-resort (no post-2023 contempt cycle, progress ignored, receiver given five years vs. the State's three), with a *Trump v. CASA* founding-era-antecedent argument it expressly says the Court need not resolve.
- **Retrieved in forward mode (see `retrieval.md`).** The live supremecourt.gov docket for 26A370 shows two entries after my baseline: Justice Kagan requested a response on Sept 18 (due Sept 25) and the respondents filed their opposition on Sept 25. No amicus entry, no referral entry, no disposition. I read the 48-page opposition. Its main points: no certworthy question (fact-bound abuse-of-discretion review, no split, *Brown v. Plata* names receivers as an available remedy); the *CASA* argument is forfeited and disclaimed; the district court did try contempt twice (about $2.2 million in fines) and found no sanction "robust enough to coerce compliance"; the State was noncompliant with 131 of 154 quality indicators after three years; preventable deaths documented by court experts; the appeal is expedited and the motions panel invited the merits panel to revisit the stay; the transfer of authority is reversible and the cost claim is unquantified. The two sibling event definitions in this case directory (`evt-order-response-requested-disposition`, opened 2026-09-18; `evt-brief-response-disposition`, opened 2026-09-25) corroborate those two entries.

## Anchor

The statpack's "The interim docket (applications)" section carries the scored base rate. Pooling the substantive resolved slice over application-Terms strictly before 2026 and within ten Terms: Term 2025 (17 granted / 226 resolved) plus Term 2024 (14 / 70) gives **31 / 296 = 10.5%**, which clears the pre-registered floor of 50. Terms 2023 and earlier are wholly unparsed and contribute nothing; Term 2024 is only partly parsed (972 of 1,297 rows unparsed) and its 20.0% rate is far from the 2025 rate of 7.5%, so the pool leans on one well-covered Term and one thin one. The section's caption already calls the rate the scored base rate (not descriptive-only). That 10.5% is the yardstick this cell is scored against.

## Adjustments

Up, substantially, from 10.5%:

- **Escalation ladder.** A response has been requested (and filed). In the pack the response-requested count is small relative to the substantive slice (64 of 367 applications) while grants number 37, and a substantive application the Court grants essentially always has a response on file. Reading the section's shape rather than a conditioned cut, P(grant | response requested) in this population is plausibly in the 35–50% range, several times the unconditioned rate. The prompt's caution applies: those columns are right-censored and not as-at-prediction, so I treat this as shape, not a lookup.
- **Applicant class.** A sovereign State with elite Supreme Court counsel, a 2–1 split below with a dissent proposing an intermediate remedy, and a framing (private receiver displacing a Governor-appointed director; power to seek waivers of state statutes) that maps onto the current majority's recent willingness to stay orders it sees as intruding on a sovereign's internal operations. The State also cites a summer-2026 per curiam (*Trump v. California*) on that point which I cannot independently verify from my own knowledge.

Down, from the ladder-conditioned range:

- **Certworthiness is weak.** The remedy is discretionary and record-bound; *Brown v. Plata* names receivers as available; there is no split; and the one novel legal question (*CASA* and receiverships over state agencies) is disclaimed by the applicant and apparently unpreserved. Several Justices treat certworthiness as a threshold on this docket.
- **Posture.** The appeal is expedited with argument in December, the motions panel left the stay open to the merits panel, and the in-chambers tradition treats a stay of a matter pending in the court of appeals as rarely granted.
- **Equities.** The respondents' record of preventable deaths and 85% noncompliance is the kind of showing that makes a majority reluctant to freeze a remedy for a few months of appellate process, and the State's irreparable-harm theory is the transfer of authority itself.
- **Resolver collapse.** The claim is P(unqualified grant). A partial stay (for example, staying only the state-law-waiver provisions) or an administrative stay followed by a denial reads as `denied`, and partial relief is a live shape here given Judge Forrest's proposal.

Net: **0.35**. I would have said roughly 0.30 on the baseline alone (State applicant, Clement, but no response yet visible); knowing a response was requested within two days moves me up modestly, since that is close to automatic for this applicant class rather than a discriminating signal.

## The three increment claims

- `response-requested-increment` **0.99.** The rung has already fired on the live docket (Sept 18). The harness will resolve this claim as vacuous for my cell because my frozen context shows `response_requested: false`; I state the probability I actually hold.
- `referral-increment` **0.85.** Referral is revealed in the disposing order's text. For a State applicant with a response on file and stakes of this size, a single-Justice disposition in either direction would be unusual. The residual 15% covers a Circuit Justice denial "without prejudice" or an in-chambers order.
- `amicus-increment` **0.40.** The Arizona legislative leaders filed as amici in the Ninth Circuit and are the natural filers here; a multistate coalition is possible. Against that, none has appeared in eleven days and the response has already been filed, which is late for application-stage amici. Count rule: any entry reciting amicus/amici curiae, plus submitted briefs by distinct lead filers.

## Big-case score

0.55. Real federalism and prison-reform significance (a State's whole prison healthcare system under a receiver), watched by state AGs and civil-rights litigators, but tied to one State's record and unlikely to be front-page news outside Arizona.

## Uncertainties and where to discount me

- My knowledge of the Court's 2026 emergency-docket behavior is incomplete past mid-2026; the application cites *Trump v. California* (Aug. 24, 2026) and *Trump v. Cook* (2026), which I could not check and took at the applicant's characterization.
- I have not seen the applicants' reply, which had not been filed at retrieval time.
- The corpus prior pool rests on two Terms of very uneven coverage; the 10.5% anchor is a floor-clearing but fragile number.
- Justice Kagan is the Circuit Justice; how quickly and in what form she refers or acts is the main driver of the increment claims and I have no case-specific signal for it.
- The pooled corpus retrieval (`fedcourts query --include-applications`) surfaced this month's application dispositions but no close analogue (a State seeking a stay of a PLRA structural remedy), so the case-specific adjustment is judgment, not a matched-prior estimate.
