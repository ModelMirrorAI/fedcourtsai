# Why 0.02, and not another number

## Inputs read

- `record/snapshots/2026-09-17.json` (the provisioned baseline; `context.json` names it).
- `record/context.json`: forward mode, band `baseline` under `sal-v4`, distribution
  count 1, no CVSG, Term 2025, `signals_observable: true`, no cutoff.
- `record/documents/questions-presented.txt` and `petition.txt` (53 pages, extracted
  cleanly, not truncated; `documents.json` lists both). No brief in opposition exists:
  the docket shows New York's waiver on June 24, 2026.
- `event.yaml`: kind `petition`, no `stage` recorded, so this is a cert-stage cell at
  the `distribution` moment.

## Anchor

The context freezes band `baseline`, and the statpack's "Segment base rate by salience
band (sal-v4)" table matches the context's salience version. Pooling the bracketed
`reached` figure over Terms strictly before this case's own (OT2017 through OT2024,
eight rows, weighted n = 11,580) gives **5.1%**. That is the population this petition
is in: a private paid petition that has reached baseline, with its future trajectory
still open. The OT2025 row (3.9%) is this case's own Term and is excluded.

Cross-checks from the paid scored segment: relist-count 1 bucket resolves granted
8.2% + gvr 5.1%, but that bucket is terminal count, not my state; the no-CVSG bucket
is granted 4.0% + gvr 2.3%; the CA2 originating-circuit bucket is granted 2.6% + gvr
2.3%. None contradicts the 5% anchor.

## Adjustments down (the bulk of the move)

1. **No split on the question presented.** Every court of appeals to reach the issue,
   eleven circuits per the Second Circuit's own footnote 3, reads § 1997e(d)(2) as a
   150% cap. The petition's "splits" are downstream corollaries (appellate fees, Sixth
   vs Ninth; pre-incarceration conduct, Tenth Circuit vs two district courts), not
   disagreement on the QP. A petition asking the Court to overturn a uniform 25-year
   consensus with no circuit on its side sits well below the band's average.
2. **Waiver with no call for a response.** New York waived on June 24. The Court
   essentially never grants without a response, so a grant would require a CFR first,
   and none had issued by September 17, eleven days before the conference. This is the
   strongest docket-level signal in the snapshot and it points to a routine denial.
3. **Summary order below, precedent-bound panel.** The Second Circuit disposed of the
   appeal in a non-precedential summary order that simply applied *Shepherd v. Goord*
   and declined a mini-en-banc; the petitioner conceded *Shepherd* bound the panel.
   There is no fresh reasoned opinion for the Court to engage.
4. **Murphy v. Smith cuts against the petitioner's reading.** I read the opinion via
   CourtListener. The Court did not decide the 150% question, but it read § 1997e(d)
   as a scheme that restrains rather than replicates § 1988 discretion, and footnote 2
   quotes the drafting history in which the second sentence's predecessor tied the
   defendant's share to the size of the fee award. A textualist reading that leaves the
   over-150% case ungoverned by the statute would have to work around that framing.
5. **Counsel and stakes.** Counsel of record is a regional firm rather than a repeat
   Supreme Court advocate, and the underlying verdict is $15,000 with a $22,500 fee
   award. Low stakes do not preclude a grant, but they do not attract one either.

## Adjustments up (modest)

- The vehicle is genuinely clean: a single, preserved, purely legal question, final
  judgment below, no cross-appeal.
- The literal-text argument has some force, and several circuits have conceded that
  the cap reading departs from the literal language (*Walker v. Bain*).
- The Court has shown interest in the PLRA fee provision before (*Murphy v. Smith*),
  and the nominal-damages fee awards the petition catalogs ($1.40, $1.50) are the kind
  of result a Justice might find worth a statement.

Net: 5.1% anchor, down roughly 60% for the uniform consensus and the waiver-with-no-CFR
posture, back up slightly for vehicle quality. **P(grant) = 0.02.**

## The other claims

- **relist-increment 0.15.** From one distribution and no CFR, the base path is a
  denial on the first order list. About a quarter of paid scored petitions end with a
  relist count of one or more, but that figure counts CFR-driven redistributions and
  reschedules, and this petition has neither yet. I put most of the 0.15 on a late CFR.
- **cvsg-increment 0.01.** No federal party, no federal interest the SG would be asked
  about; CVSGs in private-versus-state prisoner fee disputes are essentially unknown.
- **summary-disposition-route 0.08** (conditional on grant). No intervening decision
  exists to GVR against; a residual hold-and-GVR possibility if a companion petition
  were granted first.
- **dissent-from-denial 0.04** (conditional on denial). Statements respecting denial
  on PLRA fee questions are rare; the harshness of the nominal-damages results is the
  one hook.
- **big_case_score 0.18.** Real consequences for the prisoner civil-rights bar if
  decided, but a fee-allocation statute with low public salience.

## Uncertainties and where to discount me

- The largest uncertainty is whether a CFR issues between September 17 and 28. A CFR
  would roughly triple my grant number; I cannot see one and the snapshot is dated
  today, so I am forecasting from its absence.
- I have not read any brief in opposition because none exists. My read of the state's
  position is inferred from the waiver and the Second Circuit's footnote.
- The corpus prior queries were not informative: the citation lookup for *Murphy*
  returned no row (the statpack notes only 200 SCOTUS rows carry citation data), and
  the era/disposition query surfaced recent granted rows that were mostly substantive
  applications, not comparable cert petitions. The corpus service did respond, so this
  is a coverage gap rather than an outage.
- The CourtListener docket-entries endpoint returned zero entries for this docket, so
  I could not confirm post-snapshot docket activity beyond what the snapshot (dated
  2026-09-17) holds; nothing about this case's disposition surfaced in any retrieval.
- Base rates are from the committed `metrics/statpack.md`; band pooling used the
  eight prior-Term rows the table renders.
