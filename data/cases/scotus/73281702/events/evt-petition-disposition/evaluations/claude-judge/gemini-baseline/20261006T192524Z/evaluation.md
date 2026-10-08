# Evaluation of gemini-baseline — Trice v. Texas, No. 25-1195 (scotus/73281702), evt-petition-disposition

## Outcome and scores

The petition was **denied** on October 5, 2026, after the September 28 long conference, with no noted dissent (`outcome.json`: `actual_disposition` denied, `actual_granted` 0, `noted_dissent_from_denial` false, `distribution_count` 2). The event's stage is `cert`.

- `correct` = 1: the candidate predicted `denied`.
- `brier_score` = (0.05 − 0)² = **0.0025**.
- `segment_base_rate` = **0.1724**, basis `risk_set`. The prediction's frozen context carries band `elevated` under `sal-v4`, matching the heading of the statpack's "Segment base rate by salience band (sal-v4)" table, so the bracketed `reached` figure applies, pooled resolved-weighted over the rendered Terms strictly before the case's Term 2025 (OT2017–OT2024; the caption renders 10 of 10 Terms, so no window divergence needs flagging): 484.4 / 2810 = 0.1724.
- `brier_skill_score` = 1 − 0.0025 / 0.1724² = **0.92**.
- `vote_accuracy`, `judgment_correct`, `semantic_grades`: not written — cert cell.
- `claim_scores`, `process_version`, `base_rate_salience_version`: left to the harness.

## Reasoning quality: 0.55

The best score on this cell and the thinnest rationale, and `reasoning_quality` grades the second, not the first. What is here is directionally right: the petition alleges no split; the first distribution preceded the call for a response, so the long conference was effectively the first conference on full briefing; the CFR after Texas's waiver is the one signal of interest; the BIO frames the continuous course of conduct as the element. Those are the correct load-bearing points, and the candidate also named the right modal path (denial, with a possible relist for a dissent that did not materialize).

But the anchor was mis-read: the candidate took the single OT2024 figure (17.9 percent) rather than pooling the prior Terms the table renders, and then discounted it with the claim that the elevated rate "includes cases presenting deep circuit splits," which is an assertion about the band's composition the statpack does not support (a split would typically lift a petition into `high`, not sit inside `elevated`). The downward move from 17.9 to 5 percent is a 3.5-fold discount justified in two sentences. The log shows the petition was read by grepping for "split", "conflict", and "divide" and the BIO's first hundred lines, so Richardson, the Texas appellate opinion's facial-challenge framing, and the reply were not engaged. The three corpus queries failed on argument syntax and were not repaired. "Whether the Court is secretly building a vehicle to revisit Schad" is speculation offered as the main uncertainty. A one-paragraph rationale can be sound, but this one gets to a defensible number by a route a reader cannot check.

## Leakage: forward, not applicable

Mode `forward`. The prediction was created September 17, 2026 and the petition was decided October 5, 2026, so the case was genuinely open. The log's result capture coverage is 0.0 (every call `unobserved`), which is this engine's standing shape rather than a defect, so each call is graded on its query: provisioned record files, the statpack, three `fedcourts query` attempts the candidate reports as failed, and one CourtListener opinion search for `"continuous sexual abuse" unanimity`. No query names this docket, caption, or disposition; there is no web fetch; nothing touched `data/qp-topics/`. The candidate's `retrieval.md` says the CourtListener search returned Texas state opinions applying Schad, which I cannot confirm from the log but which is not outcome material either way. `retrieved_outcome_material` false, `influenced_prediction` not_applicable, `leakage_suspected` false.

## Big case

My independent read is 0.35 (see `evaluation.json`): a real post-Ramos question with reach beyond Texas, but a splitless petition with no amici, denied silently after one full-briefing conference.
