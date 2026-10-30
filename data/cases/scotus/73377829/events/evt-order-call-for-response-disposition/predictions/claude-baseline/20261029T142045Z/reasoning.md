# Why P(grant) = 0.05

**Inputs.** I read the snapshot `2026-06-16.json`. It shows the petition filed May 18, 2026, the federal respondents' waiver on June 2, distribution on June 9 for the June 25 conference, and "Response Requested" on June 15. I also read the provisioned `questions-presented.txt` and the petition (`petition.txt`, 388 pages, truncated at the cap). From `context.json`: band `baseline` (sal-v4), distribution_count 1, no CVSG, term 2025, forward mode.

**Anchor.** I used the sal-v4 "Segment base rate by salience band" table, `baseline` column, bracketed `reached` rate, pooled over Terms strictly before 2025 (OT2017–OT2024). Those rates fall between 4.5% and 5.9%, with n of roughly 1,200 to 1,750 per Term, so the pool is about 5.3%. The caption is a private petitioner against federal officers, so `baseline` is also the right class floor.

**Adjustments.**
- *Up:* The call for a response is the main signal. A Justice wanted the SG on record. Amici (Georgia Association for Women Lawyers and the Legal Accountability Project) appear on the docket. Counsel is a law-school Supreme Court clinic. The subject, how the judiciary handles its own employees' harassment claims, has institutional salience.
- *Down:* The petition points to no circuit split. The judgment below follows a bench trial, where the district court found that Strickland received the process due under the EDR Plan despite acknowledged flaws, so the record is fact-bound. The respondents are the judiciary's own administrators, which makes the Court an awkward forum and could raise recusal questions. QP 2 rests on a Judicial Conference policy whose enforceability is doubtful. Calls for a response are a low bar, and most such petitions are still denied.

On balance, the call roughly offsets the vehicle problems, and I land near the anchor at 0.05.

**Forward retrieval.** This is a forward cell, so I read the live supremecourt.gov docket. After my snapshot, the Solicitor General obtained three extensions and filed a brief in opposition on October 13, 2026. An amicus motion was filed July 15, the petitioner's reply was submitted October 26, and the petition was distributed for the November 13, 2026 conference. No disposition has issued. The opposition is what I expected, and the docket shows no relist yet, so I did not move the number. I did not read the BIO's text.

**Other claims.** `cvsg-increment` is near zero because the United States is a party. `summary-disposition-route` is 0.10 conditional on a grant, since no intervening decision would support a GVR. `dissent-from-denial` is 0.12 because the subject invites a statement, for example from Justice Jackson or Justice Sotomayor. The `order-writers` numbers are consistent with that figure.

**Uncertainty.** I would revise the most if the November 13 conference produces a relist, which would signal that a Justice is writing or that the Court is considering a grant. I also did not read the full petition. It was cut at the cap, and I skimmed the statement of the case and the reasons for granting.
