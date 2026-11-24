# Reasoning — scotus/9026000572 (No. 26-572, Padula v. Cirrus Rojas), response-requested moment

**P(any grant) = 0.52; predicted label `gvr`.**

## What the record shows

- Snapshot `2026-11-24.json`: the Solicitor General's paid petition, filed Oct 28 2026 from a divided Seventh Circuit judgment (July 30 2026, Kolar, J.; Sykes, J., dissenting). Respondent (ACLU counsel) waived a response Nov 10; the petition was distributed Nov 17 for the Dec 4 conference; on Nov 24 the Court requested a response, due Dec 24. One distribution, no CVSG, no amicus briefs.
- The docket is paper-only (Rule 34.6). Only the government's petition was staged (from the Solicitor General's posted copy); the respondent's papers are not on my record, and no response exists yet. I do not infer what it will say.
- `petition.txt` / `questions-presented.txt`: one question — whether 8 U.S.C. 1225(b)(2)(A) mandates detention pending removal proceedings of noncitizens present without admission. The petition does **not** ask for plenary review. Its whole "Reasons" section says the Court granted certiorari on this question in *Rhoney v. Barbosa da Cunha*, No. 26-104 (Oct. 1, 2026), and asks that this petition be held and then disposed of in light of that decision.
- `decision-below.txt` matches the judgment the petition describes (No. 25-3127, 183 F.4th 909). It holds the respondent is an "applicant for admission" not "seeking admission", so section 1226 governs; constitutional avoidance is an alternative ground only. Its footnote lists the split: the Second, Seventh, Tenth and (per the petition's appendix) Eleventh Circuits and one more against the government, the Fifth and Eighth for it. `lower-court-docket.txt` shows no rehearing petition.
- Appendix C: on remand the district court granted the habeas writ (Sept 25 2026); the respondent had already been released on bond.

## Why this number

This is a hold petition, so the question is almost entirely "does the government win the lead case?" If the Court reverses or vacates in *Barbosa da Cunha*, a GVR here is close to automatic (the Seventh Circuit's holding is the statutory reading at issue). If the Court affirms, this petition is denied. So P(grant family) ≈ P(the government prevails, in whole or relevant part, in No. 26-104) plus a small Munsingwear-style or other vacatur tail, minus a small tail for dismissal or withdrawal.

My estimate that the government prevails in the lead case is a little over one half:
- For the government: the text deems every noncitizen present without admission an "applicant for admission"; *Jennings v. Rodriguez* described 1225(b)(2) as a catchall; the Court chose the government's own petition as the vehicle; two circuits and several dissenters (Judge Sykes here) agree; the current Court has sided with the government in most recent immigration-detention statutory cases.
- Against: five circuits reject the reading; nearly thirty years of contrary executive practice; the "seeking admission" language and the surplusage problem for section 1226(c), sharpened by the 2025 Laken Riley Act amendment; due-process concerns that could draw votes from the centre of the Court toward a narrower reading. A grant of the government's petition on a lopsided split also carries less signal than usual, since the Court had to take the question whichever way it leaned.

I land at 0.52. I have not read the briefs in No. 26-104, and nothing here rests on anyone else's forecast of either case.

## Anchors and adjustments

- `context.json` freezes band `federal` (sal-v9) with `cert_anchor.rate` 0.731 and the amicus-line reference 0.689 (`none` arm, n=151). The statpack's federal-band terminal mix is granted 52.5%, GVR 20.8%, denied 23.5%. I sit well below the anchor because this petition has no independent path to a grant: the government asks only for a hold, so the plenary-grant share of the federal band is unavailable to it, and what remains is conditional on a merits outcome I rate near a coin flip.
- The call for a response moves me very little. After a waiver on a government hold petition, a request for a response is routine housekeeping (the Court does not GVR against a respondent who has not been heard) and says nothing about the lead case. It may also invite the respondent to raise mootness, given the habeas grant and release; that could lead to a denial or to a vacatur, and I treat those tails as roughly offsetting.
- Corpus query (GVR priors, scotus) confirmed only the ordinary shape: GVRs issue on the cert order after one or two distributions. No prior was decisive.

## Other claims

- `relist-increment` 0.95: the petition must be redistributed once the response is in (masked at this moment anyway).
- `cvsg-increment` 0.01: the United States is the petitioner.
- `summary-disposition-route` 0.97 given a grant: a grant here is a GVR; plenary review of a held follow-on is very unlikely.
- `dissent-from-denial` 0.03 given denial: a denial would follow an affirmance in the lead case, and dissenters there would not usually write again on a held case. `order-writers` numbers are correspondingly small.

## Where to discount me

The whole forecast is one judgement about the merits of another case, made without its briefing or argument. A reader with a firm view of *Barbosa da Cunha* should substitute it. Resolution is likely not until after that decision, probably by end of June 2027.
