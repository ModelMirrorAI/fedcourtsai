# Why 0.30

## What I read

Provisioned inputs, in order: `AGENTS.md`, the predict prompt and schema, the
event definition (`stage: cert`, `moment: distribution`), the snapshot
`record/snapshots/2026-10-05.json`, `record/context.json` (`mode: forward`,
`band: elevated` under `sal-v4`, `distribution_count: 2`, `cvsg_date: null`,
`term: 2025`, paid docket), and the three provisioned documents:
`questions-presented.txt`, `petition.txt` (truncated at the appendix, so the
petition body is complete but the Fourth Circuit opinion appended to it is
not), and `brief-in-opposition.txt` (complete). Because this is a forward cell
I also fetched the three later filings the docket lists but the pipeline did
not provision: the petitioner's reply (Sept 9), the respondents' Rule 15.8
supplemental brief (Sept 14), and the petitioner's response to it (Sept 15).
`retrieval.md` lists each lookup.

## Anchor

The context carries a frozen `elevated` band under `sal-v4`, and the statpack's
"Segment base rate by salience band (sal-v4)" table matches that version, so
the anchor is the bracketed `reached` rate for `elevated` pooled over Terms
strictly before OT2025. Pooling the eight rendered prior Terms (OT2017 to
OT2024) gives 484/2810, about **17.2%**; the last five alone give about 18.1%.
That is the yardstick the evaluator scores this cell against.

Two cross-checks from the statpack's relist cut, read as shape rather than
answer: among paid scored petitions that reached one relist, roughly 28% went
on to a second, and the grant family (granted plus GVR) was about 13% for those
that ended at one relist and about 40% for those that went further. Weighting
those by the onward hazard gives roughly **20%** for a petition that has
reached exactly one relist, close to the band anchor. The Fourth Circuit's
originating-court cut (grant family about 2.5% over all its petitions) and the
no-CVSG cut (about 6.3%) are population-wide and sit well below the conditioned
anchors, as expected.

## Adjustments up (from about 0.18 to the mid 0.30s)

- **Genuine, acknowledged split on the exact question.** The Fourth Circuit's
  published opinion (Niemeyer, J., joined by Harris, J.) adopts a categorical
  rule that Section 362(k) damages claims are non-arbitrable. Judge King's
  dissent says in terms that the panel "creates a clear circuit split" with the
  Second Circuit's *MBNA v. Hill* and that there is "a very solid chance" of
  reversal. Respondents themselves told the Fourth Circuit that circuit
  precedent "simply cannot be reconciled with" *Hill*. The Court rarely gets a
  cleaner dissent-flagged split.
- **The Court's FAA docket.** The Court has repeatedly taken FAA displacement
  and scope questions on thin splits, and it has never addressed how *McMahon*
  applies in bankruptcy, a gap the petition documents with judges and scholars
  calling the area a "morass." The Fourth Circuit expressly declined to follow
  the Court's "recent trend," which is the kind of lower-court resistance the
  Court tends to correct.
- **Petitioner-side quality.** Latham & Watkins with an experienced Supreme
  Court advocate as counsel of record; an American Bankers Association amicus
  brief at the cert stage; a merits posture (closed Chapter 7 for Maze) that is
  materially identical to *Hill*.
- **The relist itself.** Relisted once after the long conference, which is
  the strongest single docket signal available at this moment, and is already
  reflected in the elevated band.

## Adjustments down (back to 0.30)

- **The September 10 dismissal.** The respondents' supplemental brief
  discloses that the bankruptcy court granted Goldman's motion to dismiss the
  adversary complaint without prejudice for failure to plead actual damages,
  with 21 days to amend. The arbitration ruling remains in force and the
  petitioner argues (plausibly) that the forum dispute is unaffected because
  respondents will replead the same Section 362(k) claims. But the Court is
  cautious about granting review of a complaint that no longer exists, and the
  timing fits the relist: distributed September 9, the supplemental briefs
  landed September 14 and 15, and the Court relisted rather than acting. I read
  the relist as at least partly a vehicle check rather than a pre-grant signal.
- **Section 105(a) and the open Chapter 13 case.** The BIO's strongest points
  are that Goldman concedes contempt relief under Section 105(a) is not
  arbitrable, that the complaint invoked Section 105(a) alongside Section 362(k),
  and that Brown's Chapter 13 case is still open, a posture no other circuit
  has addressed. The reply answers each well (contempt is a motion in the
  main case, not a claim; *Hill* asks about effect on administration, not
  estate ownership), but together they give a Court looking for a cleaner
  vehicle a reason to wait.
- **Two prior denials nearby.** The Court denied certiorari in *Credit One
  Bank v. Anderson* (2018) and *GE Capital Retail Bank v. Belton* (2021), both
  Second Circuit refusals to compel arbitration of bankruptcy debtor-protection
  claims (the discharge injunction). The petitioner distinguishes them as
  contempt rather than private-claim cases, which is right, but the pattern
  shows the Court has twice passed on arbitration-in-bankruptcy.
- **A 1-1 split with a twenty-year-old opposite pole.** *Hill* is from 2006
  and the Second Circuit has not applied it since; the BIO argues a future panel
  could revisit it in light of *Anderson* and *Belton*. The Court sometimes
  prefers to let such a split percolate.

Net: I land at **0.30**, above the 17% band anchor and the 20% relist-hazard
cross-check because the split is unusually well-documented and the petition
unusually well-presented, but well short of even odds because the vehicle
developed a real problem days before the first conference and the question is
one the Court has let pass before.

## Other claims

- `relist-increment` 0.42: the population hazard from one relist to two is
  about 28%; I move up because this petition's two live uncertainties (the
  dismissal's effect, and whether to call for the SG) are the kind that take an
  extra conference, and a CVSG itself produces a later redistribution.
- `cvsg-increment` 0.12: no federal party, but a two-statute question the
  government has an institutional stake in through the U.S. Trustee Program.
  The statpack's CVSG cut shows how rare CVSGs are overall (about 1% of paid
  scored petitions), so 0.12 is a meaningful upward read from the relist and
  subject matter.
- `summary-disposition-route` 0.04: nothing to GVR in light of; the Fourth
  Circuit's reasoned divided opinion is not a summary-reversal shape.
- `dissent-from-denial` 0.22: relisted-then-denied petitions carry separate
  writings more often than the docket average, but a business FAA petition with
  a vehicle problem is a less natural occasion for one.
- `big_case_score` 0.45: stakes are real for consumer finance and consumer
  bankruptcy practice nationwide, but the case is technical and low in public
  salience.

## Uncertainty and where to discount me

- I could not read the Fourth Circuit opinion itself: the provisioned petition
  text is truncated at the appendix. My account of the opinion comes from the
  petition, the BIO, and the reply, which agree on its structure.
- The relist is the pivotal signal and is ambiguous between "vehicle check,"
  "someone is writing," and "pre-grant." I weighted the first because of the
  timing against the supplemental briefs; a reader who reads relists after the
  long conference as mostly pre-grant should sit nearer 0.40.
- I did not see the ABA amicus brief's text; its existence and the reply's
  summary of it are what I used.
- Corpus priors: `fedcourts query` by citation for the *Belton* and *Anderson*
  cert dockets returned nothing, and the tool's note says the citation column
  is barely populated on SCOTUS rows, so the corpus added no case-level prior
  beyond the statpack cuts. The anchor rests on the committed statpack, whose
  band table is the evaluator's own yardstick.
