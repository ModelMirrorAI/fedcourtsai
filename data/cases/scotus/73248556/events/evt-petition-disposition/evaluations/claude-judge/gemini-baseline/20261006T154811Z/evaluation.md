# Evaluation of gemini-baseline — scotus/73248556 evt-petition-disposition

## Outcome and cell

United States v. Hembree, No. 25-1219, a Solicitor General petition from the Fifth Circuit asking the Court to hold the case for United States v. Hemani (No. 24-1234) and then grant, vacate and remand. The petition was distributed once (July 15, 2026, for the September 28 long conference) and **denied on October 5, 2026** on the first order list of OT2026, with no noted dissent and no CVSG (`outcome.json`: `actual_disposition` denied, `actual_granted` 0, `distribution_count` 1, `noted_dissent_from_denial` false). Stage is cert (`event.yaml`).

## Baseline

The prediction froze `band` = `federal` under `salience_version` = `sal-v4`, and the statpack table heading is `(sal-v4)`, so the basis is `risk_set`. Pooling the bracketed `reached` figures for `federal` over the rendered Terms strictly before the case Term (OT2025): OT2017 through OT2024, weighted denominator 181, about 132 weighted grants, pooled rate **0.7295**. The table renders 10 of 10 Terms, so the rendered window is the whole pack and the configured ten-Term lookback is not truncated by rendering; the pack simply holds nothing before OT2017. OT2025 (52.4%, n=21) is the case's own Term and is excluded. Baseline Brier against a denial: (0.7295)^2 = 0.5322.

## Scores

- `correct` = 1: predicted `denied`, outcome `denied`.
- `brier_score` = (0.05 - 0)^2 = 0.0025.
- `brier_skill_score` = 1 - 0.0025 / 0.5322 = 0.9953.
- `reasoning_quality` = 0.60.

## What drove the reasoning grade

The rationale identifies the mechanism that actually decided the petition: the only relief sought was a hold for Hemani and a GVR, Hemani was decided against the government in June 2026 and expressly declined to reach 922(g)(1), so the hold is moot, and the Court had already denied identical government petitions (Mitchell, Doucet, Cockerham). The 0.05 call is well placed and the adjustment direction is correctly argued. Two weaknesses hold the grade down. First, the anchor is misread: the rationale quotes "~52%" as the prior-Term federal rate, which is the OT2025 row, the case's own Term, rather than the pooled prior-Term risk-set figure of about 73% that the prompt and the table caption both direct the predictor to; the error did not change the direction of the adjustment but it is the one quantitative step the anchoring rule asks for. Second, the analysis is thin: it takes the brief in opposition's characterization of Hemani and of the comparator denials entirely on trust, does not decompose the residual grant mass, and offers one sentence on the main uncertainty. It was right, and right for the right reason, but with less discipline than the record supported.

## Leakage

Forward mode. The log carries 32 calls, all unobserved (coverage 0.0, this engine's standing shape), so each is graded on its query: local reads of the provisioned snapshot, documents, context, prompt, schema and statpack, plus its own output writes. No external retrieval of any kind, no retrieved_doc_date, nothing naming this petition's disposition or `data/qp-topics/`. The prediction predates the October 5 denial by three weeks and reads the 9/28 conference as pending, so the case was genuinely open: `influenced_prediction` = `not_applicable`, `retrieved_outcome_material` = false, `leakage_suspected` = false.

## Big case

My own read is 0.4 (see `evaluation.json`): a nationally watched doctrinal question carried by a derivative, single-defendant hold-and-GVR petition. The predictor's score was visible in the staged `prediction.json` before this read was recorded; the read rests on the petition, the opposition and the outcome, not on that field. No agreement number is computed here.

## Not scored here

`claim_scores` is the harness's (cert-v claims scored in code). No votes are scored on a cert cell. No semantic set is declared on a cert cell, so no `semantic_grades` block is written. `predicted_reasoning.md` was read for context only and is not graded.
