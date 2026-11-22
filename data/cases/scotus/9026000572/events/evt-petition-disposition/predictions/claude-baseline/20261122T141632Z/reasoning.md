# Reasoning: P(grant) = 0.62, predicted disposition GVR

## What I read

- Snapshot `2026-11-22.json`: petition filed October 28, 2026 by the Solicitor General; response waived November 10; distributed once, for the December 4, 2026 conference. Paper-only docket (Rule 34.6), so only the government's petition was staged; the respondent filed nothing but a waiver.
- `record/documents/petition.txt` and `questions-presented.txt`: the petition's whole "reasons for granting" section is a request to hold for *Rhoney v. Barbosa da Cunha*, No. 26-104 (cert. granted October 1, 2026), and then dispose "as appropriate."
- The Seventh Circuit opinion in the petition appendix (2–1, Judge Kolar for the court, Judge Sykes dissenting): section 1225(b)(2)(A) does not reach a noncitizen arrested in the interior who is not "seeking admission"; the case is not moot despite his release on bond.
- `context.json`: band `federal`, `cert_anchor.rate` 0.731, amicus line (`none` arm) 0.689, `distribution_count` 1.
- `same-question.json` has `petitions: null`, so I got nothing from it. `lower-court-docket.txt` shows no en banc petition.

## How I got the number

This is a hold petition, so the forecast reduces to one question: does the government win enough in *Barbosa da Cunha* to earn a GVR here? A corpus lookup confirmed the lead docket (26-104) is granted, and that the two sibling petitions on the same question (25-1415 from the Sixth Circuit, 26-43 from the Fifth) are still pending after a single September distribution. That is the held pattern I expect here.

I put the government's chance of prevailing in the lead case at roughly 0.58:

- **For the government:** it is the petitioner in a granted case, and granted cases are reversed more often than not. It has won every recent statutory immigration-detention case I can recall (*Jennings*, *Preap*, *Guzman Chavez*, *Arteaga-Martinez*). *Jennings* called 1225(b)(2) a catchall for applicants for admission. The Fifth and Eighth Circuits and dissenters in the Sixth, Seventh and Eleventh adopt its reading.
- **Against:** most circuits to decide the question (the Second, Sixth, Seventh, Tenth and Eleventh, per the opinion below) rejected the government's reading. The "seeking admission" text, the surplusage argument, roughly three decades of contrary agency practice and constitutional avoidance all cut the other way. This Court has ruled against the government on textual immigration questions before (*Pereira*, *Niz-Chavez*).

I add a few points for other routes to a grant: a partial government win or a remand-style opinion that still warrants a GVR, and a Munsingwear vacatur if the respondent's case moots first. That gives 0.62.

This is below the federal-band anchor of 0.731. The anchor pools all Solicitor General petitions, including ones the SG hand-picked as plenary vehicles. This one's fate is tied to a single contested merits case that I see as only modestly favouring the government.

## Other claims

- `summary-disposition-route` 0.97: any grant here is almost certainly a GVR, since the lead case is already set for argument.
- `relist-increment` 0.10: held petitions usually show no further distribution entry before the post-decision order. I am not certain of the docketing practice, so I left some room.
- `cvsg-increment` 0.005: the United States is the petitioner.
- `dissent-from-denial` 0.02 and low `order-writers` figures: denial of a held follow-on petition almost never draws a writing.

## Where to discount me

- The merits estimate for the lead case is my judgement, not a base rate. I did not read the merits briefs in 26-104.
- The split tally comes from the Seventh Circuit opinion's citations, not a full survey.
- Resolution is probably seven months away. Mootness or a change in government position could intervene.
- A web search confirmed the grant in 26-104 and reported that argument is expected in late February or early March 2027 (from the respondent's counsel's case page; no calendar entry confirmed it). I saw no forecast of either case.
