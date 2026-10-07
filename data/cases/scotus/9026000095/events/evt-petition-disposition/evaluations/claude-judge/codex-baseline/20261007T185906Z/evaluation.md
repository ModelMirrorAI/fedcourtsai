# Evaluation — codex-baseline

**Cell:** cert stage, forward mode. Outcome: petition **denied** on 2026-10-05 at its first conference (one distribution, no relist, no CVSG, no noted dissent).

## Quantitative

- `predicted_disposition` = `denied` vs `actual_disposition` = `denied` → `correct` = 1.
- `probability` = 0.006, `actual_granted` = 0 → `brier_score` = 0.000036.
- `segment_base_rate` = 0.0501, basis `risk_set`: the prediction's frozen context carries `band: baseline` **and** `salience_version: sal-v4`, and the statpack's "Segment base rate by salience band (sal-v4)" heading matches that version. I pooled the bracketed `reached` figure for `baseline` over the nine Term rows strictly before Term 2026 (OT2017–OT2025), resolved-weighted by the bracketed `n` (12,720), giving about 5.01%. The caption renders 10 of 10 Terms, so the rendered window is the pack's window and there is no lookback divergence to flag.
- `brier_skill_score` = 1 − 0.000036 / 0.0501² ≈ 0.9857.
- No `vote_accuracy`, `judgment_correct`, or `semantic_grades`: cert cell. `claim_scores` is the harness's.

## Reasoning quality — 0.85

What `reasoning.md` does well:

- Anchors on exactly the right figure: the baseline band's bracketed `reached` rate pooled over OT2017–OT2025, weighted by denominator (≈5.01%, n=12,720), and explicitly refuses the terminal-band and no-relist buckets as substitutes. Its secondary statpack citations (relist-0 grant-family 1.7%, relist-1 13.3%, CVSG 34.9% vs 6.3%) all match the committed pack.
- Correctly distinguishes the stay application (26A145, denied twice) from the cert event and gives the stay denials only slight corroborative weight.
- Works through each BIO vehicle objection — preservation, mismatch between the QP's "without any reasoned analysis" premise and the six-page trial-court order, section 1257 finality, and the adverse-rulings/Caperton fit — and, importantly, treats them as adversarial assertions it cannot verify from the provisioned files rather than as findings. It notes the overlap and declines to multiply "independent" rejection probabilities.
- Candid about its information set: notes the empty application text, the unprovisioned reply and supplemental briefs, and that it did not refresh corpus vintage. The outcome bore its analysis out on every axis it addressed (denial, no relist, no CVSG, no separate writing).

What holds it below the top of the range:

- The move from the ~5% anchor to 0.6% is argued qualitatively but not quantified against any cut; the residual is described rather than derived. That is acceptable for a cert cell, but the document is also long relative to its information content and spends several paragraphs on provenance caveats that do not move the number.
- It gives no weight to a legitimate forward signal that was available on the 2026-10-04 snapshot: the September 28 conference had passed with no relist entry posted. It explicitly declines to infer anything from that, which is conservative but leaves a real signal on the table.

## Big case

My own read is 0.03: a pro se, interlocutory recusal dispute arising from a city's short-term-rental enforcement action, no split, no amicus, no institutional petitioner, stay denied twice without dissent, denied at first conference without noted dissent. The predictor's 0.20 is on the high side relative to that read, driven by the abstract reach of a "reasoned recusal decision" rule rather than this record; I supply only my read, not an agreement number.

## Leakage

Forward mode, `not_applicable`. See `leakage.notes`: the log shows no retrieval of this case's outcome, no post-resolution document dates, and the two outside sources touched (Caperton; Rule 10) are decades-old general law. `retrieved_outcome_material` = false; `leakage_suspected` = false.
