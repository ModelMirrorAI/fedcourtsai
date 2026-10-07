# Rationale for the numbers

**P(grant) 0.008; predicted disposition denied.**

## What I read

- The provisioned snapshot `record/snapshots/2026-10-06.json`: paid docket,
  Term 2026, pro se petitioner (counsel of record is the petitioner herself,
  Bismarck, ND), Eighth Circuit No. 25-2049 decided January 20, 2026, rehearing
  denied February 25, 2026, petition filed April 15, 2026 with a motion to file
  the supplemental appendix under seal, motion distributed for the September 28,
  2026 conference and granted October 5, 2026, response due November 4, 2026.
  Petition distributions: zero.
- `record/context.json`: forward mode, band `baseline` under sal-v4,
  distribution_count 0, no CVSG, no cutoff.
- No `record/documents/` directory was provisioned (no `documents.json`), so
  the pipeline fetched no petition text. I fetched the petition PDF from the
  docket link in the snapshot and extracted its OCR layer locally; and I
  fetched the Eighth Circuit opinion PDF from the court's opinion directory.
  CourtListener's MCP server returned HTTP 429 (daily quota exhausted) on both
  calls I made, so nothing below rests on CourtListener.

## What the filings show

The petition presents two questions: whether Younger abstention can reach
section 1983 claims about a warrantless child removal that preceded any state
proceeding, and whether Rooker-Feldman bars damages claims against officials
for pre-judgment conduct. The complaint sought damages, declaratory relief, and
return of the child; the district court (Hovland, J.) dismissed for lack of
jurisdiction under both doctrines, and the Eighth Circuit (Benton, Stras,
Kobes) affirmed in an unpublished Rule 47B per curiam that says only that it
found "no basis for reversal" after de novo review and that it may affirm on any
basis in the record. The district court's order is in a sealed appendix.

The claimed circuit split (Part VI of the petition) cites Wallis v. Spencer
(9th Cir. 2000) and Tenenbaum v. Williams (2d Cir. 1999). Both are merits
decisions on the Fourth Amendment standard for warrantless removals; neither
holds anything about Younger or Rooker-Feldman, so the petition identifies no
conflict on the questions actually presented.

## Anchor

The sal-v4 band table's bracketed `reached` rate for `baseline`, pooled over the
nine Term rows strictly before Term 2026 (2017 through 2025, weighted by the
`n` beside each figure), is about 5.0% (n ≈ 12,720). That is the rate every
paid private petition in this segment faces at the moment it is banded, and it
is the yardstick this cell is scored against. The modern-cert CA8 cut (granted
1.2%, GVR 1.4%) and the relist-0 bucket (granted 1.2%, GVR 0.5%) sit well below
it, as expected for terminal-state cuts.

## Adjustments

Down, strongly, for reasons that compound rather than overlap:

1. **No reasoned decision to review.** The Eighth Circuit gave no ground, and
   expressly reserved the right to have affirmed on any basis in the record.
   The Court would have to decide for itself which doctrine the dismissal rests
   on before it could decide whether that doctrine was misapplied.
2. **Sealed record.** The district court order, the only reasoned decision in
   the case, is sealed, which further obscures the actual ground.
3. **No real split.** The cited out-of-circuit cases decide a different
   question.
4. **Pro se petitioner, no amici, respondents are local officials** who will
   almost certainly waive. Paid pro se petitions grant at a small fraction of
   the paid-segment rate, and the band table does not separate them out.
5. **Posture.** Younger's fit for a damages suit about completed pre-proceeding
   conduct is a genuine doctrinal issue, and a better vehicle on it could
   interest the Court, but that is a reason to expect a grant some day on a
   different record, not on this one.

Up, slightly, for only one thing: the residual chance of a GVR should the Court
decide a Younger or Rooker-Feldman case during the months this petition is
pending, which I cannot rule out but have no concrete candidate for.

Net: 0.008, roughly a sixth of the band anchor.

## Claims

- `disposition` 0.008, as above.
- `relist-increment` 0.96. The frozen count is zero, so the first ordinary
  distribution of the petition resolves this claim true. The complement is the
  chance the petition never reaches a conference (a Rule 46 dismissal, a
  filing defect, or a dismissal for want of a timely docketing step).
- `cvsg-increment` 0.003. No federal party or federal-program interest.
- `summary-disposition-route` 0.75, conditional on a grant. Across the prior
  Terms in the per-Term table, GVRs are roughly half of the grant family; for a
  pro se petition with an unreasoned affirmance the GVR share of any grant is
  much higher than that, since plenary review of this record is close to
  excluded.
- `dissent-from-denial` 0.02. No writing expected on a Rule 47B affirmance.

## Big-case score

0.1. The underlying harm (warrantless removal of a child) and the Younger plus
Rooker-Feldman "no forum" argument are serious, but any decision here would be
confined to this record and the case has drawn no outside attention.

## Where to discount me

- I did not read the district court order (sealed) or the respondents'
  position (none filed yet), so my read of the ground below is inference from
  the petition's own account.
- The CourtListener MCP path was unavailable (rate limit), so I did not check
  the Eighth Circuit docket for the briefing below or the identity of
  respondents' counsel. A state Attorney General appearance would not change
  the forecast.
- The band anchor is a pooled segment rate that does not condition on pro se
  status; the size of my downward adjustment is judgment, not a published cut.
