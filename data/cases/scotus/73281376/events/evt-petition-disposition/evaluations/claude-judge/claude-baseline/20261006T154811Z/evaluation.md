# Evaluation of claude-baseline — scotus/73281376, evt-petition-disposition

Davie County, North Carolina, et al. v. Swink (No. 25-1091). Cert stage (`event.yaml` records `stage: cert`,
`moment: distribution`). Outcome: petition **denied** on 2026-10-05 after the September 28 long conference,
`actual_granted` 0, no noted dissent from denial, two distributions. No `record/opinion/` slot is staged, which is
the ordinary state of a cert cell. Because the stage is cert there is no `vote_accuracy`, no `semantic_grades`
block, and `claim_scores` is the harness's.

## Quantitative read

| Field | Value | How |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` `denied` matches `actual_disposition` `denied` |
| `brier_score` | 0.0121 | (0.11 − 0)² |
| `segment_base_rate` | 0.172242 | elevated band, risk-set figure, Terms 2017–2024 pooled |
| `base_rate_basis` | `risk_set` | frozen `context.band` elevated under `context.salience_version` sal-v4 |
| `brier_skill_score` | 0.592144 | 1 − 0.0121 / 0.172242² |

The prediction's frozen context carries both `band: elevated` and `salience_version: sal-v4`, and the statpack's
"Segment base rate by salience band" heading names sal-v4, so the risk-set basis applies. I pooled the bracketed
`reached` figures for `elevated` over every rendered Term strictly before the case's Term 2025, resolved-weighted:
2017–2024, 484 weighted grants over 2,810 weighted resolved petitions, 0.1722 (from the unrounded
`prefix_est_grant_rate` and `prefix_weighted_resolved` fields in `metrics/statpack.json`; the rendered table rounds
to the same). The table renders 10 of 10 Terms, the 2026 row is empty and 2025 is the case's own Term, so the
rendered window and the configured ten-Term lookback select the same eight Terms and there is no window divergence
to flag. The baseline forecaster's Brier is 0.0297.

## Reasoning quality: 0.8

Sharp cert-stage analysis with the right structure: anchor, then adjust, then say where to discount the author.

- **Anchor** correctly pooled and displayed Term by Term (484/2,810, about 17%), with the version match stated.
- **Vehicle analysis** is the best-organised in the cell: no court of appeals has acknowledged a split and the en
  banc petition did not claim one; the interlocutory posture, with the case proceeding against the provider
  regardless; and the party-presentation problem of a respondeat superior theory borrowed from the dissent at
  rehearing. Each maps onto a specific argument in the brief in opposition.
- **Two observations the others lacked**: no amicus brief on a question the petition says affects most US jails,
  and a caution that the `elevated` band may be reading a relist that did not happen if sal-v4 keys on
  `distribution_count`.
- **Honest uncertainty**: it named the call-for-response signal as the one it weighed least confidently and said
  which way each unknown would move the number.

Deductions: it relied on the brief in opposition's account of the Sixth and Fifth Circuit cases without checking
any of them (codex-baseline inspected one and found the brief's reading held), so its confidence that there is "no
acknowledged split" is borrowed rather than earned. Its statement that the Fourth Circuit "never invoked" a
non-delegable duty doctrine overstates: the phrase appears at App. 27a in the state-law malpractice discussion.
The underlying point, that the Monell holding did not rest on it, is correct and matches footnote 4 of the brief in
opposition, but the record was available to be quoted precisely. The characterisation of opposing counsel as "a
repeat Supreme Court shop" is a soft inference offered without support.

## Leakage

`leakage.mode` forward, `retrieved_outcome_material` false, `influenced_prediction` not_applicable,
`leakage_suspected` false. Log mode forward; 25 calls, result_capture_coverage 1.0. One corpus query for 2020s granted rows (a declared sanity check; 28 GETs, 7.3 MB reported). CourtListener: an opinion search for the Fourth Circuit decision (retrieved_doc_date 2025-11-20), a RECAP docket search for 25-1091 (zero results) and get_endpoint_item on dockets/73281376 (date_filed 2026-03-17, date_terminated null, date_modified 2026-07-24). The last is a lookup of this case's own docket, made 2026-09-17 while the petition was pending; it returned no disposition and is ordinary forward signal, which the candidate disclosed in retrieval.md and reasoning.md. No read under data/qp-topics/. Petition denied 2026-10-05; nothing in the prose presupposes it. Not applicable.

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
