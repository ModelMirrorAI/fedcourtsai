# Evaluation of gemini-baseline — scotus/73281376, evt-petition-disposition

Davie County, North Carolina, et al. v. Swink (No. 25-1091). Cert stage (`event.yaml` records `stage: cert`,
`moment: distribution`). Outcome: petition **denied** on 2026-10-05 after the September 28 long conference,
`actual_granted` 0, no noted dissent from denial, two distributions. No `record/opinion/` slot is staged, which is
the ordinary state of a cert cell. Because the stage is cert there is no `vote_accuracy`, no `semantic_grades`
block, and `claim_scores` is the harness's.

## Quantitative read

| Field | Value | How |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` `denied` matches `actual_disposition` `denied` |
| `brier_score` | 0.1225 | (0.35 − 0)² |
| `segment_base_rate` | 0.172242 | elevated band, risk-set figure, Terms 2017–2024 pooled |
| `base_rate_basis` | `risk_set` | frozen `context.band` elevated under `context.salience_version` sal-v4 |
| `brier_skill_score` | -3.129124 | 1 − 0.1225 / 0.172242² |

The prediction's frozen context carries both `band: elevated` and `salience_version: sal-v4`, and the statpack's
"Segment base rate by salience band" heading names sal-v4, so the risk-set basis applies. I pooled the bracketed
`reached` figures for `elevated` over every rendered Term strictly before the case's Term 2025, resolved-weighted:
2017–2024, 484 weighted grants over 2,810 weighted resolved petitions, 0.1722 (from the unrounded
`prefix_est_grant_rate` and `prefix_weighted_resolved` fields in `metrics/statpack.json`; the rendered table rounds
to the same). The table renders 10 of 10 Terms, the 2026 row is empty and 2025 is the case's own Term, so the
rendered window and the configured ten-Term lookback select the same eight Terms and there is no window divergence
to flag. The baseline forecaster's Brier is 0.0297.

## Reasoning quality: 0.42

The analysis is brief and one-sided, and its central doctrinal premise misreads the record.

- **Anchor right, adjustment wrong.** It quoted an elevated reached rate of about 17.5%, close enough to the 17.2%
  pooled figure, then moved **up** to 0.35 on "the clarity of the split" and a "compelling vehicle." Both are the
  petition's framing taken at face value; the brief in opposition's three vehicle points (no acknowledged split,
  interlocutory posture, a respondeat superior theory first pressed on rehearing) are dismissed in a single clause
  as an attempt to call the decision "factbound."
- **The quoted holding is misattributed.** It states the Fourth Circuit "clearly invoked the nondelegable duty
  theory" and quotes App. 27a: "providing medical care to those incarcerated in county jails is a nondelegable duty
  of the county, and thus, any independent contractor hired to perform that duty is an agent of the state as a matter
  of law." That sentence appears in the majority's discussion of the **state-law medical malpractice claim against
  the contractor**, citing North Carolina cases (Medley, Wilson); the Monell holding against the counties, at
  App. 23a–26a, rests on the contracts' delegation of final policymaking authority. The brief in opposition's footnote
  4 makes exactly this point. Treating the malpractice passage as the Monell ground is what turns the case into a
  "clean" vehicle for Question 1, and it is the petition's move, not the court's.
- **Omissions**: nothing on the interlocutory posture, the absence of any amicus brief, or the preservation
  problem; no engagement with whether the Sixth Circuit cases actually conflict.
- **What it got right**: it identified the issue correctly, read the call for response as a signal of attention,
  and understood that the second distribution was effectively the first full consideration. The CourtListener read
  of the decision below was a reasonable step.

Given a denial without noted dissent, 0.35 on this record was roughly double the anchor in the wrong direction, and
the reasoning offers no analysis that would have justified it against the brief in opposition. The predicted dissent
from denial and relist are claims the harness scores, not inputs to this number; I note only that the rationale
offered for them was the same petitioner-side framing.

## Leakage

`leakage.mode` forward, `retrieved_outcome_material` false, `influenced_prediction` not_applicable,
`leakage_suspected` false. Log mode forward; 38 calls, result_capture_coverage 0.0, so every marker-carrying call is unobserved: the engine's standing shape, graded on queries rather than credited as returning nothing. Calls are file reads of the prompt, AGENTS.md, context, the 2026-09-17 snapshot and record documents; shell greps over the petition, brief in opposition and statpack; one CourtListener search for the Fourth Circuit opinion in docket 21-2183 (the November 2025 decision below, pre-dating the petition) and four search_document queries inside it (policymaking, non-delegable, delegable, Monell). No query names this petition's disposition, no read under data/qp-topics/. Prediction created 2026-09-17; petition denied 2026-10-05. The prose cites nothing post-dating the snapshot. Forward retrieval of a genuinely pending case: not applicable.

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
