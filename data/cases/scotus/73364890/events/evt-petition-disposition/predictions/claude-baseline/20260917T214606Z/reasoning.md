# Rationale for the numbers

**P(grant) = 0.005; predicted disposition: denied.**

## Anchor

Cert-stage cell, `moment: distribution` (the ordinary `evt-petition-disposition`), forward mode. `record/context.json` freezes `band: baseline` under `sal-v4`, `distribution_count: 1`, `cvsg_date: null`, `term: 2025`. The statpack's "Segment base rate by salience band (sal-v4)" table matches the context's salience version, so the band is a valid anchor. Pooling the `baseline` band's bracketed `reached` figures over the rendered Terms strictly before 2025 (Terms 2017 through 2024) gives roughly 593 grants over a weighted risk-set denominator of 11,580, about 5.1%. That is the yardstick the evaluator scores this cell against and my starting point.

## Adjustments down (large)

1. **The government waived its response** (June 16, 2026) and the petition was distributed a week later with no call for a response. On a private-petitioner-against-the-United-States docket, the SG's waiver is the single strongest observable signal that no Justice's chambers has flagged the case; grants without a response on file are extremely rare, because the Court almost always calls for one before granting.
2. **The QPs do not state a cert-worthy question.** QP 1 asks whether the Court "should address" a 1985 concurrence; QP 2 asks whether "plausible" is the right Rule 52(a) standard. Anderson v. City of Bessemer City held, as its holding rather than dictum, that clear-error review applies to documentary findings, and the courts of appeals uniformly follow it. The petition alleges no circuit split, no conflict with a decision of this Court, and no recurring problem beyond its own facts.
3. **Vehicle.** The Eleventh Circuit's decision is an unpublished per curiam (Rosenbaum, Newsom, Abudu) affirming bench-trial findings after a remand that the same court ordered. The Court's stated interest is the intent behind 1920s and 1940s dredge-spoil placement, an intensely fact-bound inquiry. The petition's argument section runs about four pages and cites a single case.
4. **Statute.** Section 1313(a) of the Submerged Lands Act is litigated rarely; the petition frames no interpretive question about it, only a standard-of-review complaint about how the findings under it were reviewed.

Together these put the petition well below the baseline band's pooled floor. The band's 5% reflects a population that includes petitions that will draw a call for a response, be relisted, or be GVR'd after an intervening decision; none of those channels is plausibly open here. I land at 0.5%, which I read as the residual for a surprise call for a response followed by a grant, or a mis-read of the record on my part.

## Adjustments up (small)

Petitioner's counsel is an experienced Supreme Court and appellate advocate, the petition is paid, and Eleventh Circuit petitions grant at about the modern-cert average in the originating-circuit cut. None of this moves me materially against the signals above.

## Other claims

- **relist-increment 0.14.** One distribution shown. The relist cut's share of paid scored petitions with at least one further distribution is about a quarter, but that count is an upper bound (it includes reschedules) and is concentrated in petitions with some signal of interest. For a waived, unpublished, no-split petition at the long conference I expect a first-conference denial; the residual is a call for a response, a reschedule of the long-conference batch, or a hold.
- **cvsg-increment 0.002.** The United States is the respondent, so a CVSG is structurally unavailable; the figure is a floor for docket-parse noise, not a belief about the Court.
- **summary-disposition-route 0.25 (conditional on grant).** No intervening decision, so no GVR hook, and the question is not one the Court would summarily reverse on. I set this below the population's cert-order share of grants but not near zero, since a grant here is itself so unlikely that a strange route is a real fraction of the ways it could happen.
- **dissent-from-denial 0.01 (conditional on denial).** No Justice has recently written about Anderson or documentary-evidence review; no amicus; the government did not respond.

## big_case_score 0.12

Stakes if decided: the Wisteria Island dispute has local salience in Key West and a long litigation history (three Eleventh Circuit decisions), and a ruling narrowing Anderson would matter to appellate practice generally. But the case as framed would produce at most a procedural standard-of-review holding, and the property at issue is one small island.

## Inputs used and uncertainties

- Snapshot `2026-09-16.json` (docketed May 19, 2026; waiver June 16; distributed June 24 for the September 28, 2026 conference). No amicus, no response, no call for a response.
- `documents/petition.txt` (178 pages, truncated; text extracted, not OCR) including the Eleventh Circuit's opinion in Appendix A, and `questions-presented.txt`. No brief in opposition exists because the government waived.
- `metrics/statpack.md`: the sal-v4 band table, the relist and CVSG cuts, the originating-circuit cut.
- One `fedcourts query` for recent SCOTUS priors (mostly stay applications; not informative for this petition) and one CourtListener docket lookup confirming the docket was not terminated and had no filings after the June 24 distribution.

Where to discount me: I have not seen any post-distribution docket activity, and the snapshot was polled September 15, 2026; a call for a response entered after that date would raise both the grant and relist numbers. The petition text was truncated, but the truncation falls inside the lower-court appendices, not the petition proper, so I do not think it hides anything material.
