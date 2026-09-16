# Why 0.08

## What I read

Provisioned inputs: snapshot `2026-09-15.json` (paid docket 25-1176, marked
CAPITAL CASE; petition filed Apr 3, 2026; BIO Jun 29; reply Jul 14;
distributed Jul 15 for the Conference of 9/28/2026; no amicus briefs; no
CVSG), `context.json` (`forward`, `band: baseline` under sal-v4,
`distribution_count: 1`, Term 2025), `event.yaml` (kind `petition`, no stage
recorded, so cert governs), and all three documents in `record/documents/`:
`questions-presented.txt`, `petition.txt` (47 pp.) and
`brief-in-opposition.txt` (36 pp.), none flagged `empty_text`. Earlier
prediction directories from the July fan-out exist under this event for three
predictors, including mine; I did not open any of them and forecast from this
moment's record alone.

## Anchor

Cert stage, band `baseline`, salience version sal-v4 matching the statpack's
"Segment base rate by salience band (sal-v4)" table. Pooling the bracketed
`reached` figures for `baseline` over the Terms strictly before this case's
(OT2017 through OT2024, all eight the table renders) gives 5.1% over a weighted
n of 11,580 (the last five Terms alone give 5.4%). That is the yardstick this
cell is scored against and my starting point.

Signal cuts read for shape, not adopted wholesale: the paid-segment
capital-case cut runs granted 11.8% / gvr 5.6%, well above the unmarked 4.2% /
2.3%, but it is a marginal, terminal-status split confounded with relists and
band. The relist-count cut puts terminal relist-0 petitions at 1.2% granted and
relist-1 at 8.2% granted / 5.1% gvr. The CVSG-none cut is 4.0% granted / 2.3%
gvr.

## Adjustments up

- Capital case, paid, with repeat Supreme Court counsel (McDermott; Yale
  clinic). The petition is well built and the "155 typos, signed without
  reading, re-adopted verbatim on remand" narrative is the kind that draws a
  Justice's attention.
- Question 1 describes a real and long-standing disagreement (First, Second,
  Seventh, Ninth Circuits and Iowa aggregating; Fourth, Sixth, Eighth
  declining), and this posture avoids AEDPA deference.
- A 3-2 split below, with a dissent that tabulated the mitigation record and
  invoked Thornell v. Jones.

## Adjustments down (these dominate)

- **Vehicle on Question 1.** The BIO's preservation point has bite: it says
  "cumulative" appears neither in the challenged opinion nor in Lindsey's
  state appellate brief, and that the state-court argument was a factual one
  about the weight of new mitigation. I checked the state supreme court
  opinion's text (CourtListener cluster 10731109). The majority never
  announces a rule against aggregation; it says "Even if trial counsel's
  investigation and presentation of evidence was deficient, we hold Lindsey
  was not prejudiced," describes one witness's testimony as insufficient
  "considered in isolation or in conjunction with other evidence," recites
  Thornell's balance standard, and closes by applying the aggregate
  "balance of aggravating and mitigating circumstances" test. So the Court
  would have to infer an implicit refusal to aggregate from the item-by-item
  structure. That is exactly the kind of petition the Court has declined many
  times on this question; the petition itself concedes the Court granted it in
  Banks v. Dretke and then did not reach it.
- **Question 2 is factbound.** The state supreme court already vacated once for
  the drafting errors and, on remand, credited the judge's statements that the
  order reflected his own view and that he reviewed it. Jefferson v. Upton
  concerned deference in federal habeas, not a freestanding due-process rule,
  and the Court has never held verbatim adoption unconstitutional. The BIO's
  point that petitioner participated in the proposed-order process without
  objection further weakens it.
- **No urgency.** Forward retrieval (D.S.C. No. 2:26-cv-00560) shows an
  indefinite stay of execution entered May 15, 2026 under 28 U.S.C.
  § 2251(a)(1), with the State not objecting, while federal habeas proceeds.
  No execution date is pending, and the same claims will get a federal look,
  which the Court often treats as a reason to stay its hand.
- **The Court's recent posture toward capital petitioners** has been
  unreceptive on Strickland-prejudice claims (Thornell v. Jones cut the other
  way), and grants for capital defendants since 2020 have been rare.

Net: roughly 1.5x the anchor, to 0.08. If I am wrong it is most likely because
the Court treats this as a Jefferson-type process failure and vacates
summarily, which is why the conditional summary-route probability is high.

## Increment claims

- `relist-increment` 0.38: the record shows one distribution. About a quarter
  of paid scored-segment petitions end with at least one relist (an upper
  bound that includes reschedules); I move up for the capital marking, the
  dissent below, and long-conference carry-over behaviour.
- `cvsg-increment` 0.02: state criminal case, no federal party.
- `summary-disposition-route` 0.45 (conditional on grant): the gvr share of the
  grant family in the relevant cuts is roughly a third, and the Jefferson
  analogue pushes higher here.
- `dissent-from-denial` 0.25 (conditional on denial): capital, 3-2 below, a
  narrative suited to a Sotomayor statement, but most such petitions are
  denied silently.

## Where to discount me

I cannot see the reply brief's text (not provisioned), so I do not know how
petitioner answered the preservation argument. I also read only keyword
excerpts of the 178,000-character state opinion, not the whole thing. The
capital-case cut suggests I may be too low if the marking carries independent
signal beyond relists and band. Retrieval was not degraded; the MCP server
and corpus service both answered.
