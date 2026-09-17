# Rationale for the numbers

## Inputs read

- `record/snapshots/2026-09-17.json` (the file `context.json` names), `record/context.json` (`mode: forward`, `band: elevated`, `salience_version: sal-v4`, `distribution_count: 2`, `cvsg_date: null`, `term: 2025`).
- `record/documents/questions-presented.txt`, `petition.txt` (160 pages, flagged truncated; the argument sections through the conclusion were intact, the truncation falls in the appendix), and `brief-in-opposition.txt` (31 pages, full text). `documents.json` shows none with `empty_text`.
- `metrics/statpack.md`: modern discretionary-cert base rates, the relist / CVSG / circuit cuts, and the sal-v4 segment table.

## Anchor

Cert stage, `moment: distribution` (the event records no stage, so it reads as cert). The context's band is `elevated` under sal-v4, and the statpack's segment table is also sal-v4, so the band table is the anchor. Pooling the bracketed `reached` figures for `elevated` over Terms 2017 through 2024 (every rendered Term strictly before this case's Term 2025):

| Term | reached rate | n |
| --- | --- | --: |
| 2024 | 17.9% | 336 |
| 2023 | 17.5% | 354 |
| 2022 | 19.0% | 300 |
| 2021 | 20.5% | 342 |
| 2020 | 16.1% | 397 |
| 2019 | 13.8% | 334 |
| 2018 | 15.9% | 347 |
| 2017 | 17.5% | 400 |

Weighted pool: roughly 484 grants over 2,810, about **17%**. That is the yardstick I am scored against and my starting point.

## Adjustments

**Down, and materially, on vehicle and split quality.** The brief in opposition (MacArthur Justice Center, a repeat Supreme Court shop) makes three points I find persuasive on the cert calculus regardless of the merits:

1. **No acknowledged split.** The petition's "three circuits versus two" lineup rests on the Eleventh Circuit's Ancata, the Seventh Circuit's King, and the decision below on one side, and on fact-bound Sixth Circuit rulings plus a Western District of Texas opinion the Fifth Circuit expressly declined to reach on the other. No court of appeals has recognized a conflict, and the petition for rehearing en banc did not claim one. The Fourth Circuit denied rehearing with no judge calling for a poll.
2. **Interlocutory posture.** The Fourth Circuit reversed summary judgment and remanded for trial. The case proceeds to trial against Southern Health Partners whatever happens to the counties, and causation and the counties' immunity defenses are unresolved. The Court rarely takes a Monell scope question on an interlocutory record without a clean split.
3. **Party presentation.** The respondeat superior framing that anchors both questions presented was first pressed in the rehearing petition, borrowed from the dissent.

The petition itself is a regional-firm product with drafting errors and an overstated "automatic liability" characterization that the BIO dismantles by quoting the majority's reliance on the contracts' specific delegation language. No amicus brief appears on the docket, which is notable for a question the petition says affects most US jails; county and municipal-league amici often appear when this constituency is exercised.

**Up, modestly, on the Court's own signals.** After both respondents waived, the Court called for a response on May 8, 2026. A call for response is the clearest pre-conference signal that the petition drew attention beyond the pool memo. The decision below is published (160 F.4th 438) and 2-1, with Judge Richardson's partial dissent squarely framing the Monell holding as respondeat superior in disguise. The co-respondent contractor filed a brief in support of the petition. The issue is genuinely recurring. Most of this, however, is presumably what placed the petition in the `elevated` band in the first place, so I count it only lightly on top of the anchor.

**A caution about the band.** `distribution_count` is 2, but the first distribution was superseded by the call for a response before the May 14 conference; the petition has not been relisted in the ordinary sense. To the extent sal-v4 keys `elevated` on the distribution count, the band may be reading a relist that did not happen, which is a further reason to sit below the pooled anchor rather than on it.

Net: **P(grant) = 0.11**, below the ~17% pooled anchor. `predicted_disposition` is `denied`; a grant, if it came, would be plenary rather than summary.

## Other claims

- `relist-increment` 0.35: forecast from the two-distribution state. The statpack's relist cut buckets by terminal count and is denial-reweighted over the whole segment, so it gives shape, not the hazard from this state; roughly a quarter of paid scored petitions ever show a relist, and petitions carrying a call for response and a published dissent below sit well above that. I do not treat this case as being in bucket 2, for the reason above.
- `cvsg-increment` 0.03: no federal interest; the statpack shows CVSGs on about 1% of the paid scored segment.
- `summary-disposition-route` 0.12, conditional on grant: the prior Terms' cert-order share of the grant family runs 30-50%, but that share is dominated by GVRs against intervening decisions, and none exists here.
- `dissent-from-denial` 0.08, conditional on denial: possible interest from Justices skeptical of expansive lower-court Monell doctrine, but the interlocutory posture and party-presentation problem make it a poor case to write on.
- `big_case_score` 0.4: a decision would set the Monell rule for privatized jail health care nationwide, which matters to a large population of detainees and local governments, but the case is a doctrinal question without broader public salience.

## Uncertainty and where to discount me

- I cannot see the reply brief or the contractor's brief in support; both are on the docket but neither was provisioned, and CourtListener holds no filings for this docket. If the reply persuasively rehabilitates the split (for instance with post-BIO Fifth or Sixth Circuit authority), I am too low.
- The call for response is the signal I weigh least confidently. If the Court's practice of requesting responses after waivers is broader than I assume, the signal is weaker and 0.11 is slightly high; if it reliably marks a Justice's interest, 0.11 is low.
- Retrieval was light: one corpus priors query (a check of recent granted SCOTUS rows, none topically similar), one CourtListener opinion search confirming the Fourth Circuit decision is published, and two CourtListener docket lookups confirming the docket is open with no entries beyond the snapshot. I did not find and do not know this petition's disposition; the conference is September 28, 2026, after today.
