# Evaluation of `codex-baseline` — scotus/73281629 evt-petition-disposition

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
| probability | 0.16 |
| brier_score | (0.16 − 0)² = **0.0256** |
| segment_base_rate | 0.1722 (`risk_set`) |
| brier_skill_score | 1 − 0.0256 / 0.0297 = **+0.14** |
| reasoning_quality | **0.75** |

## What the prediction got right and wrong

Sound and disciplined. It took the exact risk-set anchor from `statpack.json` (17.2242% over OT2017–OT2024), explicitly retained the frozen band rather than recomputing it, and correctly read the docket: two distribution entries do not establish two conferences, since the Court requested a response before the first scheduled conference, and redistribution after a BIO is less diagnostic than repeated consideration of a fully briefed petition. It used the relist and CVSG cuts as population-shape checks rather than stacking them as independent predictors, which is the right discipline.

On the merits of certworthiness it read the QP, substantive portions of the petition and BIO, and the Ninth Circuit memorandum reproduced in the appendix. It identified the vehicle problems (unpublished decision applying en banc circuit precedent to document-specific findings after a bench-trial procedure) and the panel's own distinction between provider-relationship contracts and benefit terms, while treating the BIO's distinctions of *Mondry* and *Premera* as the respondent's arguments rather than established holdings, and the petition's "nine-circuit conflict" as advocacy. That even-handedness is good practice. The net 0.16, a modest step below the anchor, was borne out by the straight denial.

Weaknesses. The adjustment is under-argued relative to the material marshalled: the document lists considerations on both sides but says little about why they net to about one point below the anchor rather than more, so the number reads as anchor-plus-caution. Some prose is abstract ("permit the Court to view this as an application dispute") where a concrete statement would be stronger. It did not obtain the Sept 2 reply and so missed the *Kelly v. Altria* development, though it disclosed the failed attempts and refused to infer the reply's content, which is the right response to a gap. Its freshness note (pack last changed Sept 14, no live corpus check) is careful and accurate.

## Leakage

`mode` forward. Forward cell. 28 logged calls, result_capture_coverage 0.96. One unobserved web-search row whose query is the URL of this case's 2026-09-02 reply PDF (a pre-decision filing; graded on its query, and the candidate reports it returned nothing), plus a failed shell curl of the same URL. Remaining calls read the record, statpack.md/json, prompts, schemas, and wrote output. No CourtListener or corpus calls. No query reaches past the 2026-10-05 denial; reasoning states no outcome knowledge. Nothing outcome-revealing retrieved. `retrieved_outcome_material` false, `influenced_prediction` not_applicable, `leakage_suspected` false.

## Big case

My independent read: 0.25. Narrow ERISA document-disclosure question under 29 U.S.C. 1024(b)(4): whether claims-administration agreements are contracts 'under which the plan is operated'. A genuine inter-circuit disagreement matters to plan administrators and the benefits bar, but the per-case stakes are document access and a vacated $765 penalty, no amici appeared, the petition came from a solo practitioner against an unpublished Ninth Circuit memorandum, and the Court denied after a single conference with no noted dissent. Significant inside the ERISA bar, not beyond it. The staged prediction.json dumps showed the predictors' big_case_score before I wrote this; the read rests on the record and the outcome, not on them.
