# Evaluation — claude-baseline

**Cell:** cert stage, forward mode. Outcome: petition **denied** on 2026-10-05 at its first conference (one distribution, no relist, no CVSG, no noted dissent).

## Quantitative

- `predicted_disposition` = `denied` vs `actual_disposition` = `denied` → `correct` = 1.
- `probability` = 0.003, `actual_granted` = 0 → `brier_score` = 0.000009.
- `segment_base_rate` = 0.0501, basis `risk_set`: the prediction's frozen context carries `band: baseline` **and** `salience_version: sal-v4`, matching the statpack's sal-v4 band-table heading. Pooled bracketed `reached` figure for `baseline` over OT2017–OT2025, resolved-weighted by the bracketed `n` (12,720), ≈5.01%. The caption renders 10 of 10 Terms, so no lookback divergence.
- `brier_skill_score` = 1 − 0.000009 / 0.0501² ≈ 0.9964.
- No `vote_accuracy`, `judgment_correct`, or `semantic_grades`: cert cell. `claim_scores` is the harness's.

## Reasoning quality — 0.88

What `reasoning.md` does well:

- The anchor is exactly right and stated with its arithmetic: baseline band, bracketed `reached` rate, nine prior Terms, ≈5.0% (about 637 of 12,720). It names the version match (sal-v4) as the reason the table applies.
- Eight numbered downward adjustments, each tied to a specific source: pro se and a four-page argument; section 1257 finality while the nuisance action is pending; the BIO's quotation of the disqualification statement and writ petition showing only California statutory grounds were raised; the QP's "without any reasoned analysis" premise against the six-page trial-court order; adverse rulings as non-Caperton bias; the 170.3(c)(1) timeliness ruling as an independent state ground; the stay denied by a single Justice and then by the full Court without noted dissent; and the originating-court cut (CA Second District: granted 0.7%, GVR 4.6%, which matches the committed pack). The relist-0 bucket's 1.2% is also quoted correctly (that is the `granted` label alone; grant-family with GVR is 1.7%).
- It uses a legitimate forward signal the other candidates did not: on the 2026-10-04 snapshot the September 28 conference had passed with no relist posted, and a corpus query showed another same-conference petition already recorded as granted, so the grant orders had issued. It correctly confines that inference to the relist number and says it leaves the grant number essentially where the record puts it. It discloses the signal openly. The outcome bore out the inference precisely.
- The closing "Where to discount me" section names the two conditions under which its numbers would be wrong (a relist, a reply contesting preservation) and states that the BIO is its only source for what the disqualification statement said. That is good epistemic hygiene.

What holds it below the top of the range:

- A couple of load-bearing claims are asserted rather than sourced: "pro se paid petitions grant at a small fraction of the paid-segment rate" cites no cut, and "the Court will not take a federal question first raised in the petition for review" is stated categorically where the petition itself contests the preservation account and the candidate did not read the reply.
- The adjustments are presented as a list that "together" reaches 0.3%, with no account of their overlap (finality, preservation, and the independent-state-ground points are not independent). The number is defensible, but the path to it is less disciplined than the anchor.

## Big case

My own read is 0.03: a pro se, interlocutory recusal dispute arising from a city's short-term-rental enforcement action, no split, no amicus, no institutional petitioner, stay denied twice without dissent, denied at first conference without noted dissent. The predictor's 0.03 coincides with that read; I supply only my read, not an agreement number.

## Leakage

Forward mode, `not_applicable`. See `leakage.notes`. The one outside lookup was a corpus query for recent OT2026 rows; the candidate states none concerned this case, the log shows no query naming this docket, and the inference drawn (grant orders had issued) is public pre-resolution calendar information, which the contract classes as legitimate forward signal. `retrieved_outcome_material` = false; `leakage_suspected` = false.
