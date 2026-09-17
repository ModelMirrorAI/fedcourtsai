# Rationale for P(grant) = 0.01

## Inputs I used

Read in full: `record/context.json`, the snapshot `record/snapshots/2026-09-16.json`,
`record/documents/questions-presented.txt`, `record/documents/petition.txt`, and
`record/documents/brief-in-opposition.txt` (through its counterstatement and the
opening of its reasons for denial). `documents.json` reports all three documents
fetched with text (no `empty_text`, no truncation). Mode is `forward`; the cutoff is
null, so the snapshot is the latest poll. I did not read anything under
`data/qp-topics/`.

## What the record shows

- Paid petition (`sJsonCaseType: Paid`), filed May 6, docketed May 8, 2026, by two
  pro se petitioners (Douglas and Elisa Wain, appearing for themselves).
- Respondents are two Kentucky state judges sued in their official capacities only,
  represented by private counsel (Dentons Bingham Greenebaum). The Court of Appeals
  judge's sole involvement was signing one order denying emergency relief.
- Sixth Circuit affirmance of February 13, 2026, unpublished (BIO at 1), resting on
  absolute judicial immunity **and** on independent grounds: official-capacity claims
  are claims against the Commonwealth barred by the Eleventh Amendment, Ex parte
  Young does not reach injunctions against state judges, and section 1983's proviso
  bars injunctive relief against judicial officers absent a violated declaratory
  decree. Leave to amend to add individual-capacity claims was denied as futile.
- BIO filed June 8, 2026; distributed once, June 24, for the September 28, 2026
  conference. No relist, no CVSG, no amicus.
- The three questions presented are drafted around this case's own timeline
  (service at chambers, adverse ruling three days later). The petition asserts an
  "unresolved question" and "national significance" but cites no conflicting circuit
  decision; its section headed "Lower Courts Have Not Developed a Consistent
  Framework" is a concession that there is no split to resolve.
- The BIO's first point is that the questions presented were neither raised nor
  decided below (the complaint pleaded notice and bias claims about the foreclosure
  proceedings, not a Caperton-limits-immunity theory), and its second is that the
  decision rests on settled law (Stump, Mireles, Forrester).

## Anchor

`context.json` freezes `band: baseline` under `sal-v4`, matching the statpack's
"Segment base rate by salience band (sal-v4)" table, so the table is a valid anchor.
Pooling the baseline column's bracketed `reached` figures over Terms strictly before
this case's Term (OT2017 through OT2024, all eight prior rows the table renders)
gives roughly 5.1 percent (about 593 weighted grants over a weighted risk-set
denominator of about 11,580). That is the rate for every paid private petition that
ever reached the baseline band, the population the evaluator scores this cell
against.

The corpus-wide cuts beside it: relist-0 petitions grant about 1.7 percent including
GVRs (paid scored segment), and the no-CVSG bucket about 6.3 percent including GVRs.
The Sixth Circuit's modern grant family is about 2.8 percent. The terminal baseline
band grants about 1.2 percent including GVRs; that figure describes petitions that
never left the band, which is where I expect this one to end.

## Adjustments

Down, strongly, from the 5.1 percent anchor:

1. **Independent alternative ground.** Even a Court interested in the immunity
   question could not reach it: the judgment stands on Eleventh Amendment and
   section 1983 proviso grounds that the petition does not contest. This alone makes
   the petition an unusable vehicle.
2. **Preservation.** The BIO's point that the Caperton-versus-immunity theory was
   not pleaded or decided below is borne out by the petition's own account of the
   complaint (official-capacity claims about notice and bias) and by the Sixth
   Circuit's grounds as both sides describe them.
3. **No split.** The petition concedes lower courts have not addressed its question
   and identifies no conflicting appellate decision.
4. **Pro se, fact-bound, unpublished.** Each is a well-known negative marker; the
   questions presented recite the case's own facts rather than a rule.
5. **Serial litigation posture.** The BIO lists six additional state appellate
   proceedings the petition omitted, and the petition itself raises a side grievance
   about respondents' counsel's 2019 consultation. The Court reads this pattern as a
   collateral attack on a state foreclosure judgment.

Up, slightly: the petition is professionally printed and organized, the abstract
question (due-process disqualification versus absolute immunity) is a real one
that Williams v. Pennsylvania left open, and the campaign-depository allegation is
concrete. None of that survives the vehicle problems above.

Net: 0.01. Below the terminal baseline-band rate, because that population includes
counseled petitions with clean records that simply drew no interest.

## Other claims

- **relist-increment 0.10.** About a quarter of paid scored-segment petitions show at
  least one further distribution, but that count includes reschedules and is
  dominated by petitions with some hook. For a long-conference pro se petition with
  none, I expect a single pass; the 0.10 covers a mechanical reschedule.
- **cvsg-increment 0.005.** No federal interest.
- **summary-disposition-route 0.5.** Conditional on a grant I cannot construct a
  story for, I default near the population share of cert-order grants (GVRs are
  roughly 47 percent of the modern grant family).
- **dissent-from-denial 0.02.** Pro se, no split, alternative grounds. Judicial
  campaign-finance recusal has drawn occasional separate writings, which is why this
  is not lower.

## Retrieval and its limits

Two CourtListener MCP searches for the Sixth Circuit opinion (No. 25-5722) returned
nothing, so my reading of the decision below is through the petition's and BIO's
descriptions, which agree on its grounds. One `fedcourts query` attempt with a
free-text flag was rejected by the CLI, which takes structured filters only; no
available filter targets judicial-immunity petitions, so I did not retry. Nothing I
retrieved touched this case's disposition; the docket ends at the June 24
distribution and the conference is twelve days away.

## Where to discount me

The number is near the floor and the Brier cost of being wrong is high if the Court
holds this for some unforeseen reason. I cannot read the Sixth Circuit opinion
directly, and I have not verified the petition's characterization of the district
court's denial of leave to amend beyond the BIO's concurring account. The
`big_case_score` of 0.12 reflects that the abstract doctrinal question is real but
that a decision on this record would be narrow.
