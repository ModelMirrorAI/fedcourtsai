# Reasoning — scotus/9026000103 (No. 26-103), evt-petition-disposition

**P(grant) = 0.025; predicted disposition: denied.**

## Inputs used
- Snapshot `record/snapshots/2026-11-18.json` (forward mode, no cutoff): paid petition from the D.C. Circuit (No. 24-5218, judgment April 21, 2026), filed July 17, 2026; the United States obtained two extensions and filed a brief in opposition on October 23, 2026; distributed November 10 for the December 4, 2026 conference. One distribution, no relist, no CVSG, no amicus briefs, no reply brief on the docket yet.
- `questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt` (all with text, none truncated). I skimmed the petition and read the BIO's statement and argument; I did not rely on `appendix.txt` beyond what the briefs say of the opinion below.
- `record/context.json`: band `baseline` (sal-v8), `cert_anchor.rate` 0.0517, `cert_amicus_line` (arm `none`) 0.0268. `same-question.json` lists no similar pending petitions.

## Anchor and adjustments
The frozen anchor for a petition that has reached the `baseline` band is about 5.2% (risk-set rate, ten prior Terms). That figure includes petitions that later climb through relists; the no-amicus arm is about 2.7%, which is a floor-ish figure since a brief could still arrive, though with the petition already distributed that is unlikely here. The statpack's D.C. Circuit origin cut runs above average (granted 6.0% + gvr 2.1% of resolved, n=671), but that cut pools government petitions and is not specific to this posture.

Factors pulling down:
- **The United States is the respondent and opposes** with a full brief by the Solicitor General. Private petitions against the federal government opposed on both split and vehicle grounds are granted rarely.
- **The split is contested and looks shallow.** The petition claims a conflict over whether the Foreign Commerce Clause requires a nexus "with" the United States; the BIO says the cited Sixth and Eleventh Circuit decisions (Rife, Davila-Mendoza) concerned noncommercial conduct or other powers and that no court has adopted the petitioners' rule. On my read of the BIO's account, the cases are distinguishable enough that the Court can deny without confronting a square conflict.
- **Vehicle problems.** The claimant admitted all allegations and consented to judgment on the pleadings to speed the appeal, which the BIO says raises an antecedent appellate-jurisdiction question; the D.C. Circuit said the allegations sufficed "under any version of the test" (oil-price effects in the United States); and the BIO argues the question is at bottom statutory, with other constitutional powers available to sustain the provision.
- **Facts.** Sanctioned Iranian oil allegedly funding a designated terrorist organization is an unattractive setting for narrowing federal power.
- No amicus support.

Factors pulling up:
- Justice Thomas dissented from denial in Baston (2017) on exactly this subject and the petition is built around that writing; Justice Gorsuch has shown interest in original-meaning limits on the commerce power. That raises the chance of a relist for a separate writing more than the chance of four votes.
- Competent repeat counsel; published D.C. Circuit opinion; a genuinely open doctrinal question the Court has never squarely resolved.

Net: below the amicus-line reference, about 2.5%.

## Other claims
- `relist-increment` 0.07: most baseline petitions are decided at first conference; a small bump for a possible Thomas writing (which needs a relist) and for the residual grant path.
- `cvsg-increment` 0.002: the United States is already a party and has stated its views.
- `summary-disposition-route` 0.08 (conditional on grant): no intervening decision I know of that would prompt a GVR; a grant here would be plenary.
- `dissent-from-denial` 0.07 (conditional on denial): almost all of it is Justice Thomas, given Baston; the `order-writers` numbers match.

## Retrieval and caveats
One corpus query (generic granted priors) gave nothing case-specific; I made no CourtListener or web lookups and did not independently verify the cited circuit decisions, so my read of the split rests on the two briefs. A reply brief may still be filed before the conference; I have not seen one. I know of no outcome for this petition.
