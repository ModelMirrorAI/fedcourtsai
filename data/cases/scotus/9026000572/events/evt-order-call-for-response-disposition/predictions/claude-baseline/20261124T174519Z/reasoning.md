# Reasoning for my numbers

**P(grant family) = 0.60; label `gvr`.**

## What I read

- The snapshot `2026-11-24.json`: petition filed October 28, 2026 by the Solicitor General; respondent (ACLU counsel) waived on November 10; distributed November 17 for the December 4 conference; response requested November 24, due December 24, 2026.
- `petition.txt` (government's copy from the Solicitor General's site; the docket is paper-only under Rule 34.6, so only the government's filing was staged). The petition is twelve pages and asks only that the Court hold it for *Rhoney v. Barbosa da Cunha*, No. 26-104, cert. granted October 1, 2026, which presents the identical question: whether 8 U.S.C. 1225(b)(2)(A) mandates detention of aliens present without admission.
- `decision-below.txt` and `lower-court-docket.txt`: a published, divided Seventh Circuit opinion (Judge Kolar for the majority, Judge Sykes dissenting) holding that the respondent is not "seeking admission", so Section 1226(a) and its bond hearings govern. The opinion matches the judgment the petition describes (No. 25-3127, July 30, 2026). No en banc petition was filed.
- `same-question.json` has `petitions: null`, so I rest nothing on it.
- The corpus row for No. 26-104 confirms `date_cert_granted: 2026-10-01`, originating court ca2. A web search confirmed the grant and the same question presented, and reported that argument is expected in late February or early March 2027.

## Anchor and adjustment

- The frozen anchor is `cert_anchor.rate` = 0.731 for the `federal` band; the amicus line for the `none` arm is 0.689 (n = 151). The statpack table on disk is headed sal-v8 while my context is sal-v9, so I used the frozen anchor, not the table (flagged, info).
- I move down from 0.73 to 0.60 because this petition's fate is not a generic federal-petitioner draw. It is tied almost one-for-one to the merits outcome of *Rhoney*: GVR if the government wins or the Court's reasoning disturbs the Seventh Circuit's, denial if the government loses. So my number is essentially my estimate that the government prevails in *Rhoney*, plus a little for mootness vacatur and for a partial or narrower ruling that still warrants a remand.
- Why about 0.55–0.60 for the government in *Rhoney*: the Court took the government's own petition; the Court's recent immigration-detention cases (*Jennings*, *Preap*, *Guzman Chavez*, *Arteaga-Martinez*) read these statutes textually and for the government; *Jennings* called Section 1225(b)(2) a catchall for applicants for admission; and two circuits and several dissenting judges, including Judge Sykes here, accept the government's reading. Against that: most circuits to decide the question have rejected the government's reading, it departs from nearly three decades of agency practice, it would leave little work for Section 1226(c) and the 2025 Laken Riley Act amendment, and the constitutional-avoidance argument could attract textualist votes. I see it as a modest government lean, not a strong one.
- The response request itself moves me very little. No committed table conditions on it. Here it has a plain procedural reading: the Court does not ordinarily grant, including by GVR, without a response on file, and the respondent had waived. The call is consistent with the Court preparing to hold the petition and keeping a GVR available. It says the petition will not be denied outright now, which was already near-certain given the pending lead case.

## Other claims

- `relist-increment` 0.97: one distribution on the record, and the petition must be redistributed after the response.
- `cvsg-increment` 0.01: the United States is the petitioner.
- `summary-disposition-route` 0.97 (conditional on a grant): a hold petition resolves in the cert order.
- `dissent-from-denial` 0.03 (conditional on denial) and low `order-writers` figures: writings on a post-decision hold disposition are rare.
- `big_case_score` 0.4: the legal question is major, but this docket is a follower.

## Where to discount me

- My number is a merits forecast of a case that has not been argued, formed without reading the *Rhoney* briefs. That is the main uncertainty.
- I did not see the respondent's side (paper-only), and the response is not yet filed. The appendix shows a district-court habeas grant on remand (September 25, 2026); the petition text I was given is cut around parts of the appendix, so I cannot assess mootness risk in detail.
- The label `gvr` is scored correct only on a GVR outcome; a plenary grant or consolidation would make it wrong, but I think that is under 2%.
