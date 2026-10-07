# Rationale for the numbers

**P(grant) = 0.18; predicted disposition `denied`.**

## Inputs read

- `record/snapshots/2026-10-06.json` (the provisioned baseline; `context.json` names `snapshot_date` 2026-10-06). Forward cell, cert stage, `moment: distribution`.
- `record/context.json`: `band: baseline` under `sal-v4`, `distribution_count: 1`, `cvsg_date: null`, `term: 2026`, `signals_observable: true`.
- `record/documents/petition.txt` (44 pages, text extracted) and `questions-presented.txt`. No brief in opposition exists yet: the United States waived on August 5, the Court called for a response on September 9, and the response is now due November 9, 2026 after a Clerk-granted extension.
- `metrics/statpack.md`: the modern-cert disposition section, the relist and CVSG cuts, and the sal-v4 "Segment base rate by salience band" table.

## Anchor

The context's band is `baseline` under `sal-v4`, which matches the statpack table's version. Pooling the bracketed `reached` figure for `baseline` over the nine rendered Terms strictly before OT2026 (OT2017 to OT2025, the OT2026 row is empty) gives **5.0%** (weighted n = 12,720). That is the rate every private paid petition in this class faces from its first distribution, and it is the yardstick the evaluator scores this cell against.

## Adjustments up

1. **The Court called for a response after a waiver.** This is the single strongest signal on the record and one the salience band does not encode (the band keys on relists and a CVSG, and this petition has neither). A call for a response is an affirmative act of the Justices' chambers; historically the grant rate among paid petitions that draw one is several times the paid base rate, on the order of one in eight to one in ten rather than one in twenty.
2. **Eight cert-stage amicus briefs**, including two United States Senators (Lee and Paul), the Cato Institute with NFIB, the Goldwater Institute, the Manhattan Institute, the American Center for Law and Justice, Judicial Watch, former federal forfeiture prosecutors, and law-and-economics scholars. Cert-stage amicus support is a well-documented grant predictor, and this volume is unusual for a private petition.
3. **Subject-matter receptivity.** The Court has taken forfeiture cases recently (*Timbs*, *Culley*), and the *Culley* separate writings from Justices Gorsuch, Thomas, and Sotomayor signal appetite on at least five Justices' part for forfeiture-abuse questions. The petition's textual hook (*Hardt* v. *Reliance Standard*, and *Lackey v. Stinnie* from OT2024) is strong, and the Court recently granted *Lackey* on a neighbouring "prevailing party" question.
4. **Clean vehicle.** Pure question of law, preserved below, full recovery of the res, and by the Court's conference the limitations period for refiling will have run, which answers the "not enduring" objection the Second Circuit relied on. The petition itself distinguishes *Salgado v. United States*, No. 19-659 (OT2019), an earlier petition on this question that drew a call for a response and did not produce a grant; the petition's own account of it shows the Court's interest in the issue is not new but that the prior vehicle had problems this one lacks.

## Adjustments down

1. **No split on Question 1.** Four circuits by the petition's own count (the Second, Eighth, Eleventh, and a fourth it does not single out in the pages I read) uniformly read "substantially prevails" through *Buckhannon*. The petition frames the conflict as one with this Court's precedent rather than among the circuits, which is a weaker Rule 10 ground, and the Solicitor General's brief will press uniformity hard.
2. **Question 2's split is shallow:** Second and Eighth Circuits versus the Eleventh's conditional rule versus a *non-precedential* Ninth Circuit decision (*Ito*). The Court does not grant to resolve a split whose minority side is an unpublished disposition.
3. **The United States is the respondent and will oppose.** The Solicitor General's opposition carries more weight than a private respondent's, and the government can argue the FOIA-amendment contrast the Second Circuit relied on.
4. **Modest stakes per case.** A fee award in a single forfeiture matter; the Court may judge the practice better addressed by Congress or by district courts conditioning dismissals under Rule 41(a)(2).

Netting these, I move from the 5% anchor to **0.18**. The call for a response and the amicus weight each roughly double the base rate; the absence of a split on the lead question and the coming SG opposition take back part of that.

## Claims

- `disposition` 0.18 (equals `probability`).
- `relist-increment` 0.96. From one distribution, a further "DISTRIBUTED for Conference" entry is all but mechanical once the brief in opposition (due November 9) and reply arrive. The residual covers withdrawal, dismissal, or an unforeseen disposition without redistribution.
- `cvsg-increment` 0.01. The United States is the party respondent; a CVSG is not a device the Court uses when the government is already in the case.
- `summary-disposition-route` 0.05, conditional on a grant. No intervening decision exists to GVR in light of; the Second Circuit already addressed *Lackey*. The relist cut shows GVRs forming roughly 40% of the grant family at one relist, but those are cases with an intervening decision, which this is not.
- `dissent-from-denial` 0.22, conditional on a denial. Above the ordinary rate because forfeiture reliably draws separate writings and the amici have put the fee-evasion practice squarely before the Court.

## Degraded retrieval

The CourtListener MCP server returned HTTP 429 (daily rate limit exhausted, retry expected in about 54 minutes) on both lookups I attempted (the Second Circuit opinion below, and the *Salgado* docket). There is no REST fallback, so I did not retry and worked from the provisioned petition text, the snapshot, and the committed statpack. My reading of the Second Circuit's reasoning and of *Salgado* comes from the petition's account, which is advocacy; discount accordingly. One `fedcourts query` for recent granted SCOTUS priors returned no case on point (its ranking surfaced interim applications and unrelated grants), so it informed nothing beyond confirming the corpus has no close CAFRA fee analogue.

## Where to discount me

- I did not read the brief in opposition because it does not exist yet; the SG's arguments are my inference.
- The band `baseline` is correct under the salience scorer's own rules, but the call for a response is exactly the kind of signal the scorer does not see, so the gap between my number and the 5% anchor rests mostly on that one docket entry and on the amicus count.
- The CFR grant-rate figures above are from memory of published empirical work, not from a committed artifact in this repository; the statpack publishes no response-requested cut for cert petitions.
