# Evaluation — codex-baseline, evt-petition-arrival-disposition (scotus/9026000369)

**Cell.** Cert stage, arrival moment: *Loop v. Washington*, No. 26-369. Outcome: petition **denied** on 2026-11-16 after one distribution (conference of 11/13/2026), all respondents having waived; no CVSG, no noted dissent.

**Scores.** Predicted `denied` at P(grant) = 0.012 → `correct` = 1, `brier_score` = 0.000144. No `vote_accuracy` (cert cell). The segment base rate, skill score and claim scores are the harness's to stamp; any comparison is against the stamped segment base rate. No semantic grades (cert cell, no declared set).

## Reasoning (`reasoning_quality` = 0.8)

The call (denied, P(grant) 0.012) was correct. The rationale is careful and sound: it identifies the right arrival-population anchor (private petitioner, baseline band, prior Terms only, explicitly excluding the current Term and the terminal relist-0 rate), and its downward adjustments are the right ones — an unpublished, case-specific application of a jurisdictional rule, a claimed conflict that is really misapplication since the petition's own circuit authorities support its rule, and QP2's dependence on first clearing jurisdiction. It verified the petition's account of T.M. against the opinion and drew the correct inference (no intervening rule that would prompt a GVR). It is scrupulous about what it did not have (appendix opinions, any opposition) and about treating the petition's facts as allegations. Compared with the strongest rationale in the cell it is somewhat less concrete on vehicle: it does not weigh the pro se filing explicitly as a factor, nor the respondents' immunity defences as alternative grounds, and it leaves about twice as much mass on a grant, with a 70% plenary share conditional on grant that sits oddly with an unpublished memorandum below. Those are differences of degree; the analysis held up.

## Predicted reasoning (`predicted_reasoning_quality` = 0.8)

Central claims: denial without writing; one distribution after the deadline or a waiver and no relist; November/December timing; no CVSG; no dissent or statement. All were borne out. The document is specific on the path but hedges where a sharper forecast committed: 'response deadline or a waiver' rather than calling the waivers, and a timing window stretched to early 2027. The conditional question-selection and route forecasts were never tested. Specific and borne out, with some hedging, so just above the 0.75 anchor.

Checked against: Docket (2026-11-16 snapshot): waivers Oct 2 and Oct 8, DISTRIBUTED Oct 28 for Conference of 11/13/2026, 'Petition DENIED' Nov 16.

## Leakage

Mode `forward`; `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. Forward cell, predicted 2026-09-27; event resolved 2026-11-16. Log (26 calls, coverage 0.92): shell reads of provisioned inputs and the statpack, two web-search rows whose queries (per the candidate's retrieval.md) targeted the T.M. and Skinner opinions on supremecourt.gov and neither named this petition, and a CourtListener read of T.M. (decided 2026-06-18, a different case). No call string names this docket or caption; no retrieved date on or after resolution; reasoning states no outcome material for this case was read.

## Big case (evaluator read 0.12)

Paid petition, pro se at filing, from an unpublished CA9 memorandum affirming a Rooker-Feldman dismissal of a section 1983 suit arising from a privately arbitrated parenting plan. QP2 (delegating parental-rights adjudication to a private arbitrator) has some national family-law reach in the abstract and drew five cert-stage amicus briefs plus a later counsel appearance, but it was never reached below; all respondents waived, the petition was distributed once and denied without a writing.
