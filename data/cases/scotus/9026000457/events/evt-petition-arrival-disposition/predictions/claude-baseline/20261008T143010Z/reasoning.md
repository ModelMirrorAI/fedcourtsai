# Rationale for the numbers

**P(grant) = 0.14; predicted disposition: denied.** Forward cell, cert stage,
`moment: arrival`, `band: baseline` under `sal-v4`, `distribution_count: 0`,
no CVSG, Term 2026. Snapshot read: `record/snapshots/2026-10-08.json` (five
entries: two time-extension applications granted by Justice Alito and the
petition filed October 2, 2026; response due November 6, 2026; paid docket;
lower court CA5 No. 24-60342, decided April 9, 2026, rehearing denied May 5,
2026).

## Anchor

The salience band table's version (`sal-v4`) matches the context's, and the
petitioner is a private corporation (Novartis) against a state officer, so the
caption class is `private` and the anchor is `baseline`'s bracketed `reached`
rate. Pooling every rendered Term strictly before OT2026 (OT2017 through
OT2025, n = 12,720 weighted) gives **5.0%**. I did not use the relist-0 row
(1.2%), which is the rate among petitions that ended undistributed and
understates an arrival's future. The statpack's modern-cert base rate for CA5
petitions is 1.6% granted + 2.1% GVR, which is the undifferentiated docket
and sits below the band floor.

## Adjustments up (to roughly 0.14)

- **Importance and institutional backing.** Twenty-two state 340B laws, a
  program measured in tens of billions of dollars, Hogan Lovells counsel of
  record, and the United States filing amicus briefs supporting the
  manufacturers in seven courts of appeals (petition, Part III and its
  footnote 3). The Eighth Circuit denied rehearing en banc in *Hanaway* by a
  5-3 vote with a written dissent, and the Fourth Circuit granted rehearing
  en banc in *McCuskey* on May 28, 2026 — both signals the question is
  regarded as exceptionally important.
- **A companion vehicle is imminent.** Justice Sotomayor extended PhRMA's time
  to petition from the Fifth Circuit's published Louisiana decision
  (*AbbVie v. Murrill*, No. 26A356) to November 3, 2026. That is public
  information predating my snapshot and is legitimate forward signal: the two
  petitions will be considered together, and a grant of the Louisiana case
  would carry this one either as a consolidated grant or a hold-and-GVR, both
  of which count as grants on the scored axis.
- **The petitioner asks for a CVSG**, and the Court's CVSG practice in
  federal-program preemption cases is well established.

## Adjustments down (why not higher)

- **Vehicle.** The decision below is an unpublished per curiam affirmance of a
  preliminary-injunction denial that considered itself bound by the earlier
  *AbbVie v. Fitch* panel; the Court rarely takes a PI-posture, unpublished
  decision when a published summary-judgment decision on the same statute from
  the same circuit is about to be presented.
- **The Court already passed once.** *PhRMA v. McClain*, No. 24-118, was
  denied on December 9, 2024 at its first conference, without a CVSG and
  without a noted dissent, on the same question from the Eighth Circuit. The
  petition's own account of what has changed (more state laws, the Fifth
  Circuit joining, the United States' circuit amicus briefs) is real but does
  not yet include a live appellate split on the state-law question: the
  Fourth Circuit panel decisions that created one were vacated by the en banc
  grant. The D.C./Third Circuit "split" the petition presses is about HRSA's
  authority, not state preemption, and the Court is likely to see it that way.
- **Percolation is actively under way.** The Fourth Circuit en banc and
  pending First, Sixth, Ninth and Tenth Circuit appeals give the Court an
  obvious reason to wait a year.

Net: the hold-or-grant pathway through the Louisiana petition and the
Court's demonstrated interest justify roughly three times the band floor, but
the modal path is denial after the Court declines to pre-empt the Fourth
Circuit en banc. 0.14.

## The other claims

- **relist-increment 0.96.** From a zero-distribution state this is
  P(at least one distribution), i.e. P(the petition reaches a conference).
  Only a withdrawal (e.g. a settlement or a legislative repeal of H.B. 728)
  prevents it.
- **cvsg-increment 0.25.** Above the paid-segment CVSG incidence (173 of
  roughly 14,000, about 1.2%) by an order of magnitude because the federal
  interest is direct, the petition asks for it, and a CVSG is the Court's
  cheapest way to wait for the Fourth Circuit; below even odds because the
  Solicitor General's position is already on the record in every circuit and
  *McClain* drew none.
- **summary-disposition-route 0.40 (conditional on grant).** The pack's
  cert-order share of the grant family runs 30-59% per Term. Here a grant is
  most plausibly a hold behind the Louisiana petition ending in a GVR, which
  pushes toward the middle of that range; a stand-alone plenary grant of this
  petition alone, which would put the figure near zero, is the less likely
  grant shape.
- **dissent-from-denial 0.12 (conditional on denial).** *McClain* drew no
  writing; a statement respecting denial pointing to the en banc proceedings
  is possible but not the norm.
- **big_case_score 0.62.** High policy stakes (340B's size, 22 states, the
  hospital-versus-manufacturer fight) tempered by the technical,
  preemption-doctrine shape of the question.

## Inputs and their limits

- Provisioned: the snapshot, `context.json`, `documents.json`, the petition
  (53 pages, full text, not truncated) and the derived questions-presented
  file. No brief in opposition exists yet (response due November 6, 2026), so
  the respondent's vehicle arguments are inferred, not read.
- Retrieval (forward mode, unrestricted): CourtListener opinion search for the
  circuit decisions; three web searches for the *McClain* docket history, the
  Louisiana petition's status, and the Fourth Circuit en banc status; two
  corpus `query` sweeps (details in `retrieval.md`). No search surfaced this
  petition's disposition, which does not exist yet.
- Corpus priors: `fedcourts query` limited to 500 rows ranked by recency did
  not reach the December 2024 *McClain* denial, so the McClain history comes
  from the web search, not the corpus.
- Uncertainty I would discount me on: how the Court treats the pair of
  petitions in January 2027 is the whole forecast. If the Louisiana petition is
  granted, this cell almost certainly resolves as a grant (consolidation or
  GVR); if the Court waits for the Fourth Circuit, it resolves as a denial.
  I put the first branch at roughly one in five and the chance this petition
  rides it at about two in three.
