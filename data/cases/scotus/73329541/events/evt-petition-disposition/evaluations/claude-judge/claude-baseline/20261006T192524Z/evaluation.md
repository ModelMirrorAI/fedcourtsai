# Evaluation of claude-baseline — St. Clair v. Pettit, No. 25-1274 (cert stage)

## Outcome and scores

The petition was denied on October 5, 2026, after a single distribution for the September 28 long conference, with no response called for and no noted dissent. Cert cell; `outcome.actual_granted` = 0.

| Field | Value |
| --- | --- |
| predicted_disposition / actual | denied / denied → `correct` = 1 |
| probability | 0.015 |
| brier_score | 0.000225 |
| segment_base_rate | 0.0512 (`risk_set`) |
| brier_skill_score | 0.914 |
| reasoning_quality | 0.90 |

**Base rate.** The prediction froze `band: baseline` under `salience_version: sal-v4`, matching the statpack table's heading, so the basis is `risk_set`: the bracketed `reached` figure for `baseline` pooled resolved-weighted over OT2017–OT2024 (n = 11,580) is 5.12%. All ten Terms the pack holds are rendered, so no lookback divergence. `judgment_correct` null; `vote_accuracy` omitted (cert).

## What the reasoning got right

- **Anchor reproduced exactly.** Pooled the sal-v4 baseline reached rate over the eight rendered prior Terms with the per-Term n's stated, arriving at the same 5.1% this evaluation uses, and read the relist-0, CVSG-none and Tenth Circuit cuts for shape without mistaking them for forward hazards.
- **The decisive doctrinal point, stated first.** Section 2244(d)(1) reaches "an application for a writ of habeas corpus by a person in custody pursuant to the judgment of a State court"; the petitioner is serving Oklahoma sentences, so the limitations period applies however the petition is captioned, and the Seventh Circuit's Cox v. McBride line concerns administrative custody and would not obviously help him. It also read Bowe's syllabus and drew the right inference: Bowe's holdings concern 2244(b) for federal prisoners and its reasoning that section 2244's strictures aim at state prisoners cuts against this petition. This is the strongest single argument any candidate made, and the denial is consistent with it.
- **Vehicle verified against the lower-court record.** Retrieved the Tenth Circuit RECAP docket (COA termination, October 17, 2025) and the E.D. Okla. March 24, 2026 opinion, which records untimeliness under every trigger including (d)(1)(D) with no tolling. That both confirmed the threshold question was dispositive and showed the underlying custody claim had persuaded no court.
- **Docket signals read correctly.** One distribution, no response or waiver, no amici, non-specialist counsel, old split the Court has left alone since 2006.
- **Calibrated secondary claims and candid discounts.** The relist, CVSG, summary-route and dissent figures are each tied to a stated reason, and the "where to discount me" section names what it could not read.

## Where it falls short

- Landing at 1.5%, below the relist-0 bucket's 1.7% grant-family figure, is aggressive for a paid, counseled petition presenting a genuine statutory split. The outcome vindicated it, but the reasoning's own upward factors (paid, real split, outcome-determinative question) were given almost no weight, and a slightly less confident number would have been equally well supported.
- It describes the petition as fifteen pages where the provisioned manifest records 22; likely body pages versus PDF pages, immaterial to the number.
- The one corpus query it ran returned nothing usable, which it says honestly; the time was not wasted but the retrieval did not inform the forecast.

Reasoning quality 0.90: the most complete legal analysis in the cell, anchored exactly, verified against primary lower-court material, and right on the doctrinal point that decided whether Bowe could carry a GVR.

## Leakage

Forward cell. Prediction created September 16, 2026; event resolved October 5. The log (39 calls, capture coverage 1.0) includes one corpus query for recent SCOTUS grants (document date September 10, 2026, unrelated rows, unused) and 17 CourtListener calls. One of those searched for SCOTUS docket 25-1274 and returned zero results, captured, on September 16, before any disposition existed; the rest sought the Bowe opinion, the Cox line, and the petitioner's lower-court proceedings in the Tenth Circuit and E.D. Okla. All retrieved lower-court material predates the event and is legitimate forward signal. No document is dated at or after October 5, 2026, no query seeks this petition's disposition, and no `data/qp-topics/` path appears. `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Big case

My own read is 0.15, formed from the record and outcome: a real but old and shallow split, an unpublished COA denial, an idiosyncratic executive-agreement custody claim, and a first-list denial with no response and no writing. The predictors' scores sit in the staged `prediction.json`, so I had seen them before forming this; noted as a caveat.

Semantic grades: none (cert cell). `claim_scores`: harness-computed, not written here.
