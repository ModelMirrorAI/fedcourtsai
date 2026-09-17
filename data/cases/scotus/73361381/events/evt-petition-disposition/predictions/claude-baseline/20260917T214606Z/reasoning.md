# Rationale for the numbers

**P(grant) = 0.004; predicted disposition: denied.**

## Anchor

My cell is a `forward` cert cell at the `distribution` moment. The frozen
context gives `band: baseline` under `sal-v4`, `distribution_count: 1`,
`cvsg_date: null`, `term: 2025`. The statpack's "Segment base rate by salience
band (sal-v4)" table matches my salience version, so I pooled the bracketed
`reached` figure for `baseline` over the Terms strictly before 2025 that the
table renders (OT2017 to OT2024, eight rows):

| Term | reached rate | n |
| --- | --- | --: |
| 2024 | 5.7% | 1271 |
| 2023 | 5.9% | 1312 |
| 2022 | 5.8% | 1192 |
| 2021 | 5.6% | 1500 |
| 2020 | 4.5% | 1739 |
| 2019 | 4.6% | 1399 |
| 2018 | 4.6% | 1524 |
| 2017 | 4.7% | 1643 |

Pooled: about 593 grants over 11,580 weighted petitions, roughly **5.1%**
(the grant family, GVRs included). That is the yardstick the evaluator scores
this cell against. For context, the relist-count cut's relist-0 bucket runs
about 1.7% grant family and the CVSG-none bucket about 6.3%, and the modern
discretionary-cert table's overall grant-family share is about 2.8%.

## Adjustments, all downward

The pooled baseline rate is the rate for every private paid petition that
ever sat in the weakest band, including well-lawyered petitions with real
splits that later climbed. This petition sits at the bottom of that
population on every dimension I can observe:

1. **The federal question was not passed on below.** I read the Ohio Tenth
   District's opinion (Chaganti v. Cincinnati Ins. Co., 2025-Ohio-1982,
   decided June 3, 2025, well before my snapshot). It resolves the case on
   (a) the plain text of Section 4 of S.B. 224, (b) the Ohio Constitution's
   Retroactivity Clause, holding that eight years from the effective date
   left a reasonable time to sue, (c) the irrelevance of a 2020 California
   filing, and (d) waiver of an incorporation argument. It contains no
   federal due-process analysis at all. The petition's sole question is a
   Fourteenth Amendment notice claim, so the question appears unpreserved
   under 28 U.S.C. § 1257 and the Ohio Supreme Court's discretionary
   decline adds nothing. This is the single largest reason to sit far below
   the anchor.
2. **The legal theory is weak on its own terms.** The petitioner concedes
   (petition at 6 to 7) that S.B. 224 shows clear retroactive intent and
   that eight years is a reasonable time under Terry v. Anderson and Texaco
   v. Short. What remains is the claim that a duly enacted, published session
   law gives constitutionally inadequate notice because it is not printed in
   the codified Revised Code. Texaco itself says a legislature generally
   need only enact and publish the law. No court is cited holding otherwise.
3. **No split.** The petition offers Tabbaa v. Nouraldin (8th Dist. 2022)
   and a footnote in an S.D. Ohio decision as "confusion"; the Tenth District
   explains that Tabbaa's remark was dicta and that the Eighth District
   applied S.B. 224 the same way a year later in Brook Park v. Cleveland.
   Intra-state disagreement over a state statute is not a certworthy split
   in any event.
4. **Pro se paid petition, no response, no amici, no CFR.** The respondent
   filed neither an opposition nor a waiver; the petition was distributed on
   the deadline's lapse for the long conference. Any grant would first have
   to pass through a call for a response, which the docket does not show. The
   petition is 16 pages and cites no recent authority of this Court.
5. **Petitioner history.** CourtListener shows a prior cert petition by the
   same petitioner (No. 18-1425, denied June 2019) and a long run of
   pro se litigation in Missouri, California, Virginia, and the D.C. Court of
   Appeals, including a bar-discipline matter. Serial pro se petitioners
   grant at rates well below the paid population.

I also considered what could push up: the snapshot's case type is `Paid`
rather than IFP, and the underlying question (notice of uncodified law) has
some academic interest. Neither moves the number meaningfully.

Taking the pooled 5.1% anchor and discounting for an unpreserved federal
question, no split, a theory contrary to existing precedent, and a
no-response pro se posture, I land at about 0.4%. I would defend anything in
the 0.2% to 1% range; the number mostly measures the small residual chance
that I have misjudged the preservation issue or that the Court finds the
publication question interesting enough to call for a response.

## Claim-by-claim

- `disposition` 0.004: restates the headline.
- `relist-increment` 0.08: from one distribution and zero relists. The
  statpack's relist cut shows about a quarter of the paid scored segment
  ending with at least one further distribution, but that population is
  dominated by petitions with responses on file; a no-response pro se
  petition at the long conference is near the floor of that hazard, and the
  route that would most plausibly add a distribution (a call for a response)
  I already price low. Reschedules off the September conference are the
  residual.
- `cvsg-increment` 0.003: no federal interest of any kind.
- `summary-disposition-route` 0.25: conditional on a grant. No intervening
  decision exists to GVR against, but the grant family's cert-order share
  in prior Terms is substantial and I have little case-specific reason to
  depart far from it. Vacuous on the expected denial.
- `dissent-from-denial` 0.01: conditional on denial. No Justice has
  written on this theory and the case carries no recurring stakes.

## Big-case score

0.04. A one-party insurance dispute over a 2010 loss; the notice theory, if
adopted, would have broad implications, but nothing about the vehicle or
posture suggests it will be reached, and the stakes as framed are one
assignee's time-barred claim.

## What I read and where to discount me

Provisioned: `record/snapshots/2026-09-16.json` (the file
`context.json` names), `record/context.json`, `record/documents/petition.txt`
(16 pages, text extracted, not truncated) and
`record/documents/questions-presented.txt`. No brief in opposition was
provisioned because none was filed; my read of the respondent's position is
inferred from the Ohio opinion, not from any filing in this Court.

Retrieved: the Ohio Tenth District opinion via the CourtListener MCP server,
the CourtListener docket row for No. 25-1291 (confirming the docket is not
terminated as of CourtListener's data), and a party-name opinion search for
the petitioner's litigation history. CourtListener carries no docket entries
for this SCOTUS docket, so the snapshot is my only view of filings after the
petition. Corpus priors from `fedcourts query` for 2020s SCOTUS grants
returned mostly substantive emergency applications and one paid cert grant,
none comparable, so they did not move the number. I did not encounter this
case's disposition anywhere.

Discount me on the preservation reading if the petitioner's Ohio Supreme
Court memorandum in support of jurisdiction raised the federal claim; I did
not retrieve that filing, and the Tenth District opinion's silence is my only
evidence that the federal question was not pressed below.
