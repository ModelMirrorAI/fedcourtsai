# Rationale for the numbers

**P(grant) = 0.005; predicted disposition `denied`.**

## What I read

Provisioned inputs: `event.yaml` (kind `petition`, no stage recorded, so this
is a cert cell at the distribution moment), `record/context.json`
(`mode: forward`, `band: baseline`, `salience_version: sal-v4`,
`distribution_count: 1`, `cvsg_date: null`, `term: 2025`), the snapshot
`record/snapshots/2026-09-16.json`, and `record/documents/petition.txt` plus
`questions-presented.txt` (both `ocr_derived: true`, `empty_text: false`, 26
pages, not truncated; no brief in opposition was provisioned because none
exists — the respondents filed a waiver on May 13, 2026). The committed
`metrics/statpack.md` supplied the base rates.

## Anchor

The context band is `baseline` under `sal-v4`, which matches the version on the
statpack's "Segment base rate by salience band (sal-v4)" table, so the table is
my anchor. Pooling the `baseline` column's bracketed `reached` figures over the
Terms strictly before this case's own (OT2017–OT2024; OT2026 is a dash) gives
about 593 grants over about 11,580 weighted petitions, roughly **5.1%**. That
is the yardstick my skill will be scored against. The relist-count cut's
relist-0 row (granted 1.2%, gvr 0.5%) and the CA6 originating-circuit row
(granted 1.5%, gvr 1.3%) describe adjacent populations and agree that a
once-distributed petition from the Sixth Circuit sits well below the pooled
paid-segment rate.

## Adjustments down, and why they dominate

Every case-specific signal points the same direction, and together they take
this petition far below the baseline band's pooled rate:

1. **Pro se petitioner in a paid filing.** The petition names Mr. Gomez as
   counsel of record and "Petitioner Pro Se"; the docket carries no attorney.
   Paid pro se petitions are granted at a rate an order of magnitude below the
   counseled paid segment, and the baseline band's reached rate is dominated by
   counseled filings.
2. **Response waived and not requested.** Respondents waived on May 13 and the
   Court distributed on June 17 without calling for a response. A grant almost
   never issues without the Court first requesting a response; the absence of a
   request after a summer's distribution is itself a strong negative signal.
3. **Nonprecedential affirmance adopting the district court.** The petition's
   own account is that the Sixth Circuit affirmed "in a nonprecedential
   disposition, adopting the district court's reasoning in full." The Court
   rarely takes unpublished orders as vehicles for doctrinal questions.
4. **Independent, unchallenged grounds.** The district court also dismissed on
   Rule 12(b)(6) and immunity grounds. The respondents are state trial judges,
   a juvenile magistrate, a clerk, and a probation officer acting in connection
   with custody proceedings; judicial immunity would dispose of most claims
   regardless of how Rooker-Feldman came out, which makes Question 1 unlikely
   to be outcome-determinative.
5. **Vexatious-litigant posture.** The district court imposed prefiling
   restrictions, and the petition lists a prior cert petition from the same
   dispute (No. 24-6293, denied May 5, 2025) and an Ohio Supreme Court mandamus
   action. The Court treats a serial litigant's follow-on petition as a poor
   vehicle.
6. **The asserted splits are thin.** The Rooker-Feldman "split" is stated at a
   high level of generality with a mixed set of authorities, and the Court has
   declined many better-presented Rooker-Feldman petitions since *Skinner*
   (2011). Question 2 is a discretionary Rule 15 ruling with no proposed
   amended complaint in the record, per the petition itself.

Nothing pushes up: no amicus, no circuit-court dissent, no state or federal
party, no capital marking, no CVSG.

I land at **0.005**, about one-tenth of the band anchor. I would not go
lower than a few tenths of a percent because grants of pro se paid petitions,
while rare, are not unheard of, and a GVR in light of some unanticipated
intervening decision is always a tail possibility.

## Claims

- `disposition` 0.005 — identical to `probability`.
- `relist-increment` 0.07 — one distribution shown; the paid segment's
  terminal relist-≥1 share is around a quarter, but that population includes
  every counseled petition that drew interest, and the stored count is an
  upper bound that includes reschedules. For a pro se petition at the long
  conference with a waived response, I expect a clean first-conference denial;
  the residual is mostly long-conference reschedule noise.
- `cvsg-increment` 0.002 — no federal interest of any kind.
- `summary-disposition-route` 0.7 — conditional on a grant. If this petition
  were granted at all it would far more likely be a GVR or summary order than
  a plenary grant; I know of no pending merits case bearing on Rooker-Feldman
  or Rule 15 futility, which is why this is not higher.
- `dissent-from-denial` 0.01 — conditional on denial; no Justice has shown
  appetite for writing on Rooker-Feldman petitions from pro se litigants.

## big_case_score 0.04

Stakes are the parties' own: a custody-related section 1983 dispute with
immunity-protected defendants. The Rooker-Feldman scope question has modest
general interest, which is why this is not lower.

## Uncertainties and where to discount me

- The petition text is OCR-derived and garbled in places (section symbols
  read as "§ 19838", some case years are wrong); I read through the noise but
  could not verify the cited authorities' pin cites, and did not try to.
- The appendix (the Sixth Circuit order and the district court opinions) was
  not provisioned, so the characterization of the judgment below is the
  petitioner's own. Two CourtListener MCP searches for the Sixth Circuit
  disposition (by caption and by docket number 24-3840) returned no results,
  so I could not read the order itself.
- The corpus `query` I ran returned recent denied SCOTUS rows ranked by
  recency, mostly substantive applications; it confirmed nothing specific to
  this petition and did not move the number.
- The snapshot is same-day (`2026-09-16`), so I do not think the cell is
  mis-provisioned; the petition sits distributed for a conference twelve days
  out and no disposition exists.
