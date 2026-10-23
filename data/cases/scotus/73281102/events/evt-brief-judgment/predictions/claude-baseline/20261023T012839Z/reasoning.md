# Reasoning — P(disturbed) = 0.80

**Inputs.** Forward cell; snapshot `2026-09-19.json` (cutoff 2026-09-19; the
docket runs through the 2026-09-18 filing of the Court-appointed amicus brief,
with argument set for 2026-11-02). Documents I read (in part): the QP section,
the Fifth Circuit opinion in `appendix.txt`, the petitioner's merits brief, and
the Solicitor General's merits brief "supporting vacatur" (summary of argument
and table of contents). The appointed amicus's brief was not provisioned and I
did not retrieve it, so I know the defense of the judgment only from what the
docket says about it and from the obvious historical-habeas line. Both merits
briefs being on disk is what this moment calls for (event opened 2026-09-18,
`moment: briefed`), so I don't flag it as an anomaly. I made no MCP or corpus
retrieval calls.

**Anchor.** The statpack's "merits docket" section publishes an `excluded`
count, so it can be quoted. The grant was 2026-06-01, which falls in OT2025, so
the pool is grant Terms 2015–2024. The table shows parsed rows only from 2017
on: 360 disturbed out of 516 parsed, which is **69.8%**. Coverage is near-complete
for those Terms (parsed versus granted is 73/75, 55/55, 73/74, and so on). This
rate is the bar the cell is scored against.

**Adjustment up.** Three things move me above the base rate.
- The respondent, through the SG, agrees that the decision below is wrong and
  asks the Court to vacate it. When the federal government confesses error and
  the Court appoints an amicus, the confessing side usually prevails. That's
  my recollection of the pattern, not a committed figure.
- The Fifth Circuit's rule is an outlier against other circuits, as the
  petition argues.
- The Court rewrote the question to the narrow habeas-vehicle issue, which
  reads like a grant aimed at correcting the error below.

**Adjustment down.** Several things hold the number below where the confession
of error alone would put it.
- The appointed amicus, Cooper & Kirk, is formidable, and at least two Justices
  are open to a Founding-era, release-only conception of habeas.
- The government itself floats a DIG and offers alternative grounds for
  affirmance. One is exhaustion, which the district court found. The other is
  the §3621(b) review bar.
- Mootness risk if petitioner is transferred. That pushes toward a
  *Munsingwear* vacatur, which disturbs, or a DIG, which does not.

Net: roughly 80% disturbed, 7–8% DIG, 12–13% affirmed.

**Judgment label.** I chose "vacated" over "reversed" because the SG explicitly
asks for vacatur and remand to address the alternative grounds first. This is
a coin-flip-adjacent choice. It doesn't affect the scored binary.

**Votes.** Low confidence (0.6). The two dissenters are a guess from those
Justices' known habeas-history writings.

**Uncertainty / discount.** I didn't read the amicus brief. My confession-of-error
prior comes from memory, not from the corpus. I haven't seen the argument, which
takes place after this cell.
