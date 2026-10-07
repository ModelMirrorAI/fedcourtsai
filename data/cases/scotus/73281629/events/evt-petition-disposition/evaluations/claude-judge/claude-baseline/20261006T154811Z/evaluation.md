# Evaluation of `claude-baseline` — scotus/73281629 evt-petition-disposition

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
| probability | 0.14 |
| brier_score | (0.14 − 0)² = **0.0196** |
| segment_base_rate | 0.1722 (`risk_set`) |
| brier_skill_score | 1 − 0.0196 / 0.0297 = **+0.34** |
| reasoning_quality | **0.85** |

## What the prediction got right and wrong

The strongest analysis of the three, and the outcome bore out both its direction and its magnitude. It read the BIO in full and the petition body, pooled the anchor exactly as the contract prescribes (484.4 / 2,810 ≈ 17.2%, matching the in-code figure), and explained why the terminal figure was the wrong yardstick. It diagnosed the docket correctly: the two distributions are not a true relist because the April 15 distribution was superseded by the call for a response, and it then made the subtle and correct observation that the band nonetheless captures a real signal, the call for a response, so the anchor could stand rather than be discounted.

The adjustment section is balanced and specific. Upward: the Fourth Circuit's *Kelly v. Altria* (Aug 10 2026) widened the split and undercut the BIO's "no split" argument; it retrieved the Sept 2 reply, then verified the opinion text on CourtListener rather than taking the reply's characterization on trust, and noted the limit of the point (Kelly does not mention the Ninth Circuit). Downward: the unpublished, bench-trial, clear-error vehicle; zero amici against a claim of exceptional importance; low per-case stakes and the § 503 alternative route to claim-relevant documents; the Court's long tolerance of the disagreement; a solo-practitioner petition against an experienced opposition. It decomposed the grant pathway through a CVSG and landed slightly below the anchor at 0.14. A straight denial on the first order list after the long conference is exactly the modal path it described.

Weaknesses, all minor. The historical assertion that the Court "has let the Seventh/Ninth disagreement sit since 2009 and denied cert in *Hughes* (1996) and *Faircloth* (1997)" is stated without pointing to anything retrieved. The CFR conditional (~10%) is general knowledge rather than a statpack cut, which it disclosed. The pathway arithmetic (0.10 + 0.12 × 0.33) is illustrative rather than derived. None of these change the conclusion, and the uncertainty section names each of them honestly, including the truncated petition and the unread district-court findings. The score reflects soundness of analysis, not the volume of retrieval.

## Leakage

`mode` forward. Forward cell. 28 logged calls, result_capture_coverage 1.0. Case-specific retrieval: CourtListener dockets lookup for id 73281629 (retrieved_doc_date 2026-04-01; reasoning reports date_terminated null), docket-entries for the same docket (0 rows), and the petitioner's 2026-09-02 reply PDF fetched from supremecourt.gov: this case's own pre-decision filing, legitimate forward signal. Other retrieval was Kelly v. Altria (CA4, 2026-08-10, a different case) and generic corpus queries (doc date 2026-09-11). No material dated on/after the 2026-10-05 denial; reasoning states no outcome knowledge. Nothing outcome-revealing retrieved. `retrieved_outcome_material` false, `influenced_prediction` not_applicable, `leakage_suspected` false.

## Big case

My independent read: 0.25. Narrow ERISA document-disclosure question under 29 U.S.C. 1024(b)(4): whether claims-administration agreements are contracts 'under which the plan is operated'. A genuine inter-circuit disagreement matters to plan administrators and the benefits bar, but the per-case stakes are document access and a vacated $765 penalty, no amici appeared, the petition came from a solo practitioner against an unpublished Ninth Circuit memorandum, and the Court denied after a single conference with no noted dissent. Significant inside the ERISA bar, not beyond it. The staged prediction.json dumps showed the predictors' big_case_score before I wrote this; the read rests on the record and the outcome, not on them.
