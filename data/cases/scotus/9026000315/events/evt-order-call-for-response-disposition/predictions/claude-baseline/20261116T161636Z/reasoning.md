# Reasoning — Goldman v. Phillips, No. 26-315 (response-requested moment)

**P(grant) = 0.20; predicted disposition: denied.**

## What I read
- Snapshot `2026-11-05.json`: paid petition from the en banc Ninth Circuit (judgment May 7, 2026), filed Sept. 4, 2026; one amicus brief (four retired bankruptcy judges and a law professor) filed Sept. 24; no response filed by the Oct. 13 due date (the docket shows no waiver entry either); distributed Oct. 28 for the Nov. 13 conference; **response requested Nov. 4, due Dec. 4**. No response is on my record and I do not guess at its content.
- `questions-presented.txt`, `petition.txt` (28 pp., not truncated) and the opening of `appendix.txt` (the en banc opinion by Judge Nguyen for an 11-judge court; my keyword scan of the appendix found no separate concurrence or dissent in the en banc decision).
- `context.json`: band `baseline` (sal-v8), `cert_anchor.rate` 0.0517, `cert_amicus_line` 0.163 (arm `some`, basis `arm`, 2,315 resolved). `same-question.json` lists no matching petition, so nothing rests on it.
- No `decision-below.txt` / `lower-court-docket.txt` was staged; I relied on the petition appendix for the opinion below.

## Anchor and adjustments
- Anchor: the baseline band's reached rate, 5.2% (frozen `cert_anchor`). The amicus-adjusted reference line is 16.3%, which I treat as probably running high for a baseline-band petition (as the prompt cautions), but this petition does already have its brief at an early stage.
- Up for the call for a response. No committed table conditions on it; my own judgement is that a called-for response on a paid, counselled petition roughly doubles to triples the unconditional rate, because it shows at least one chambers thought the petition could not be denied on the petition alone. Most such petitions are still denied.
- Up for the petition's quality on the traditional criteria: (i) the decision below is an en banc court of appeals decision taken up sua sponte; (ii) the petition documents a long-acknowledged conflict (negligence: CA1, CA2, CA9, CA11; willful and deliberate: CA4, CA6, CA7, CA10; gross negligence: CA5), with courts and treatises calling it a circuit split; (iii) the question is purely legal and outcome-determinative, because respondents stood on a complaint pleading only ordinary negligence; (iv) experienced Supreme Court counsel (Daniel Geyser), and a cert-stage amicus brief from retired bankruptcy judges; (v) the Ninth Circuit stayed its mandate. The Court regularly takes one to three bankruptcy cases a Term.
- Down: (i) the split is decades old (its roots are in differing readings of *Mosser v. Darrow* from the late 1970s and 1980s) and the Court has let it sit, which suggests either low practical stakes or that several of the "willful and deliberate" statements are loose or dicta — I have not verified the split's depth independently and the response will surely attack it; (ii) the posture is interlocutory (reversal of a dismissal, remand), and the Ninth Circuit's opinion is framed around immunity doctrines (quasi-judicial and derived immunity) plus a business-judgment defense, so the response can argue the QP ("whether ... and if so, under what standard") is broader or differently framed than what was decided, and that the trustee may yet prevail on remand; (iii) the QP as written is two-part and somewhat open-ended; (iv) respondents were unrepresented by Supreme Court specialists and filed nothing, which cuts both ways.
- Net: about 0.20. I considered a range of 0.12–0.30. A CVSG is a live alternative path (the United States Trustee Program supervises Chapter 7 trustees, so the government has a real interest), which would itself raise the grant odds later; I put it at about 0.12.

## Other claims
- `relist-increment` 0.97: the petition must be redistributed once the response is in (the harness masks this claim at this moment).
- `cvsg-increment` 0.12: see above.
- `summary-disposition-route` 0.05 (conditional on a grant): no intervening decision is pending that I know of; a grant here would be plenary.
- `dissent-from-denial` 0.03 and `order-writers`: bankruptcy cert denials very rarely draw a writing; small numbers per Justice, consistent with the 0.03.

## Retrieval and limits
One corpus query (generic granted SCOTUS priors, 2020s) returned nothing specific to this question; the structured filters cannot search by subject for SCOTUS rows. I used the committed statpack for the band table, relist cut (relist-1 bucket: 8.3% granted + 5.2% GVR, n=2,539 resolved) and amicus cut (1 brief: 10.1% granted + 4.7% GVR, n=1,163) as cross-checks. I did not consult the live docket, the web or the CourtListener MCP. Discount me most on the true depth of the split, which I took from one side's petition.
