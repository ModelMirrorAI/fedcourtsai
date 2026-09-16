# Why 0.022

## Inputs read

- Snapshot `record/snapshots/2026-09-15.json` (the file `context.json` names). Paid docket 25-1192 from the Third Circuit (unpublished, non-precedential panel opinion of November 10, 2025; rehearing denied January 14, 2026). Petition filed April 14, 2026; two extension grants; two briefs in opposition filed June 17, 2026 (the federal respondent's and the Newspaper Guild's); distributed July 1 for the September 28, 2026 conference; petitioner's reply filed July 2. No amicus brief. No CVSG.
- `record/context.json`: mode `forward`, `band` = `baseline` under `sal-v4`, `distribution_count` = 1, `cvsg_date` null, `term` 2025, `signals_observable` true.
- Provisioned documents (`documents.json`): `questions-presented.txt`, `petition.txt` (41 pp, full text), and `brief-in-opposition.txt`, which is the **Guild's** brief (36 pp). None had `empty_text`.
- Not provisioned but on the docket: the **federal respondent's** brief in opposition. I fetched it from the supremecourt.gov URL in the snapshot and extracted its text (details in `retrieval.md` and `flags.json`). This is a forward cell, so that retrieval is ordinary forward-mode use of the case's own filings.
- `metrics/statpack.md`: the modern-cert disposition section, the relist and CVSG cuts, and the per-Term salience-band table (sal-v4).
- Corpus priors via `fedcourts query` (see `retrieval.md`).

## Anchor

The context's band is `baseline` and the statpack's band table is computed under the same `sal-v4`, so the anchor is the `baseline` bracketed `reached` rate pooled over Terms strictly before OT2025. Pooling the eight rendered prior Terms (OT2017–OT2024) by their `n`:

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

Weighted pool ≈ 593 / 11580 ≈ **5.1%**. That is the rate for a private paid petition that has reached `baseline`, and it is what the evaluator will score this cell against. For context, the relist-count cut's relist-0 bucket grants 1.2% and the CVSG-none bucket 4.0%; the Third Circuit's modern-cert grant rate is 1.5% (gvr 0.9%).

## Adjustments from 5.1% down to 2.2%

Downward, and substantially:

1. **The Solicitor General opposes and concedes no split.** The government's brief argues the Third Circuit's rule (bad faith may be inferred where the cumulative proposals leave employees worse off than no contract) is shared by the Seventh, Tenth, Eleventh, and D.C. Circuits, and that the D.C. Circuit's District Hospital decision, which the panel relied on, is on the same side. Having read the petition's own authorities, I think the SG has the better of it: the D.C. and Ninth Circuit cases the petition cites say proposals alone warrant caution, not that they are legally insufficient, and none rejected a Board finding on facts like these. A petitioner-drawn split that the SG credibly dissolves is the ordinary shape of a denial.
2. **Independent alternative ground.** Both BIOs press the Board's footnote finding that no valid impasse existed "even absent" bad faith (parties had unexchanged movement; the company implemented terms better than its "final" offer). After the May 2026 sale of the paper, only make-whole liability for the unilateral changes remains, and that remedy rests on the impasse finding regardless of QP 1. The petition addresses this only glancingly. The Court rarely takes a case where the challenged holding would not change the judgment.
3. **QP 2 is weak.** The panel reviewed a factual finding for substantial evidence and stated plenary review of legal questions; the petition's Loper Bright argument is really a complaint about the word "deferential." The SG also cites Urias-Orellana v. Bondi (2026) for the proposition that Loper Bright does not touch statutorily mandated deferential review of facts.
4. **QP 3 is forfeited and the Court just passed on the clean vehicle.** The Third Circuit held the Thryv challenge unpreserved under Section 10(e); the Third Circuit itself already invalidated Thryv in Starbucks, so this circuit is not on the Board's side of that split; and on June 15, 2026 the Court denied Macy's v. NLRB (No. 25-627), a Ninth Circuit case where Thryv was preserved and decided on the merits, even though the government asked for a GVR so the reconstituted Board could revisit Thryv. Here the SG expressly declines to request a remand. The petition's own fallback ask was a hold for Macy's, which is now gone.
5. **Vehicle and signal negatives.** Unpublished, non-precedential opinion below; no amicus support for a business-side labor petition (the Chamber and allied groups typically file where they see a live vehicle); stakes reduced to backpay by the sale; the Court denied this petitioner's stay application (No. 25A725) on January 7, 2026 without noted dissent per the petition, which is weak evidence that no Justice saw the merits as compelling. Recent employer-side NLRB petitions in the corpus (Cemex, denied July 2026; NP Red Rock, denied September 2026) fit the same pattern.

Upward, modestly:

- The petition is well drafted and counsel of record is an experienced appellate advocate; the SG's filing of a full BIO rather than a waiver means the government took it seriously (though as a party respondent, the NLRB rarely waives).
- The Thryv question is genuinely live and has Seventh Amendment resonance after Jarkesy; a hold-then-GVR path exists if the Court grants another Thryv vehicle this Term. I weight this as most of the remaining 2.2%.

Net: about 0.4× the anchor. I would not go below ~1.5% because hold-and-GVR paths on the Thryv issue are real, and not above ~3.5% given the SG's no-split position and the alternative ground.

## The other claims

- **relist-increment 0.27.** State forecast from: one distribution (the July 1 entry for the 9/28 conference), zero relists. The statpack's terminal buckets say roughly a quarter of paid scored petitions ever pick up a second distribution (relist-0 holds 10408 of ~13900). Long-conference petitions are rescheduled somewhat more often than the average, and two BIOs plus three QPs give a Justice something to look at, so I sit slightly above the marginal rate. Most of that mass is one extra distribution, not a run.
- **cvsg-increment 0.003.** The federal government is already a party and has filed. A CVSG is practically impossible; I leave a sliver for a clerical or procedural oddity.
- **summary-disposition-route 0.5** (conditional on a grant). The grant paths are split between a plenary grant on QP 1 and a hold-then-GVR on the Thryv question if another vehicle is granted. The statpack's grant family runs 30–59% GVR by Term; the conditional here is about even.
- **dissent-from-denial 0.04.** The Court passed on Macy's; this vehicle is worse. A short statement respecting denial on the Thryv question is conceivable but not expected.

## Big case score

0.35. If the Court actually decided the Thryv or Loper-Bright-for-the-NLRB questions the case would be significant to labor law nationally; but the realistic decided shape is a narrow bad-faith-inference ruling on a fact-bound record from an unpublished opinion, and the paper's sale reduces the practical stakes to one bargaining unit's backpay.

## Uncertainties and where to discount me

- I have not seen the Third Circuit opinion itself, only the parties' characterizations of it. If the panel's language really does announce a per-se rule (proposals alone always suffice), QP 1 is stronger than I have credited.
- I do not know whether any Justice dissented from the Macy's denial; if one did, my dissent-from-denial number is too low and the relist number a little low.
- The relist-increment number is the least anchored: the statpack buckets by terminal count, and no as-at-prediction hazard is published.
- The SG BIO was fetched by me, not provisioned; the other predictors in this fan-out may not have read it, which is a difference in information set worth knowing when comparing cells.
