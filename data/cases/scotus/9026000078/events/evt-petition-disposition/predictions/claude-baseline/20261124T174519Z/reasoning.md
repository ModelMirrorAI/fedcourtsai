# Reasoning — scotus/9026000078 (Hunt v. Florida, No. 26-78), evt-petition-disposition

**Number: P(any grant) = 0.17; label: denied.**

## Inputs read
Snapshot `2026-11-24.json` (forward mode, no cutoff); `questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt`, `cert-reply.txt` (appendix skimmed only through the petition's description of it); `record/related/26-76.json` (Jackson v. Florida, relation `vided-amicus`, one shared brief — and on reading it plainly a true companion: same counsel, same Florida Supreme Court decision day, petitions cross-reference each other); `same-question.json` (lists only 26-76, pending). Context: band `elevated` (sal-v9), `distribution_count` 2, `cert_anchor.rate` 0.248, `cert_amicus_line.rate` 0.397 (arm `some`).

## Anchor and adjustments
- Anchor: elevated-band reached rate 0.248. The amicus-line reference is 0.397.
- I discount both. The band was reached through a *reschedule*, not a true relist: the petition was distributed for 12/4, rescheduled the same day, and re-distributed for 12/11. No conference has sat. The statpack itself warns that the distribution count is an upper bound on relists. Reschedules carry some signal of chambers' attention (and Jackson has now been rescheduled twice), but part of it here is plainly logistical — Jackson was pulled from the 9/28 conference so it could travel with Hunt once Florida's thrice-extended BIO came in. The single amicus brief is a brief filed in Jackson and "VIDED" onto this docket; it addresses the Jackson question.
- For the petition: Jeffrey Fisher / Stanford clinic as counsel; capital case; Florida's 8-4 rule is the least demanding in the country; the 10-2 vote makes the change outcome-determinative, so the vehicle on QP 2 is clean; the Court granted Kian v. Florida (No. 25-6623, six-person juries, granted 15 June 2026 after five distributions per the corpus row), which shows at least four Justices willing to revisit Florida jury rules; Justice Gorsuch (Ramos, Erlinger) plus the three Democratic appointees is a conceivable cert coalition.
- Against: the split on QP 2 is thin by the petition's own admission (an 1899 Louisiana decision under an abandoned test, an Oregon legislative choice, and two parole-board cases); Collins v. Youngblood overruled Thompson v. Utah on the Ex Post Facto treatment of jury-size changes and Dobbert is close on its facts; Peugh was 5-4 with four current-majority Justices' predecessors/selves in dissent. On QP 1, McKinney v. Arizona and Kansas v. Carr (weighing/mercy need not be a jury fact-finding) make it hard to count a fifth vote for reversal, which matters to a defensive-denial calculus by the liberal Justices; the Court has repeatedly denied Florida post-Poole petitions. Only Florida is affected on QP 2.
- Structure: P(Jackson granted) ≈ 0.2. Given that, Hunt is granted outright (~45%) or held and later GVR'd/denied (hold then GVR ≈ half of the rest). Hunt alone without Jackson ≈ 0.02. That lands near 0.17.

## Other claims
- relist-increment 0.55: one more distribution or reschedule after the 12/11 listing; any serious look (grant or a dissent from denial) entails it, and reschedules have recurred on both dockets.
- cvsg-increment 0.01: no federal interest.
- summary-disposition-route 0.25 (conditional on grant): the hold-then-GVR path.
- dissent-from-denial 0.25 (conditional on denial): Sotomayor has written on Florida capital sentencing repeatedly; but a writing may sit on Jackson's order rather than Hunt's. `order-writers` is kept consistent (Sotomayor 0.17 dominant).

## Uncertainty / where to discount me
- I did not read Jackson's petition or BIO text (not provisioned); my view of QP 1's strength is from the Hunt filings' summaries and general knowledge.
- I cannot tell why the 12/4 listing was rescheduled; if it reflects a chambers' request rather than calendaring, my number is low.
- Kian's pendency could lead to a long hold of both petitions; I treat that as not materially changing the eventual disposition odds.
- No outcome for this petition surfaced; no one else's forecast was seen.
