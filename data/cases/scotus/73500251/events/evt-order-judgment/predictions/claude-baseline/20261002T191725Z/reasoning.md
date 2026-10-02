# Rationale for the numbers

**P(disturbed) = 0.70; judgment = reversed; 7-2.** This is a `moment: grant` merits cell: certiorari was granted on 2026-10-01 (the last entry in the provisioned snapshot `2026-10-02.json`), and the forecast is made from the cert-stage record only.

## What I worked from

- Snapshot `record/snapshots/2026-10-02.json`: paid petition, docketed 2026-06-03 from the North Dakota Supreme Court (No. 20250066, decided 2026-03-04); respondent waived, the Court called for a response (2026-07-15), BIO filed 2026-08-26, reply 2026-09-08, one distribution (the 2026-09-28 long conference), granted 2026-10-01. Counsel of record for petitioner is Adam Unikowsky (Jenner & Block); respondent's counsel is a Minnesota family-law firm.
- `record/documents/`: `questions-presented.txt`, `petition.txt` (173 pages, truncated at the appendix, body intact), `brief-in-opposition.txt` (29 pages, complete). `documents.json` lists exactly these three. **No merits brief is on disk**, which is correct for this moment; the forecast is made from the docket skeleton plus the cert-stage filings.
- Retrieval (forward mode, unrestricted): the North Dakota opinion below (2026 ND 66) and the Court's opinion in Howell v. Howell, both via CourtListener; two `fedcourts query --citation` lookups that returned no rows (coverage gap, see `retrieval.md`). I did not search for and did not encounter anything about this case postdating the grant; the judgment does not exist yet.

## The anchor

The committed statpack carries a "The merits docket (granted cases)" section that publishes an `excluded` count (66 across all Terms), so it is quotable. The grant Term is **2026**: the grant date 2026-10-01 falls in October, and the repo's one date-to-Term rule puts an October grant in that year's Term (the cert docket number's Term, 2025, is the wrong axis for this table). The pool is grant Terms 2016-2025; the table renders every Term with a parsed judgment and its earliest row is 2017, so the shown window is the pool.

| Term | parsed | disturbed |
| --- | --: | --: |
| 2017-2025 pooled | 540 | 377 |

Pooled disturbed rate **377/540 = 69.8%**, well past the 30-parsed-judgment floor. Coverage caveat: Term 2025 is 24 parsed of 50 granted, and those 24 are the quicker dispositions; Term 2024 is 73 parsed of 75. The pooled figure is the baseline my Brier skill is scored against. I do **not** use the salience band (`baseline`) or any cert cut: the petition is granted and those describe a question that is settled.

## Adjustments, and why they net to roughly zero

Pushing above the base rate:

1. **The cert pattern.** The BIO documents that the Court denied certiorari in Yourko (2024), Martin (2024), and Tronsrue (2026), all petitions by veterans against state-high-court rulings that *enforced* settlement indemnity, and in Foster (2023), a petition by a former spouse against a Michigan ruling that barred it. It then called for a response and granted here, on a former spouse's petition against a ruling that barred enforcement. Leaving three enforcement-permitting rulings in place and taking the first clean enforcement-barring one is weak but real evidence that the Court's center is not troubled by enforcement.
2. **Doctrinal fit with the current bench.** The North Dakota holding rests on Howell's "regardless of their form ... stand as an obstacle to the ... purposes and objectives of Congress" passage, which is purposes-and-objectives preemption, the one part of Howell Thomas declined to join. Several current Justices are skeptical of that mode; the petitioner's affirmative case is textual (1408(c) is a grant of judicial power to "treat" pay as property, not a regulation of private promises), supported by the waiver presumption (Mezzanatto) and Rose v. Rose.
3. **Howell's own reservation and the equities.** Howell said "we need not and do not decide these matters," and the Howell petitioner's counsel told the Court that a settlement waiver would be enforceable. Petitioner here paid $140,500 of present consideration for the promise. The Court's grants-to-reverse base rate already prices sympathetic petitioners, but this one is unusually clean on that axis.

Pulling back toward or below it:

1. **Mansell was a settlement case.** The BIO's strongest point: the Mansell decree incorporated a property settlement dividing total retired pay including the waived portion, and the Court held the state courts had no power to treat that pay as divisible. Petitioner's answer (Mansell never considered a waiver argument and the veteran there sought modification) is plausible but not airtight, and 1408(a)(2)'s definition of "court order" expressly includes "a court ordered, ratified, or approved property settlement," which the respondent reads as Congress treating settlements and decrees alike.
2. **Express anti-assignment text for the VA portion.** 38 U.S.C. 5301(a)(3)(A) deems an agreement by which another "acquires for consideration the right to receive such benefit" a prohibited assignment. Most of the money here is Chapter 61 pay waived to VA disability pay. The clause is aimed at benefit-advance schemes and Rose v. Rose limits 5301, but it gives a textualist a hook for affirmance.
3. **Vehicle.** The trial court granted Rule 60(b) relief and recast the remedy as spousal support; the operative terms are in a post-judgment order; the decree never says "indemnify." The Court could affirm on the ground that what happened below was a court-imposed restoration indistinguishable from Howell, or DIG. I put the DIG at about 0.05 and the "affirm because this record is Howell, not a contract case" route inside the ~0.24 affirmance mass.
4. **Trajectory of the line.** McCarty, Mansell, and Howell each reversed a state court for reaching military pay; a Court that has policed this statute strictly three times may be reluctant to bless a drafting workaround that would restore the pre-Howell status quo in every well-counseled divorce.

I weighed these as roughly offsetting and landed on 0.70, essentially the committed baseline. That is a considered judgment that the case-specific signals are balanced, not a default; the scoring rule is proper and I would not move the number to manufacture skill.

## Votes and judgment label

The vote block is banked, not scored, and I hold it loosely. The 7-2 lineup reflects the view that the purposes-and-objectives basis of the ruling below is unattractive to most of the bench while Mansell's settlement facts and the 1408(a)(2)/5301 text give a pair of Justices a principled dissent; Thomas and Alito are my best guess for that pair, but a unanimous reversal is nearly as likely as 7-2 and the identity of any dissenters is low-confidence. I chose `reversed` over `vacated` because the North Dakota court's holding is a categorical federal-law rule the Court would reject outright, as it did in Howell ("reversed, and the case is remanded"); a `vacated` label is nearly as likely if the Court frames the state-law questions (whether this decree is such an agreement) as requiring fresh analysis under a corrected standard. The two labels score identically on the disturbed axis.

## Semantic claims

Both propositions are written on the assumption the judgment is disturbed, since that is the forecast. If the Court affirms, both come back wrong, which is the honest exposure of a committed forecast. The majority-ground claim stakes out a specific basis (judicial-power reading of 1408(c), waiver presumption, Rose, Howell distinguished as court-imposed) and a specific road not taken (5301 as a ground); the breadth claim stakes out "categorical on the federal question, remand on the state-law application."

## Where to discount me

- No merits briefing, no SG position. If the Solicitor General files for respondent (the government supported the former spouse in Howell and lost, so its view on the contract question is unknown), I would move down several points; if for petitioner, up.
- I know Mansell and Howell well and have read the opinion below, but I have not read Yourko, Tronsrue, Martin, Jones, or Foster beyond the parties' characterizations.
- The `fedcourts query --citation` lookups returned nothing (only 200 SCOTUS rows carry any citation), so the corpus contributed the statpack baseline and nothing case-specific.
- `big_case_score` 0.30: a recurring family-law/veterans question with a real split and a large affected population, but technical and low in public salience.
