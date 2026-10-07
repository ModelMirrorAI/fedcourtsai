# Evaluation of gemini-baseline — St. Clair v. Pettit, No. 25-1274 (cert stage)

## Outcome and scores

The petition was denied on October 5, 2026, after a single distribution for the September 28 long conference, with no response called for and no noted dissent. Cert cell; `outcome.actual_granted` = 0.

| Field | Value |
| --- | --- |
| predicted_disposition / actual | denied / denied → `correct` = 1 |
| probability | 0.15 |
| brier_score | 0.0225 |
| segment_base_rate | 0.0512 (`risk_set`) |
| brier_skill_score | −7.58 |
| reasoning_quality | 0.40 |

**Base rate.** The prediction froze `band: baseline` under `salience_version: sal-v4`, matching the statpack table's heading, so the basis is `risk_set`: the bracketed `reached` figure for `baseline` pooled resolved-weighted over OT2017–OT2024 (n = 11,580) is 5.12%. All ten Terms the pack holds are rendered, so no lookback divergence. `judgment_correct` null; `vote_accuracy` omitted (cert).

## What the reasoning got right

- Named the right anchor (about 5.2% for a baseline paid petition) and the right disposition.
- Noticed the two docket facts that cut against a grant: the Tenth Circuit denied rehearing a month after Bowe, so the court below plausibly had Bowe in front of it; and no brief in opposition had been filed, so a plenary grant would need a call for a response first.
- Identified the real crux ("whether the Court will view Bowe's 2255 analysis as applicable to 2241 state-prisoner petitions").

## Where it falls short

- **The upward move is unsupported by the analysis.** It triples the anchor to 0.15 on a "clean circuit split" and a "very recent Supreme Court decision," but never examines either. The split is two decades old and the Court has passed on it for the whole period; the reasoning does not ask why this vehicle would be different.
- **The Bowe-GVR theory is asserted, not tested.** Bowe construed section 2244(b)(1) and (b)(3)(E) as applied to federal prisoners' section 2255 motions. It says nothing about the section 2244(d)(1) limitations period or section 2241, and its reasoning that section 2244's strictures target state prisoners cuts against this petitioner. A GVR "in light of" a decision that does not bear on the provision at issue is not a classic GVR vehicle; one search confirming Bowe exists did not check what it held. This same unexamined premise drives the 0.6 summary-route figure.
- **No vehicle analysis.** The decision below is an unpublished COA denial; the custody claim rests on an executive agreement no court found colorable; the petitioner is in custody under a state judgment so 2244(d)(1) applies on its own terms regardless of the 2241 label. None of this is engaged, and each point was readable from the provisioned petition.
- **Thin on its face.** One paragraph, one retrieval call, no stated pooling of the band table, and the hedging facts it does notice are not weighed against the tripled number in any traceable way.

The number was wrong in direction and the reasoning offered no sound basis for it; the parts it got right (the anchor, the rehearing-after-Bowe observation, the missing BIO) are what keep this above the floor. Reasoning quality 0.40.

## Leakage

Forward cell. Prediction created September 16, 2026; event resolved October 5. The log's `result_capture_coverage` is 0.0, the engine's standing shape, so every call is graded on its query: provisioned record and statpack reads, and a single CourtListener search for Bowe v. United States. No query names this petition's disposition or docket number, and no `data/qp-topics/` path appears. The reasoning treats the petition as pending. `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Big case

My own read is 0.15, formed from the record and outcome: a real but old and shallow split, an unpublished COA denial, an idiosyncratic custody claim, and a first-list denial with no response and no writing. The predictors' scores sit in the staged `prediction.json`, so I had seen them before forming this; noted as a caveat.

Semantic grades: none (cert cell). `claim_scores`: harness-computed, not written here.
