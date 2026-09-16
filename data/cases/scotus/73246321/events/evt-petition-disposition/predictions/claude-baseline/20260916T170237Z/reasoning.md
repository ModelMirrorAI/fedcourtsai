# Why these numbers

**P(grant) = 0.005; predicted disposition: denied.**

## What I read

- The provisioned snapshot `record/snapshots/2026-09-16.json` (the file
  `context.json` names). Mode `forward`, band `baseline` under `sal-v4`,
  distribution count 1, no CVSG, Term 2025, paid docket (`sJsonCaseType`
  "Paid"), not a capital case.
- `record/documents/petition.txt` (10 OCR-derived pages, not truncated) and
  `record/documents/questions-presented.txt`. No brief in opposition exists:
  Allstate filed a waiver on June 22, 2026, after taking one extension.
- The committed `metrics/statpack.md`: the modern discretionary-cert
  disposition table, the relist-count and CVSG cuts, and the per-Term
  "Segment base rate by salience band (sal-v4)" table.
- One `fedcourts query` for recent denied SCOTUS priors (see
  `retrieval.md`), which confirmed the shape of the recent denied population
  but returned nothing specific to this case.

I did not make any CourtListener MCP call. The snapshot is dated today, the
conference is twelve days away, and the case's only lower-court record is a
Georgia Court of Appeals dismissal order plus a one-line Georgia Supreme
Court denial, neither of which CourtListener would add anything useful to.

## Anchor

The context carries band `baseline` under `sal-v4`, which matches the
statpack table's heading, so the bracketed `reached` rate for `baseline` over
Terms strictly before 2025 is the anchor. Pooling the eight rendered prior
Terms (2017–2024) by their `n`:

| Pool | Rate | Weighted n |
| --- | --- | --- |
| baseline, `reached` (risk-set), OT2017–OT2024 | 5.1% | 11,580 |
| baseline, terminal (leading figure), same Terms | 1.3% | 8,770 |

The 5.1% figure is what the evaluator scores skill against. It is the grant
rate over every paid petition that ever reached `baseline`, which includes
counseled petitions with real circuit splits that later climbed to `elevated`
or `high`. This petition is not one of those, so I move far below it.

## Adjustments down

1. **The petition has no cert-worthy content.** The argument section is two
   short paragraphs citing one case (*Haines v. Kerner*). It alleges no
   circuit split, no conflict with this Court's precedent beyond the
   liberal-construction principle, and no question of national importance.
   The three questions presented are generalized policy grievances about pro
   se litigants and procedural rules.
2. **Adequate and independent state ground.** The judgment below is a state
   appellate court's dismissal of a discretionary application as untimely
   (the Georgia Court of Appeals had already dismissed one appeal as untimely
   on October 24, 2024, and dismissed a second application on May 5, 2025).
   The Court does not review a state court's enforcement of its own filing
   deadlines, and the petition does not argue the rules were applied
   inconsistently or that the federal question was raised below.
3. **Pro se, no response.** The petitioner is counsel of record for himself.
   Respondent waived. The Court almost never grants a paid pro se petition of
   this shape; the relist and CVSG cuts show the pre-grant signals this
   docket lacks.
4. **No GVR hook.** No intervening decision of this Court bears on an
   untimely Georgia discretionary application, so the one grant route that
   does not require a cert-worthy question is also closed.

Taken together I place P(grant) at about half a percent. I do not go lower
because the Court's docket occasionally produces a surprise hold or GVR on a
petition of this class, and a proper score does not reward a zero I cannot
justify.

## The other claims

- **relist-increment 0.08.** The relist cut shows roughly a quarter of the
  paid scored segment ends with at least one additional distribution entry,
  but that count is an upper bound (reschedules count) and is dominated by
  petitions with some signal. A pro se paid petition at the Long Conference
  with a waived response is usually denied on the first pass. The residual is
  a reschedule or an administrative hold.
- **cvsg-increment 0.002.** No federal interest of any kind.
- **summary-disposition-route 0.75** (conditional on a grant). If this
  petition were granted at all, it would almost certainly be by a GVR or
  per curiam rather than plenary review, since the questions could not carry
  argument. I leave a quarter for the possibility that a grant would signal
  the Court had found a real question I cannot see in the OCR text.
- **dissent-from-denial 0.01** (conditional on denial). No Justice writes
  separately on petitions of this shape.

## big_case_score 0.02

An individual's dispute with an insurer, lost on a state procedural default.
Even decided, it would matter to the parties alone.

## Where to discount me

- The petition text is OCR-derived; a few lines are garbled ("September
  380, 2025"), but the argument section and questions presented are legible
  and I do not believe the OCR hid substance. The appendix (the state court
  orders) was not provisioned, so my characterization of the judgment below
  comes from the petition's own statement of the case, not the orders.
- The petition's cover says the writ is sought to the Supreme Court of
  Georgia, while the docket names the Court of Appeals of Georgia as the
  lower court. Either way the judgment under review is a procedural
  dismissal and the analysis is the same.
- The docket dates the petition filing "Oct 14 2025" while docketing and the
  received stamp are April 24, 2026, and the Georgia Supreme Court denial was
  September 30, 2025. This likely reflects a corrected refiling credited to
  its original receipt date; I have treated the petition as timely because
  the Clerk docketed it. A timeliness problem would only lower the number.
- I did not read this predictor's earlier July run on this event and this
  forecast is made from today's record alone.
