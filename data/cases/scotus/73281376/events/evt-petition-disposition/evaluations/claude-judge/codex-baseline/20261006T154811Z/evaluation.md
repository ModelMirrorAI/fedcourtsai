# Evaluation of codex-baseline — scotus/73281376, evt-petition-disposition

Davie County, North Carolina, et al. v. Swink (No. 25-1091). Cert stage (`event.yaml` records `stage: cert`,
`moment: distribution`). Outcome: petition **denied** on 2026-10-05 after the September 28 long conference,
`actual_granted` 0, no noted dissent from denial, two distributions. No `record/opinion/` slot is staged, which is
the ordinary state of a cert cell. Because the stage is cert there is no `vote_accuracy`, no `semantic_grades`
block, and `claim_scores` is the harness's.

## Quantitative read

| Field | Value | How |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` `denied` matches `actual_disposition` `denied` |
| `brier_score` | 0.0144 | (0.12 − 0)² |
| `segment_base_rate` | 0.172242 | elevated band, risk-set figure, Terms 2017–2024 pooled |
| `base_rate_basis` | `risk_set` | frozen `context.band` elevated under `context.salience_version` sal-v4 |
| `brier_skill_score` | 0.514617 | 1 − 0.0144 / 0.172242² |

The prediction's frozen context carries both `band: elevated` and `salience_version: sal-v4`, and the statpack's
"Segment base rate by salience band" heading names sal-v4, so the risk-set basis applies. I pooled the bracketed
`reached` figures for `elevated` over every rendered Term strictly before the case's Term 2025, resolved-weighted:
2017–2024, 484 weighted grants over 2,810 weighted resolved petitions, 0.1722 (from the unrounded
`prefix_est_grant_rate` and `prefix_weighted_resolved` fields in `metrics/statpack.json`; the rendered table rounds
to the same). The table renders 10 of 10 Terms, the 2026 row is empty and 2025 is the case's own Term, so the
rendered window and the configured ten-Term lookback select the same eight Terms and there is no window divergence
to flag. The baseline forecaster's Brier is 0.0297.

## Reasoning quality: 0.82

The strongest verification discipline of the three. It anchored on the correct pooled risk-set figure (17.2%,
computed from the same unrounded fields I used), then moved below it for reasons that the outcome bears out and
that the record supports:

- **It tested the split rather than accepting either side's description.** It pulled Robinson v. Midland County
  (80 F.4th 704) from CourtListener and read footnote 4, finding the Fifth Circuit left the nondelegable-duty theory
  undecided. That is the one independent check of a disputed authority anywhere in this cell, and it correctly
  undercut the petition's "square Fifth Circuit holding."
- **It read the majority's Monell discussion itself** (App. 23a–26a) and characterised it accurately: contracts
  delegating authority, policy-or-custom and moving-force causation, a remand rather than a liability finding. That
  is the right frame; the brief in opposition's footnote 4 says the same thing about where the "nondelegable" language
  actually sits.
- **Vehicle analysis** covered the preservation objection, the interlocutory remand, and the fact that claims against
  the provider proceed regardless, each weighed rather than treated as dispositive.
- **It read `distribution_count: 2` correctly** as a response request superseding the first conference, not a relist,
  and said so.
- **Honest information-set accounting**: it named what it had not read (reply, provider's supporting brief, the
  dissent beyond the truncation boundary) and treated the petition's account of the dissent as advocacy.

Deductions: the document is hedge-heavy in places and spends words on provenance that do not move the analysis; the
observation that the response request is "genuine evidence of attention" is asserted without any sense of how
common a call for response after waivers is, which was the key uncertainty (claude-baseline at least flagged it as
such). The number itself sat sensibly below the anchor on a petition that was denied without a word.

## Leakage

`leakage.mode` forward, `retrieved_outcome_material` false, `influenced_prediction` not_applicable,
`leakage_suspected` false. Log mode forward; 33 calls, result_capture_coverage 0.94. The two unobserved rows are web-search queries naming the Cornell LII page for Praprotnik (485 U.S. 112) and Supreme Court Rule 10, graded on their queries: neither names this petition. CourtListener calls are a citation search for 80 F.4th 704 (Robinson v. Midland County, 2023) and reads of opinion 9839933; every other call is a shell read of the prompt, schemas, statpack and provisioned record documents. No lookup of this docket, no retrieved_doc_date on any call, no read under data/qp-topics/. Prediction created 2026-09-17; petition denied 2026-10-05; the 2026-09-17 snapshot carried no disposition. Nothing in reasoning.md, predicted_reasoning.md or retrieval.md presupposes the outcome; the candidate states it encountered none. Forward retrieval of a genuinely pending case: not applicable.

The prediction's frozen `context` carries `cutoff` null and `cut_kind` null, the ordinary forward shape; there
is no replay boundary to read.

## Big case

My own read is 0.35. Monell liability for a county's contracted jail medical provider: a recurring question that touches a widespread outsourcing model, with a published 2-1 Fourth Circuit opinion and a call for a response after both respondents waived. Against that: a doctrinal municipal-liability question on an interlocutory record (summary judgment reversed, remand for trial), no amicus support on the docket, and a denial on 2026-10-05 without any noted dissent or statement. Mid-low stakes for the cert docket. On the anchoring caveat: the
predictor's `big_case_score` sits inside the staged `prediction.json`, which I read for the probability and the
disposition before writing anything, so an unanchored read was not available to me on this staging; I formed the
number from the record documents and the outcome and did not compute any agreement figure.

## Not written, and why

`vote_accuracy`, `semantic_grades`, `claim_scores`, `process_version`, `base_rate_salience_version` and
`prediction_run_id` are omitted: the first two are merits-only, the rest are the harness's. `flags.json` is not
written for this cell because nothing needs a maintainer's attention: the salience version matched, the rendered
Term window matched the configured lookback, the cell was genuinely forward, and no candidate retrieved outcome
material.
