# Rationale for the numbers

**P(grant) = 0.004; predicted disposition: denied.**

## What I read

- Provisioned snapshot `record/snapshots/2026-09-16.json` (as-stored, forward
  mode, `signals_observable: true`). Paid docket (Supreme Court Press printed
  the petition), petitioners pro se (Ronald J. Dittmer is counsel of record for
  himself and his wife), respondent Katie Dittmer, their daughter-in-law.
  Lower court: Appellate Court of Illinois, First District (consolidated Nos.
  1-24-1269, 1-24-1274), order of September 18, 2025; Illinois Supreme Court
  denied leave to appeal January 28, 2026. Docketed May 4, 2026; response due
  June 3, 2026; **no brief in opposition and no waiver docketed**; distributed
  once, June 17, 2026, for the Conference of 9/28/2026. `distribution_count`
  frozen at 1, `cvsg_date` null, `band: baseline` under `sal-v4`, Term 2025.
- `record/documents/petition.txt` (26 pages, not truncated, text extracted)
  and `questions-presented.txt`. The petition contests two two-year Illinois
  orders of protection entered after a bench hearing on May 21, 2024, on a
  harassment theory. The narrative is a family estrangement: a "prayer walk"
  around the respondent's block, emails and a Christmas card to the
  petitioners' son and his family, and a 911 call. Claims: burdens on free
  exercise, speech, the right to keep and bear arms (firearm surrender under
  the order), due process, and equal protection; ineffective assistance of
  retained civil counsel; facial vagueness of the Illinois Domestic Violence
  Act; and procedural irregularities (an altered transcript, exhibits missing
  from the record, a compressed briefing schedule, Zoom witnesses not called).
  The petition's own account says the Appellate Court held the constitutional
  arguments **forfeited** because they were not raised at the hearing. The
  table of authorities cites one case (Kennedy v. Bremerton). It asserts no
  circuit or state-court split and identifies no conflicting decision.
- No brief in opposition exists to weigh against the petition.

## Anchor

`band: baseline`, `salience_version: sal-v4`, matching the statpack's
"Segment base rate by salience band (sal-v4)" table, so the anchor is the
**bracketed `reached`** rate for `baseline` pooled over Term rows strictly
before OT2025 (OT2017–OT2024, all eight shown). Weighted by the bracketed
`n`, those eight rows pool to roughly **5.1%** (n≈11,580) — the grant-family
rate (plenary grants plus GVRs) among paid scored petitions that ever reached
the baseline band. That is the yardstick the evaluator scores this cell
against.

Corroborating cuts, all paid scored segment: relist-count bucket 0 shows
granted 1.2% + gvr 0.5%; CVSG `none` shows granted 4.0% + gvr 2.3%; the state
originating-court rows show grant-family rates at or near zero (Illinois
courts do not appear individually; the `(none)` bucket, mostly state courts,
shows granted 0.5% + gvr 0.8%). The modern discretionary-cert section as a
whole puts grants plus GVRs at about 2.8% of resolved petitions.

## Adjustments

Down, by an order of magnitude, for reasons that compound:

1. **Pro se, fact-bound, no split.** The petition asks the Court to re-weigh
   the evidence in a family protective-order hearing. It names no conflict of
   authority and no question of general importance framed in a way the Court
   could take.
2. **Forfeiture below.** By the petition's own account the constitutional
   claims were not raised at the hearing and were held forfeited on appeal. The
   Court will not reach a federal question the state court disposed of on an
   adequate and independent procedural ground, and the ineffective-assistance
   theory has no Sixth Amendment footing in a civil proceeding.
3. **Vehicle.** An unpublished consolidated state intermediate appellate order,
   a discretionary denial by the state supreme court, and a private respondent
   who has not responded. There is no federal party and nothing for a CVSG.
4. **Originating court.** State-court petitions in the statpack grant at a
   small fraction of the federal-circuit rates.
5. **No GVR hook.** The `reached` anchor includes GVRs, which are roughly half
   of the grant family. A GVR needs an intervening decision that bears on the
   judgment below; I know of none pending on civil protective orders and the
   Second Amendment (Rahimi, 2024, predates the state decisions here and was
   available to the state courts), so the GVR share of the anchor mostly does
   not transfer.

The remaining mass is model uncertainty about the long-conference process
(a stray GVR, an unusual relist) rather than any positive feature of the
petition. 0.004 is roughly a tenth of the anchor; a pro se, forfeited,
family-court petition with no opposition is among the least grantable shapes
in the paid segment, and I would not defend a number above 0.01.

## Claims

- `disposition` 0.004 — equals `probability`.
- `relist-increment` 0.07 — the docket shows one distribution. Most paid
  petitions end at zero relists (bucket 0 holds about three-quarters of the
  segment), and a pro se petition with no response at the long conference is
  well below the segment average; the residual is mostly the chance of a
  reschedule entry, which the distribution count treats as a further
  distribution.
- `cvsg-increment` 0.003 — no federal interest of any kind.
- `summary-disposition-route` 0.7 — conditional on a grant. Population share
  of GVRs among grants is roughly half in Terms where the label is
  comparable; for this petition a plenary grant is far less plausible than a
  GVR, so I put the conditional above the population share.
- `dissent-from-denial` 0.01 — conditional on denial. No Justice writes on a
  pro se family protective-order denial where the federal claims were
  forfeited below.

## Big-case score

0.03. Stakes are confined to two individuals' two-year orders of protection
and the attendant firearm restriction; no rule of general application would
be settled even on the petitioners' own framing.

## Uncertainty and where to discount me

- I did not have the Illinois Appellate Court's order itself, only the
  petition's account of it (the petition's appendix was not provisioned, and
  the order is not on CourtListener). If the appellate court in fact reached
  the constitutional merits, adjustment 2 weakens, though the outcome would
  not change materially.
- The absence of a waiver entry is unusual but not informative about the
  merits; the Court distributes once the response deadline lapses.
- The corpus `query` returned only recency-ranked applications and a
  dismissal, none comparable; the prediction rests on the statpack and the
  provisioned documents rather than on retrieved priors.
- Forward cell; the CourtListener docket record was unchanged since June 17,
  2026 and showed no disposition, so no leakage arose.
