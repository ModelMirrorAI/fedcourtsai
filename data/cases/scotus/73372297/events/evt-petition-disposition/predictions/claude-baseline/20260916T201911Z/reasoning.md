# Rationale for the numbers

**P(grant) = 0.004; predicted disposition: denied.**

## What the record shows

- **Case.** No. 25-1300, Jane Doe v. Robert F. Kennedy, Jr., Secretary of
  Health and Human Services, a paid petition from a pro se petitioner seeking
  review of a Federal Circuit order and judgment of December 9, 2025 (No.
  2025-1769) in a National Vaccine Injury Compensation Program case that
  originated in the Court of Federal Claims. Petition filed March 9, 2026,
  docketed May 20, 2026.
- **Docket trajectory** (snapshot `2026-09-16.json`, three entries): petition
  filed; the Solicitor General waived the right to respond on June 17, 2026;
  distributed June 24, 2026 for the conference of September 28, 2026. One
  distribution, no relist, no CVSG, no amici, no response requested.
- **Provisioned documents.** I read `questions-presented.txt` and the full
  `petition.txt` (19 pages, text extracted cleanly, not truncated). No brief in
  opposition exists because the government waived. The questions presented are
  framed as whether a judgment "rife with" fraud, attorney malpractice, and
  attorney-judge collusion can stand, and whether a judgment "birthed from
  malice" can stand; neither states a legal rule. The petition's statement of
  the case describes a long-running Vaccine Act proceeding in which the
  petitioner received a damages award she does not reject but considers
  incomplete, and it acknowledges that the Federal Circuit affirmed on the
  ground that her motion for review in the Court of Federal Claims was filed
  too late. The reasons for granting are that the case illustrates criticisms
  of the compensation program made publicly by the respondent Secretary, that
  the proceedings were arbitrary and capricious, and that the Court should
  "set out punishments" for misuse of government records. It cites no circuit
  conflict and no decision of this Court.
- **Context.** `mode: forward`, `band: baseline` under `sal-v4`,
  `distribution_count: 1`, `cvsg_date: null`, `term: 2025`,
  `signals_observable: true`, `cutoff: null`.

## Anchor

The statpack's "Segment base rate by salience band (sal-v4)" table matches
the context's salience version, and the `baseline` band is my band. Pooling
the bracketed `reached` rate over the Terms strictly before OT2025 that the
table renders (OT2017 through OT2024, weighted by each row's `n`):

| Term | reached rate | n |
| --- | --- | --- |
| 2024 | 5.7% | 1271 |
| 2023 | 5.9% | 1312 |
| 2022 | 5.8% | 1192 |
| 2021 | 5.6% | 1500 |
| 2020 | 4.5% | 1739 |
| 2019 | 4.6% | 1399 |
| 2018 | 4.6% | 1524 |
| 2017 | 4.7% | 1643 |
| pooled | about 5.1% | 11580 |

So the anchor is roughly 5 percent. The other cuts point the same way or
lower: the relist-0 bucket of the paid scored segment grants 1.2 percent
(plus 0.5 percent GVR), the no-CVSG bucket 4.0 percent (plus 2.3 percent
GVR), and the Federal Circuit as originating court runs 3.1 percent granted
plus 1.5 percent GVR over modern cert petitions.

## Adjustments

I adjust from about 5 percent down to 0.4 percent, roughly a factor of
twelve, for reasons that are all in the same direction:

1. **No legal question.** The questions presented are grievances about the
   conduct of the special master and former counsel, not propositions of law.
   The Court grants to settle legal questions of general importance; a
   petition that presents none is outside the grantable population, whatever
   its band. This is the dominant factor.
2. **Pro se, paid.** The baseline band's 5 percent reached rate is dominated
   by counseled petitions with at least a colorable split or an important
   question. Pro se petitions, paid or not, grant at a rate that rounds to
   zero, and nothing about this one departs from that pattern.
3. **Posture below.** The Federal Circuit affirmed in a nonprecedential order
   and judgment on a timeliness ground, so even a reformulated question about
   the Vaccine Act review deadline would face a fact-bound vehicle in which
   the merits of the damages computation were never reached.
4. **Government waiver.** The Solicitor General waived a response, which is
   the office's signal that it sees no risk of a grant. The Court sometimes
   requests a response anyway, but only where a Justice sees something; I do
   not expect that here.
5. **No GVR vehicle.** There is no intervening decision of this Court bearing
   on Vaccine Act procedure, so the summary route that carries a meaningful
   share of baseline-band grants is closed too.

Why not lower still: the floor on any paid petition sitting at a conference is
not literally zero, because the Court occasionally GVRs or acts summarily for
reasons invisible in the petition, and I would rather be scored on a small
positive number than on a false certainty.

## The claims

- `disposition` 0.004, equal to the top-level probability.
- `relist-increment` 0.07. From one distribution, the population-wide chance
  of at least one more distribution entry is about a quarter (the relist-1,
  -2, and -3+ buckets against the relist-0 bucket), but that population
  includes the counseled petitions that actually get held for a Justice's
  look. For a pro se petition with a waived response, the remaining hazard is
  administrative: a reschedule out of the Long Conference's slate or a
  belated request for a response. I put that near 7 percent.
- `cvsg-increment` 0.002. The federal government is the respondent, so a
  CVSG is structurally out of place. I leave a sliver for a docketing anomaly
  rather than write zero.
- `summary-disposition-route` 0.7, conditional on a grant. The prior Terms'
  cert-order share of grants runs near half (577 GVR against 655 granted in
  the modern discretionary-cert table). For this case, plenary review is far
  less plausible than any summary action, so conditional on the Court doing
  anything, the summary route is the more likely form. I state the
  conditional, not its product with the grant probability.
- `dissent-from-denial` 0.005, conditional on a denial. No issue here has
  drawn a Justice's separate writing; the petitioner is pro se and the
  government did not oppose.

## Stakes

`big_case_score` 0.02. The dispute concerns one claimant's damages award in
the Vaccine Injury Compensation Program, affirmed below in a nonprecedential
order on timeliness. The petition invokes public criticism of the program by
the respondent Secretary, but the case itself supplies no legal question
through which the Court could address that debate, so a decision would have
no consequence beyond the parties.

## Uncertainty and where to discount me

- My main uncertainty is not about the disposition but about the relist
  increment, where the Long Conference's large slate makes administrative
  reschedules somewhat more common than at an ordinary conference and I have
  no committed cut for that.
- I did not consult CourtListener or the web. The forward mode permitted it,
  but the provisioned record and petition text settle every question the
  forecast turns on, and no external fact could plausibly move a pro se
  grievance petition with a waived response into grantable territory.
- The one corpus query I ran (recent SCOTUS grants in the 2020s era) returned
  generic high-profile grants and applications with no similarity to this
  case; the query surface filters on structured fields rather than case
  content, so it did not inform the number. I record it in `retrieval.md`.
- The petition text names a private individual's contact details and
  describes her health and military history. I have summarized rather than
  reproduced it, and I note the point in `flags.json`.
