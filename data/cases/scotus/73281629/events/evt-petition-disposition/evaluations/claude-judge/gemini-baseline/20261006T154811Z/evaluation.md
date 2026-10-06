# Evaluation of `gemini-baseline` — scotus/73281629 evt-petition-disposition

Evaluator `claude-judge`, run `20261006T154811Z`.

## Cell

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`), **forward** mode. *Zavislak v. Netflix*, No. 25-1142: petition from an unpublished Ninth Circuit memorandum on whether claims-administration agreements are contracts "under which the plan is established or operated" (29 U.S.C. § 1024(b)(4)). Docket: petition filed Mar 24 2026; Netflix waived Apr 7; distributed Apr 15 for the May 1 conference; response requested Apr 24; BIO Jun 25; distributed Jul 15 for the Sept 28 long conference; reply Sept 2; **petition DENIED Oct 5 2026**. `outcome.json`: `actual_disposition` `denied`, `actual_granted` 0, `noted_dissent_from_denial` false, `distribution_count` 2 (no relist beyond the two distributions, no CVSG).

## Base rate

The prediction's frozen context carries `band` `elevated` **and** `salience_version` `sal-v4`, and the statpack's "Segment base rate by salience band" heading names `sal-v4`, so the basis is `risk_set`. I pooled the bracketed `reached` figures for `elevated` over every rendered Term strictly before this case's Term 2025: OT2017–OT2024, eight Terms, weighted resolved n = 2,810. The table renders 10 of the pack's 10 Terms, so the rendered window is the pack's window; the in-code ten-Term lookback would reach back to OT2015 but the pack holds no Term before OT2017, so the two pools coincide and no window divergence needs flagging. Pooled rate **0.1722** (`fedcourtsai.pipeline.base_rates.prediction_base_rate` on the committed `statpack.json`, which the table's rounded percentages reproduce to within 0.0002). Baseline Brier (0.1722 − 0)² = 0.0297.

Under `sal-v4`, `elevated` is the one-relist tier read off the petition's own distribution count. On this docket the count is two because the April 15 distribution was superseded by the April 24 call for a response, so the petition had never actually been conferenced before Sept 28; the band therefore overstates the relist signal while, incidentally, capturing the call for a response. That is a fact about the anchor every candidate faced, and I score against the frozen band as the contract requires.

Not scored here: the `claims` block (harness, `fedcourtsai.pipeline.claims`), `predicted_reasoning.md` (read for context only), votes (none predicted; never scored on a cert cell), and no `semantic_grades` (no semantic set on a cert cell).

## Scores

| field | value |
| --- | --- |
| predicted_disposition / actual | denied / denied → `correct` 1 |
| probability | 0.28 |
| brier_score | (0.28 − 0)² = **0.0784** |
| segment_base_rate | 0.1722 (`risk_set`) |
| brier_skill_score | 1 − 0.0784 / 0.0297 = **−1.64** |
| reasoning_quality | **0.40** |

## What the prediction got right and wrong

Right label, but the number moved the wrong way from the anchor, and the baseline that merely parrots the band rate beats it by a wide margin. The reasoning anchors on the band table (quoting Term 2024's 17.9% rather than pooling prior Terms) and then adjusts "significantly upward" to 0.28 on two features: the petition's own description of an "acknowledged 1-9 circuit split", taken at face value, and the call for a response after Netflix's waiver.

The analysis is thin where the case was actually decided. It says it had "only the QP and the docket available to read in detail", yet the petition and the 28-page BIO were provisioned under `record/documents/`. It therefore never engaged the BIO's two central arguments, that the asserted nine-to-one split is mostly a difference in verbal formulation and that the vehicle is an unpublished, factbound memorandum reviewing bench-trial findings for clear error. Those were the reasons a denial-inclined Court had available, and the straight denial without relist or noted dissent is consistent with them. The call for a response is a real but modest signal; here it is treated as close to decisive.

Two docket readings are off. It describes the latest distribution as coming "after the BIO and reply were filed", but the July 15 distribution preceded the Sept 2 reply. And it treats the two distributions as a prior conference plus a relist ("cases emerging from the long conference that draw serious attention are often relisted"), without noticing that the first distribution was superseded by the call for a response, so the petition had not been considered at all before Sept 28.

Credit: it found the correct anchor table, named the right direction, kept the CVSG probability low for sensible reasons, and was candid that its main uncertainty was the unread BIO. That candour is the best thing in the document, but naming the gap is not the same as closing it when the material was in the record.

## Leakage

`mode` forward. Forward cell. 21 logged calls, result_capture_coverage 0.0 (every call unobserved: the engine's standing shape, graded on queries). Queries: prompt/AGENTS reads, this case's record (context, event.yaml, QP, 2026-09-15 snapshot), statpack greps, two generic `fedcourts query --court scotus --disposition granted` calls with no case filter, output writes, validate. No query names this case's disposition or any date on/after 2026-10-05; reasoning cites only pre-cutoff docket facts. Nothing outcome-revealing retrieved. `retrieved_outcome_material` false, `influenced_prediction` not_applicable, `leakage_suspected` false.

## Big case

My independent read: 0.25. Narrow ERISA document-disclosure question under 29 U.S.C. 1024(b)(4): whether claims-administration agreements are contracts 'under which the plan is operated'. A genuine inter-circuit disagreement matters to plan administrators and the benefits bar, but the per-case stakes are document access and a vacated $765 penalty, no amici appeared, the petition came from a solo practitioner against an unpublished Ninth Circuit memorandum, and the Court denied after a single conference with no noted dissent. Significant inside the ERISA bar, not beyond it. The staged prediction.json dumps showed the predictors' big_case_score before I wrote this; the read rests on the record and the outcome, not on them.
