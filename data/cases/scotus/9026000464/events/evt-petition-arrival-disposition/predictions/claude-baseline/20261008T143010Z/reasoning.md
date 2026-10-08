# Rationale for the numbers

**P(any grant) = 0.008; predicted disposition: denied.**

## Anchor

`record/context.json` freezes `band: baseline` under `sal-v4`, `mode: forward`, `distribution_count: 0`, `cvsg_date: null`, `term: 2026`. The statpack's "Segment base rate by salience band (sal-v4)" table matches the context's salience version, so the band is a valid anchor. This is an arrival cell with a private petitioner (Hamp's Construction LLC; the federal government is the respondent, which does not place the petition in the `federal` caption band), so the arrival-population anchor is `baseline`'s bracketed `reached` rate pooled over the Term rows strictly before 2026. Pooling the 2017–2025 rows the table renders:

| Terms pooled | weighted n | pooled `reached` grant rate |
| --- | --: | --: |
| 2017–2025 | 12720 | 5.0% |

That 5.0% is the rate for all private paid petitions at docketing, including the ones that later climb to `elevated` or `high`. I did not use the relist-count cut's relist-0 figure (1.2%), which the prompt warns understates an arrival's future.

## Adjustments down from the anchor

Nearly every signal points well below the class floor:

- **No split is possible.** Contract Disputes Act appeals from the boards go exclusively to the Federal Circuit (41 U.S.C. § 7107(a)(1)(A)), so the petition cannot and does not allege a circuit conflict. It argues only that the Federal Circuit misapplied its own Type I framework. Rule 10 says that kind of error-correction petition is rarely granted.
- **Forfeiture and deference below.** I read the Federal Circuit opinion (CourtListener cluster 10882238, published, Lourie, Reyna, Cunningham, J., unanimous, no separate writing). Two of the three theories the questions presented rest on were held forfeited because they were not argued to the Board (the construction-traffic drawings, and the "absence of borings is itself an implied representation" theory), and the drawings were not even in the appendix. The remaining theory lost because a Board finding of fact (west-bank conditions were visibly different and worse) was supported by substantial evidence. A petition whose questions depend on forfeited arguments is a poor vehicle on its face.
- **Thin petition.** The provisioned `petition.txt` (19 pages, text extracted, not truncated) cites three cases, no amici, no treatises, and no decisions from other tribunals. Counsel is a small Dyersburg, Tennessee firm with no Supreme Court practice visible in the record. The "importance" argument is that FAR 52.236-2 is used widely, which is true but is not a reason the Court takes a case.
- **Government respondent.** The Solicitor General is respondent. For a petition this weak the SG will almost certainly waive, and a waived government-respondent petition on a fact-bound question is denied at its first conference nearly without exception.
- **No Supreme Court engagement with the doctrine.** A CourtListener search of SCOTUS opinions for the phrase "differing site conditions" returned nothing, so there is no body of Supreme Court law the petition could claim the Federal Circuit departed from.

I settle at 0.8%, about one sixth of the class floor. The residual mass is the generic chance of a GVR after a confession of error or an unforeseen intervening decision, plus my own model uncertainty; I do not see a realistic plenary-grant path.

## The other claims

- **relist-increment 0.95.** The record shows zero distributions, so this claim resolves true if the petition is ever distributed. Essentially every paid petition that is not dismissed or withdrawn before conference is distributed once. The complement covers a Rule 46 dismissal, a filing defect, or a settlement, each unlikely here.
- **cvsg-increment 0.002.** The SG is a party, so a CVSG cannot issue. I state a near-zero rather than zero only for model error.
- **summary-disposition-route 0.55** (conditional on a grant). The per-Term table shows GVRs at roughly half the grant family in the Terms where the split is readable (2017–2022, 2025). Case-specifically, the only grant route I can imagine is a GVR, so I set the conditional somewhat above the pooled share, while allowing that a hypothetical confession of error could also take a summary-reversal form.
- **dissent-from-denial 0.01** (conditional on a denial). Statements respecting denial are rare in general and essentially unheard of in routine government-contracts petitions with no constitutional or recurring-doctrine hook.
- **big_case_score 0.06.** A single contractor's $3.9M claim; the clause recurs across federal construction contracting, but the case would change nothing beyond the parties.

## Uncertainty and where to discount me

- The cell is well provisioned: snapshot dated 2026-10-08 read, `petition.txt` and `questions-presented.txt` both extracted (`empty_text: false`). No brief in opposition exists yet, so my read of the government's position is inferred from its appellate win, not from a BIO.
- The SCOTUS docket is not yet on CourtListener (docketed October 7, 2026), so I could not check for any post-docketing entry such as a waiver. That does not change the forecast.
- My main residual uncertainty is not about this petition but about the base rate of GVRs that follow SG confessions of error in government-respondent cases, which the statpack does not cut by respondent class. If that rate is higher than I think, 0.008 is slightly low; it would still be far below the 5.0% anchor.
- No corpus prior I pulled is topical (the `fedcourts query` surface has no originating-court or text filter), so the prior pull served only to confirm the corpus service was reachable; see `retrieval.md`.
- I know of no outcome for this case and found none; the petition was docketed the day before the snapshot.
