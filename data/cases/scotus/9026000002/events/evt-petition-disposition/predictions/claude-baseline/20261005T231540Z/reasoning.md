# Rationale for my numbers (claude-baseline, run 20261005T231540Z)

**P(any grant) = 0.19; predicted disposition `denied`; granted = 0.**

## What I read

Provisioned inputs: `record/snapshots/2026-10-05.json` (six docket entries, June 26
to August 14, 2026), `record/context.json` (mode `forward`, band `baseline` under
`sal-v4`, distribution_count 1, no CVSG, Term 2026, cutoff null),
`record/documents/petition.txt` (the full 40-page petition including the Fifth
Circuit's summary-affirmance order, the *Town of Vinton* opinion it adopts, and the
district court's order) and `questions-presented.txt`. `documents.json` lists no
brief in opposition, which matches the docket: none has been filed. The snapshot's
caption class is private (insurers against a hospital service district), so the
`baseline` band the harness froze is the right floor and I used it.

Beyond the provisioned inputs (all listed in `retrieval.md`): the committed
statpack, two informative and two uninformative `fedcourts query` calls, four
CourtListener MCP docket searches (all empty: the MCP index does not carry SCOTUS
dockets), and web retrieval of the supremecourt.gov dockets for 26-2, 25-1383,
26-53 and 25A1218, the October 5, 2026 order list, the October 2 grant reporting,
and the lead case's petition, brief in opposition and reply (PDF text extracted
locally). This is a forward cell, so that retrieval is unrestricted; nothing I found
discloses this petition's outcome, and the order list confirms the cluster is
still pending.

## The anchor

Statpack, "Segment base rate by salience band (sal-v4)", `baseline` column,
bracketed `reached` figures pooled over OT2017 to OT2025 (every rendered Term
strictly before this case's Term 2026): the per-Term rates run 3.9% to 5.9%, and
the weighted pool is about **5.4%** (roughly 637 grants over 11,720 weighted
petitions). That is the rate a paid private petition that reached the baseline band
faces, and the yardstick the evaluator will score this cell against. The modern
discretionary-cert table's whole-docket grant family is lower still (granted 1.5%
plus GVR 1.3% of resolved), and the CA5 originating-circuit cut (granted 1.6%, GVR
2.1%) is in line with it.

## Adjustments up (to about 0.19, 3.5x the anchor)

1. **The Court called for a response on this docket** (July 28, after respondents
   waived), the strongest pre-conference signal a docket can show, and one the
   `sal-v4` band does not encode (the band reads distribution count, CVSG and
   caption class only). Calls for a response on a waived paid petition are
   historically followed by a grant something like one time in seven or eight.
2. **This is a tag-along in a three-petition cluster, and the lead is strong.**
   The petition itself asks to be held for No. 25-1383, *Indian Harbor v. Town of
   Vinton*: Skadden as counsel of record, two amicus briefs (the American Property
   Casualty Insurance Association and a group of international-arbitration
   scholars), a response requested there a day before this one, and now fully
   briefed. No. 26-53 (*Indian Harbor v. One Lakeside Plaza*, same Fifth Circuit
   line) was "Rescheduled" on August 27, the usual sign the Clerk is lining the
   cluster up for one conference. Two calls for a response in two days on the same
   question is a Justice's interest in the issue, not a clerical reflex.
3. **The question is a reserved one with an acknowledged split.** *GE Energy* (2020)
   expressly left open which law governs nonsignatory equitable estoppel under the
   Convention. The petition claims a 4-1 split (CA1 *InterGen*, CA2 *Smith/Enron*,
   CA4 *Aggarao*, CA9 *Setty* versus CA5). The reply documents that the Seventh
   Circuit joined the Fifth in *Kim v. Jump Trading* (August 13, 2026, Easterbrook,
   J.) while expressly acknowledging the four contrary circuits, and the BIO cites
   *Kim* as agreeing with CA5. A split acknowledged by the court that deepened it
   is the shape the Court grants on. The issue recurs across hundreds of Louisiana
   hurricane-coverage suits and the surplus-lines market generally.

My estimate for the lead petition being granted (including after a CVSG) is about
0.28. For 26-2 the grant family then arrives two ways: consolidation with the
lead (about 15% of that branch) or a hold followed by a GVR if the Court reverses
or vacates (about 85% x 65%). That gives roughly 0.28 x 0.70 = 0.20; I round to
0.19 to reflect the dismissal and affirmance residuals below.

## Adjustments down (why not higher)

1. **Vehicle problems in the lead case, and worse ones here.** The BIO's points are
   real: no live claim by or against any foreign party (the foreign insurers were
   released or dismissed with prejudice), separate contracts under the allocation
   endorsement so the Convention arguably never attaches, public-entity
   respondents against whom estoppel runs awkwardly, and a plausible argument that
   the answer would not change the outcome. The Fifth Circuit's primary holding
   (no foreign party, so the Convention does not apply) is independent of the
   choice-of-law holding. 26-2 adds a one-line summary affirmance and a nine-page
   petition that does not independently argue the vehicle.
2. **A cleaner vehicle is on its way.** *Kim v. Jump Trading* is a published
   Seventh Circuit decision from August 2026; a petition there would be due around
   November. The Court may prefer to deny this cluster and wait.
3. **No rehearing poll** was requested in the Fifth Circuit, and the panel was
   unanimous.
4. **Base rates are unforgiving**: even a petition with a call for a response and
   amici is denied most of the time.

## The other claims

- `relist-increment` 0.93: one distribution shown; the response request pulled the
  petition from the 9/28 conference and a redistribution after the BIO is docketed
  is standard. The residual is a withdrawal or dismissal before redistribution
  (the district court had set a bench trial for August 10, 2026, so settlement is
  live) rather than a decision without another distribution.
- `cvsg-increment` 0.10: P(CVSG on the lead) about 0.3; P(this docket also
  invited | lead invited) about a third; small independent chance.
- `summary-disposition-route` 0.78: conditional on a grant, the held-then-GVR path
  dominates consolidation, for the reasons above.
- `dissent-from-denial` 0.05: a tag-along to a technical commercial question; any
  writing would attach to the lead.
- `big_case_score` 0.3: significant for international-arbitration doctrine and the
  Louisiana insurance market, not a headline case.

## Uncertainties and where to discount me

- The biggest swing is my 0.28 for the lead petition. If the Court sees the
  response calls as routine clean-up after amici, the right number is nearer 0.15
  and this cell nearer 0.11; if a CVSG issues, the conditional rate after a CVSG
  (29% granted plus 6% GVR in the statpack's CVSG cut) would push the lead to 0.35
  or more.
- I did not read the 26-53 petition or the two amicus briefs in the lead case.
- I inferred the "lined-up cluster" reading from the 26-53 "Rescheduled" entry and
  the absence of a redistribution on 25-1383 after its reply; that is an inference
  about Clerk's-office practice, not something the docket states.
- The corpus `query` calls returned nothing topically relevant (no text or topic
  filter on SCOTUS rows), so no retrieved prior shaped the number; the anchor is
  the statpack band table alone.
- `fedcourts corpus-info` was not run in the cell; the corpus vintage behind the
  statpack is the committed pack's, and the live docket state I relied on was
  fetched from supremecourt.gov on 2026-10-06.
