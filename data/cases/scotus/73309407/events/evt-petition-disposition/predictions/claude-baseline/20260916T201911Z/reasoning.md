# Rationale for the numbers

**P(grant) = 0.006; predicted disposition: denied.**

## What I read

- Snapshot `record/snapshots/2026-09-16.json` (the file `context.json` names; `snapshot_date` 2026-09-16, `snapshot_provenance` as-stored). Paid petition, docket 25-1263, Term 2025, not capital. Two docket entries: the petition (entry dated Feb 06 2026; response due June 8, 2026) and "DISTRIBUTED for Conference of 9/28/2026" on June 24, 2026. No brief in opposition and no waiver entry appears. Lower court listed as the Jackson County Circuit Court; Michigan Supreme Court order of November 21, 2025.
- `record/context.json`: mode `forward`, `band` = `baseline` under `sal-v4`, `distribution_count` = 1, `cvsg_date` null, `term` 2025, `signals_observable` true, `cutoff` null.
- `record/documents/petition.txt` (32 pages, full text) and `questions-presented.txt`. `documents.json` lists only those two; no BIO was fetched, consistent with the docket showing none filed.
- `event.yaml`: kind `petition`, no `stage` or `moment` recorded, so this reads as a cert-stage cell at the distribution moment.

## Anchor

The context band is `baseline` and the statpack's band table is computed under `sal-v4`, which matches `salience_version`, so the table is the anchor. Pooling the bracketed `reached` baseline figures over the Terms strictly before Term 2025 that the table renders (2017 through 2024; the table renders all ten Terms the pack holds) gives a weighted grant-family rate of about 5.1% (n ≈ 11,580). That is the yardstick this cell's skill is scored against. Cross-checks from the same pack point the same way: the relist-0 bucket of the paid scored segment shows granted 1.2% plus gvr 0.5%; the `cvsg: none` bucket shows granted 4.0% plus gvr 2.3%; the Court of Appeals of Michigan originating-court bucket shows zero grants in 89 resolved petitions; Term 2025's est. grant rate is 2.6%.

## Adjustments (down, substantially)

1. **Interlocutory posture, no final judgment.** The petition itself says the Michigan Supreme Court "declined to hear Petitioner's interlocutory appeal" from a bindover ruling after a preliminary examination; the criminal case has not been tried. Under 28 U.S.C. § 1257 the Court reviews final judgments of state courts, and none of the Cox Broadcasting exceptions is argued. This alone is close to dispositive against a grant.
2. **Fact-bound questions and no reasoned decision below.** QP I asks whether this petitioner had actual notice "on the night in question"; QP II invokes the capable-of-repetition mootness doctrine, which has no application. The only written decision is the trial court's; the Court of Appeals denied leave "for lack of merit" and the Michigan Supreme Court denied leave in a form order. There is nothing for this Court to review as a legal holding.
3. **No split, and a legislative ask.** The petition asserts national importance but identifies no conflict among courts; its requested relief is that the Court adopt a numeric THC threshold "until a standardized formula is set Nationally," which is not a question the Court would take up.
4. **Weak advocacy signals.** The petition is drafted by a county public defender's office, contains typographical errors in the questions presented, and mixes state-law statutory-interpretation arguments with the federal claim. The State did not respond (no BIO or waiver appears in the snapshot, and the distribution came after the response deadline), which is the ordinary handling of a petition the respondent considers hopeless.
5. **Baseline band and single distribution to the long conference** are consistent with the modal paid-petition path to a denial.

Weighing these, this petition sits well below the median petition in the `baseline` band, which already contains most paid petitions. I place it around 0.6%: not zero, because the band's pooled rate includes GVRs and occasional surprises, but roughly an order of magnitude under the anchor.

## Claims

- `disposition` 0.006: equals the top-level probability.
- `relist-increment` 0.08: the docket shows one distribution. About a quarter of the paid scored segment ends with at least one relist under the stored count, but that count is an upper bound (reschedules count) and is concentrated in petitions with some pull. Nothing here would draw a hold, a statement, or a second look, so I set it well below the segment's marginal rate while leaving room for housekeeping reschedules.
- `cvsg-increment` 0.005: no federal interest of any kind.
- `summary-disposition-route` 0.3: conditional on a grant. There is no intervening decision to GVR against, so both routes are remote; I put the cert-order route somewhat below the baseline band's historical GVR share of the grant family (roughly a third) but not far below, because plenary review of this vehicle is even less plausible than a GVR.
- `dissent-from-denial` 0.01: conditional on denial. No Justice has shown interest in a per se THC-impairment standard, and there is no reasoned opinion below to disagree with.

## big_case_score = 0.12

A national standard for THC impairment while driving would be significant if the Court ever announced one, but this vehicle would not produce that; a decision would be narrow and fact-bound. Score reflects stakes if decided, not grant odds.

## Uncertainties and where to discount

- The petition's docket entry is dated Feb 06 2026 although the petition is signed May 2, 2026 and docketed May 7, 2026; the petition mentions a February 12, 2026 letter from the Court and refiling within 60 days of it, so the February date is most plausibly the original deficient filing's date retained by the Clerk. This does not affect the forecast.
- I cannot see whether Michigan filed a waiver; its absence from the snapshot may be a gap in the stored docket rather than a fact about the docket. Either way it does not move the number.
- The `fedcourts query` priors I pulled (recent granted SCOTUS matters) were not comparable to this petition and did not inform the number; the anchor is entirely from the committed statpack.
- Forward mode: I checked the docket record on CourtListener; it shows no termination date and was last modified on the June 24 distribution, so the cell is correctly provisioned as pending. No outcome material surfaced.
