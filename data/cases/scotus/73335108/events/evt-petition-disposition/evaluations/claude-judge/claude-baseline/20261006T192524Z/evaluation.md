# Evaluation: claude-baseline — Watson v. Mason, No. 25-1279 (scotus/73335108), evt-petition-disposition

## Outcome and scores

Cert-stage cell. The petition was **denied** on 2026-10-05 at its first conference (one distribution, no relist, no CVSG, no noted dissent). The candidate predicted `denied` with P(grant) = 0.005.

| field | value | basis |
| --- | --- | --- |
| `correct` | 1 | `denied` == `denied` |
| `brier_score` | 0.000025 | (0.005 − 0)² |
| `segment_base_rate` | 0.0512 | `risk_set`; see below |
| `brier_skill_score` | 0.9905 | 1 − 0.000025 / 0.0512² |
| `reasoning_quality` | 0.90 | see below |

**Base rate.** The prediction's frozen context carries `band: baseline` **and** `salience_version: sal-v4`, matching the heading of the statpack's "Segment base rate by salience band (sal-v4)" table, so the basis is `risk_set`. Pooling the bracketed `reached` baseline figure, resolved-weighted, over the rendered Terms strictly before Term 2025 (2017–2024) gives n = 11,580 and ≈ 0.0512. The caption renders 10 of 10 Terms, so the rendered window is the pack's window; the configured ten-Term lookback reaches further back than the pack holds, so the in-code pool is bounded to the same eight Terms. No window divergence to flag.

## Leakage

Forward cell, graded from the harness-captured log (26 calls, capture coverage 1.0, every result observed). The prediction was created 2026-09-16; the denial came 2026-10-05. Beyond record and statpack reads, the log shows: one corpus `query` for recent denied SCOTUS rows (unrelated to this case; `retrieved_doc_date` 2026-09-10), a CourtListener opinion search for the Seventh Circuit caption (0 results), a SCOTUS docket search for 25-1279 (0 results), the docket item for 73335108 (`date_terminated` null, `date_modified` 2026-06-17) and its docket entries (0 results). The docket lookup is a live check that nothing had been filed since the snapshot, which forward mode permits and which the reasoning discloses in its own "where to discount me" section. No post-resolution date, no disposing order, no `data/qp-topics/` read. `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`. No mis-provisioning.

## What the reasoning got right

- **The anchor is the contract's**: the bracketed `reached` figure for `baseline` pooled over Terms 2017–2024, with the Term rows tabulated, the case's own Term excluded, and the resulting ≈ 5.1% named as "the yardstick the evaluator will score this cell against". The arithmetic has a slip in the denominator (it says 11,680; the table sums to 11,580) that does not change the rounded rate.
- **The doctrinal analysis is the sharpest of the three and it is correct on each point.** Lockett and Eddings govern capital sentencing and have nothing to say about a guilt-phase instruction; Patterson v. New York and Martin v. Ohio leave the allocation of the self-defense burden to the States, which defeats the petition's asserted "split" on its own terms; the Mullaney/Winship strand is correctly isolated as the one serious theory, and its weakness (the state courts held the defense legally unavailable on Count 1 as a matter of state law) is correctly identified. Estelle is read the right way round.
- **The posture discounts are the right ones**: COA denial in an unpublished order; the Court's habeas grants run overwhelmingly on the State's petition; the State's waiver on a paid docket with no call for a response is a meaningful negative because the Court routinely calls for a response when any Justice wants one; the long-conference distribution carries no signal.
- **Record detail is used, not just recited**: the caption names the prior warden; the petitioner is self-represented but not an inmate-ID filing; the QPs are internally inconsistent about whether the jury was told to consider self-defense on Count 1 or failed to. It names where the account may be wrong (no appendix, so the Count 1 instruction's actual wording is the petitioner's description) and says which way that would cut.
- **It verified the docket was unchanged** as of prediction day and said so, which is good forward practice.

## Where it falls short

- The reasoning asserts the Court "grants almost no petitions from COA denials" and that the relist cut "counts reschedules" without pointing at the statpack rows or any source for either, so two load-bearing empirical premises rest on the author's word. Both are plausible, and the statpack has no COA-specific slice to cite, but the reasoning does not mark them as unsourced.
- The denominator slip noted above is small but it is an arithmetic error in the one number the contract says will be scored.
- `confidence: 0.9` is asserted without saying what it means for a 0.5% forecast.

`reasoning_quality` = 0.90: correct anchor and basis, the best-grounded and most accurate legal analysis of the three, honest about its own weak points, with a minor arithmetic slip and a couple of unsourced empirical premises.

## Big case

My independent read is 0.04, set from the record and the outcome before weighing the candidate's own score (which is visible in the staged `prediction.json` and could not be avoided; I fixed my number from the record first). Pro se, paid, non-capital state habeas petition from an unpublished COA denial on a Wisconsin-specific self-defense question, State waived, denied at first conference without writing.

## Not scored here

`vote_accuracy` is omitted (cert stage; no votes predicted). `claim_scores` is the harness's. No `semantic_grades` block on a cert event. The forecast document was read for context only and is unscored.
