# Rationale for the numbers

P(grant) = 0.40, disposition `denied` as the modal outcome, with `granted = 0`.

## Inputs read

- `record/snapshots/2026-10-05.json` (the provisioned baseline; snapshot date matches
  `context.json`). Thirteen docket entries: extension application granted by Justice
  Kagan, petition filed July 24, 2026, BIO filed August 26, five amicus briefs on
  August 28, distribution for the September 28 conference, reply, and the October 5
  CVSG order.
- `record/context.json`: mode `forward`, `band: high` under `sal-v4`,
  `distribution_count: 1`, `cvsg_date: 2026-10-05`, term 2026, `cutoff` null.
- `record/documents/`: `questions-presented.txt`, `petition.txt` (49 pages) and
  `brief-in-opposition.txt` (43 pages), all extracted with text (`empty_text: false`,
  none truncated). I read both filings in full.
- `metrics/statpack.md`: the modern-cert disposition table, the relist, CVSG and
  circuit cuts, and the per-Term "Segment base rate by salience band (sal-v4)" table.
- CourtListener (forward mode, unrestricted): the Ninth Circuit opinion's first page
  for the panel (Gould, Paez, and Chief District Judge McShane by designation; opinion
  by Gould; published, 153 F.4th 947). I did not search for this petition's own
  disposition; it is pending.

## Anchor

The context band is `high` under `sal-v4`, and the statpack's band table is headed
`sal-v4`, so the versions match. Pooling the bracketed `reached` figures for the
`high` column over the nine Term rows strictly before OT2026 (OT2017 through OT2025)
gives a weighted rate of about 35.5% on a risk-set denominator of 966. The most recent
three Terms run a little higher (about 37.8%). The CVSG cut of the paid scored segment
tells the same story: among CVSG'd petitions the grant family (granted plus GVR) is
about 34.9%, against 6.3% without one. So the anchor is roughly 0.35.

The relist cut is not used as an anchor here: a petition with one distribution and a
CVSG is in a different position from the terminal relist-1 bucket, which mostly counts
petitions that were simply denied after one reschedule.

## Adjustments

Up from the anchor:

- The CVSG came at the very first conference rather than after a relist, and the Court
  is plainly interested. The petition's own request for a CVSG was granted over the
  BIO's specific argument against one.
- Counsel and amici are top tier: Jeffrey Wall (former acting SG) as counsel of record,
  with the Province of British Columbia, the U.S. Chamber of Commerce, the National
  Mining Association, the American Petroleum Institute, the Pacific Legal Foundation,
  the Washington Legal Foundation, and the Canadian mining associations as amici.
- The merits hook suits this Court. The Ninth Circuit grounded its holding in section
  9651(c)(2), a "Reports and studies" provision in the "Miscellaneous provisions"
  subchapter, and the petition cites the Court's own recent language (Sackett, and the
  June 2026 Monsanto v. Durnell decision) about not finding major expansions in
  obscure provisions. The exposure is large and the federal government is itself a
  frequent CERCLA defendant, which gives the SG an institutional reason to support
  review.
- The stakes are concrete: more than $500 million in tribe-specific claims against
  $177 million in joint claims, with a district court that has described the case as
  carrying "potential for over $1 billion."

Down from the anchor:

- No real circuit split. The BIO is persuasive that neither New Mexico v. General
  Electric (10th Cir.) nor Ohio v. Department of the Interior (D.C. Cir.) addressed a
  cultural component, and the Ninth Circuit expressly aligned itself with Ohio. The
  petition's "three-way split" is a disagreement in emphasis, not in holdings.
- Interlocutory posture under section 1292(b), no damages awarded, and a trial court
  that has said it will not set trial until appellate issues are done. The SG has an
  easy "premature; the real dispute is methodology" path to a denial recommendation.
- The Interior Department's natural-resource-damage regulations have recognized nonuse
  and existence values since 1986 and expressly said in 2008 that cultural, religious
  and ceremonial losses "continue to be cognizable." A pro-Teck SG brief would have to
  distance itself from the government's own trustee regulations, which the current
  administration has not proposed to change.
- Teck's lead textual argument, the "use only to restore, replace, or acquire" clause of
  section 9607(f)(1), may not apply to tribes at all after the 1986 amendments; the BIO
  makes this a vehicle argument, and it is a fair one.
- The Court denied Teck's two earlier petitions in this same litigation (2008, after a
  CVSG in which the SG recommended denial; and 2019).

My rough decomposition: P(SG recommends grant or otherwise supports review) around
0.35 to 0.40; P(grant | SG supports) around 0.75; P(grant | SG opposes) around 0.20.
That yields 0.39 to 0.42, and I settle at 0.40, a modest step above the 0.355 anchor.

## Other claims

- `relist-increment` 0.96: any action after a CVSG requires redistribution once the SG
  files; the only path to no further distribution is a settlement dismissal first, which
  the respondent's brief itself argues is unlikely after 22 years.
- `cvsg-increment` 0.0: the CVSG is already on the docket (October 5, 2026), so the
  increment cannot occur; I expect the harness to mask this claim as vacuous.
- `summary-disposition-route` 0.05 (conditional on grant): no intervening decision
  bears on the question, and a novel statutory question will be set for argument. The
  statpack's CVSG cut shows GVRs at roughly 16% of the grant family, but those are
  cases where the SG points to a recent decision; none exists here.
- `dissent-from-denial` 0.15 (conditional on denial): after a CVSG, with strong
  business amici and a textualist hook, a short statement from one Justice is
  plausible but not the norm, and the interlocutory posture makes a silent denial the
  more likely form.
- `big_case_score` 0.55: a notable CERCLA remedies question with international and
  federal-PRP dimensions and half a billion dollars on the line, but technical and
  statutory rather than headline-grabbing.

## Uncertainties and where to discount me

- The whole number rides on the SG's recommendation, which I cannot observe. The
  current administration declined to file at the rehearing stage after the prior one
  supported the Tribes at the panel stage, which I read as genuine ambivalence rather
  than a signal either way.
- I did not read the Ninth Circuit opinion beyond its first page; my understanding of
  its reasoning comes from the two parties' characterizations, which differ sharply on
  what was actually held.
- I have no corpus prior that is a close analog. The `fedcourts query` calls I ran
  returned only generic recent grants (dominated by federal-party and emergency
  matters) and nothing on the citation filter, so the base-rate work rests entirely on
  the statpack cuts.
- Statpack vintage: the committed `metrics/statpack.md` describes the live/historical
  slice as of its build; its OT2026 band row is empty, so the pooled anchor uses
  OT2017 through OT2025 only, as the prompt directs.
