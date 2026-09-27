# Why these numbers

**P(grant family) = 0.01; predicted disposition: denied; big-case score 0.05.**

## Inputs read

- `record/context.json`: mode `forward`, band `baseline` under `sal-v4`, `distribution_count` 0, `cvsg_date` null, Term 2026, cutoff 2026-09-17 (`date` cut), `signals_observable: true`.
- `record/snapshots/2026-09-17.json`: paid petition, docketed September 16, 2026, one docket entry (petition filed, response due October 16, 2026). Lower court: CA6 No. 25-1631, decided June 18, 2026. Petitioners are two private LLCs and an individual; counsel is a Southfield, Michigan firm. Not a capital case.
- `record/documents/petition.txt` (38 pages, full text) and `questions-presented.txt` (extracted cleanly, only line-break artifacts). No brief in opposition exists yet, as expected at arrival.
- `metrics/statpack.md`: the sal-v4 salience-band Term table, the relist-count and CVSG cuts, the by-circuit cut.
- CourtListener MCP: confirmed the CA6 decision is **published**, decided by a panel of Griffin, Larsen and Readler, and carries a single opinion (so no separately recorded dissent below).

## Anchor

Cert stage, arrival moment, band `baseline`, salience version matches the table's (`sal-v4`). Per the arrival rule I anchor on my caption class's floor — the `baseline` band's bracketed **reached** rate — pooled over every Term row strictly before 2026 that the table renders (2017 through 2025; the 2026 row is empty).

| Terms pooled | weighted n | est. grants | pooled reached rate |
| --- | ---: | ---: | ---: |
| 2017–2025 | 12,720 | ~637 | **5.0%** |

So the private-petitioner arrival population grants (including GVRs) about 5% of the time. That is the yardstick my skill is scored against, and I am moving well below it.

## Adjustments down (large)

1. **The questions presented are not legal questions.** All five read "whether a grant of a writ of certiorari is warranted where the decision ... conflicts with well-established principles regarding X." That framing signals error correction and no articulated split. The body confirms it: the petition argues the panel misapplied settled law to the facts and never identifies a conflict among circuits on any point (the string cite of constructive-denial cases in Part II is offered as agreement, not disagreement).
2. **Fact-bound, poor vehicle.** Summary judgment affirmed; the record includes deficiency letters, conditional approvals issued, and a state-court declaratory judgment already won by petitioners. The delay argument (about 21 months) is argued as a jury question, which the Court does not review.
3. **Weak advocacy signals.** Solo/small-firm counsel with no visible Supreme Court practice; a comparison of the City's permitting conduct to the death of Eric Garner; a jurisdictional statement citing 28 U.S.C. §1257(a) (state-court review) for a federal court of appeals judgment. These correlate strongly with denial in the paid docket.
4. **Unanimous published panel below, no dissent**, and a Sixth Circuit origin whose modern grant family (granted plus GVR) runs about 2.8% on the by-circuit cut, at or below the docket average.
5. **Medical-marijuana setting.** The Court has shown no appetite for state-licensed cannabis disputes, and the federal-illegality backdrop makes it a less attractive vehicle for a property-rights holding.

## Adjustments up (small)

- The current Court is receptive to property-rights petitions (regulatory takings, exactions, Monell). A permit-delay takings or due-process question could in principle interest a Justice. But this petition does not isolate such a question, so I give it only a sliver.
- GVR channel: I know of no pending OT2026 merits case that would produce a hold-and-GVR here. If one exists that I am unaware of, my number is too low.

Net: 0.01, roughly a fifth of the class floor. Petitions with this shape (no QP, no split, error correction, small-firm counsel) sit at the bottom of the `baseline` distribution; the band's leading (terminal) rate is 0.6% to 1.8% per Term and this petition is unlikely to climb out of it.

## Claims

- `disposition` 0.01 — equals the top-level probability.
- `relist-increment` 0.96 — from zero distributions, this is P(at least one distribution). Paid petitions are distributed unless dismissed under Rule 46 or withdrawn first (about 1% to 2% of the docket); I leave a further margin for a distribution the parser fails to record.
- `cvsg-increment` 0.005 — no federal interest at all.
- `summary-disposition-route` 0.6 — conditional on a grant. The petition has no plenary vehicle, so a grant would most plausibly be a GVR after a hold; the prior Terms' cert-order share of grants runs roughly 30% to 59%, and this case's shape pushes above that.
- `dissent-from-denial` 0.02 — conditional on denial. Below the ordinary rate because the petition gives no Justice a clean statement to write about.

## Big-case score

0.05. A local zoning and licensing dispute involving one property; the constitutional framing is generic. Even if decided, the doctrinal payoff would be narrow.

## Uncertainty and where to discount me

- I have not read the CA6 opinion itself; the petition's account of it is the petitioner's. The panel's reasoning could contain a sharper holding on permit-delay deprivations than the petition conveys, but that would cut toward, not against, denial of a petition that does not frame it.
- No BIO exists yet; the City's response (or waiver) is the main future signal, and I forecast a waiver.
- I did not run `fedcourts query`: the tool filters on structured fields only, and no filter maps to "land-use due-process cert petition," so a pull would have returned untargeted priors. The statpack cuts carried the base-rate work.
- No knowledge of this case's outcome: it was docketed September 16, 2026 and is genuinely pending.
