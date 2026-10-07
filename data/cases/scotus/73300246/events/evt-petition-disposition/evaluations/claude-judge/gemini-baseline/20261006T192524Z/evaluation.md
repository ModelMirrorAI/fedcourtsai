# Evaluation of gemini-baseline — scotus/73300246, evt-petition-disposition

## Outcome and scoring

Cert cell (`event.yaml` stage `cert`). The petition in No. 25-1254, Harvey v. City of Reno, was distributed once (June 24 for the September 28, 2026 conference) and **denied on October 5, 2026** with no noted dissent and no CVSG (`outcome.json`: `actual_disposition: denied`, `actual_granted: 0`, `distribution_count: 1`).

- `predicted_disposition: denied` → **correct = 1**.
- `probability: 0.015` → **brier_score = 0.000225**.
- **segment_base_rate = 0.0512**, basis **`risk_set`**. The prediction's frozen context carries `band: baseline` with `salience_version: sal-v4`, matching the statpack's sal-v4 band table heading. Pooled bracketed `reached` figure for `baseline`, weighted by `n`, over the rendered Terms strictly before OT2025 (OT2017–OT2024): 5.12% over n = 11,580. The caption says "Most recent 10 of 10 Term(s)", so the rendered window is the pack's whole window; no divergence to flag.
- **brier_skill_score = 0.9142**.
- No `vote_accuracy` (cert stage). No `semantic_grades` (cert cell). `claim_scores` and `process_version` are the harness's.

## Reasoning quality: 0.50

The number landed well and the direction of every argument is right, but the rationale is thin and its base-rate handling is loose in two ways that matter for soundness:

- **The anchor is read off the wrong rows.** It quotes the `baseline` bracketed `reached` rate "of 3.9% for the 2025 Term (and ~5.7% historically)". The 3.9% is this case's own Term's row, which the table's own note says already contains the case and which the prompt directs predictors away from in favour of strictly-prior Terms; and 5.7% is simply OT2024's single row, not a pooled historical figure. The right pooled anchor (~5.1%) happens to sit between the two numbers quoted, so the error did not cost much here, but the method is not the leakage-safe one.
- **A terminal bucket is used as a forward hazard.** "The petition is currently at its first distribution (relist 0), which carries a low base rate of ~1.2% for paid petitions" reads the relist-count table's zero-relist row (I checked: `0 | … granted 1.2%`) as if it were the grant rate facing a petition that has so far been distributed once. That row is terminal: it contains only petitions that *ended* with zero relists, so by construction it excludes the petitions that were later relisted and granted. A petition at first distribution faces the band's risk-set rate, not the terminal zero-relist rate. The candidate then "adjusts slightly downwards" from a figure that was already the wrong population.
- **Vehicle analysis is correct but second-hand.** The three obstacles named — limitations bar, no state-law property interest, disputed landlocked premise — are the BIO's headings, accurately restated, and they are the right reasons. But there is no engagement with the petition's own theory (the Tyler "state law cannot define away property" framing, or the accrual-at-the-2021-sale argument answering the limitations point), no mention of the unpublished state-court posture or the waiver pattern, and no account of why these defects dominate the Court's recent receptivity to takings petitions. The reader cannot tell from this document whether the candidate weighed anything the petitioner said.

What it does right: it correctly identifies the band, correctly reads that no CVSG is plausible with no federal party, and names genuine vehicle defects that in fact explain the denial. A sound bottom line reached by a partly unsound route.

## Leakage: not applicable (forward)

Mode is `forward` in both the log and the frozen context; the prediction was created 2026-09-16, before the conference and the denial. All 29 log rows are `unobserved` (coverage 0.0), which is this engine's standing telemetry shape and not a defect, so I graded the calls on their queries: every one is a read of the provisioned record, the prompt, or the statpack, or a write of the candidate's own outputs. No CourtListener, web, or corpus call; nothing names the disposition; no read of `data/qp-topics/`. `retrieval.md` reports no retrieval beyond the provisioned inputs and the statpack, consistent with the log. `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, `leakage_suspected = false`.

## Big case

My independent read is 0.10: a fact-bound, local access dispute from an unpublished state order, denied without comment. Formed before weighing the candidate's own score.
