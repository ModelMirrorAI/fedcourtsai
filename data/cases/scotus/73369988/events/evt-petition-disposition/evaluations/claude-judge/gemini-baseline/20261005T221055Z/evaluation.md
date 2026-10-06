# Evaluation — gemini-baseline, cell scotus/73369988 / evt-petition-disposition

**Outcome.** Cert stage (`event.yaml` `stage: cert`, `moment: distribution`). The
petition in *Honeycutt v. JPMorgan Chase Bank, N.A.* (No. 25-1298) was **denied**
on the October 5, 2026 order list after the September 28 long conference, with one
distribution, no call for a response, no relist, and no noted dissent
(`outcome.json`: `actual_disposition` denied, `actual_granted` 0,
`noted_dissent_from_denial` false, `distribution_count` 1).

**Scores.**

| field | value |
| --- | --- |
| predicted_disposition / actual | denied / denied → `correct` 1 |
| probability | 0.01 |
| brier_score | 0.0001 |
| segment_base_rate | 0.0512 (`risk_set`) |
| brier_skill_score | 0.9619 |
| reasoning_quality | 0.50 |

**Base rate.** The prediction's frozen context carries `band: baseline` **and**
`salience_version: sal-v4`, and the statpack's "Segment base rate by salience band
(sal-v4)" heading matches, so the basis is `risk_set`: the bracketed `reached`
baseline figure pooled resolved-weighted over Terms strictly before the case's
docket Term 2025. The rendered rows are OT2017–OT2024 (5.7%/1271, 5.9%/1312,
5.8%/1192, 5.6%/1500, 4.5%/1739, 4.6%/1399, 4.6%/1524, 4.7%/1643), pooling to
0.0512 over a weighted n of 11,580. The caption renders 10 of 10 Terms, so the
rendered window is the pack's window and there is no lookback divergence to flag.
Skill: 1 − 0.0001 / 0.0512² = 0.962.

**What the prediction got right.** The disposition, the no-relist and no-CVSG
calls, the no-separate-writing call, and a probability well under the band anchor.

**Reasoning quality (0.50).** The rationale is one paragraph. Its direction is
right and its headline considerations are the real ones: first conference, waived
response, unpublished state-court decision on an arbitration standard of review,
no developed split. But the analysis is thin and in one place methodologically
off. It reads the correct anchor (the baseline band's reached rate, ~4.5–5.9%)
and then re-anchors on "the ~1.2% base rate for 0-relist petitions". That figure is
a **terminal** bucket, the grant rate among petitions that *ended* with zero
relists, and a petition awaiting its first conference has not yet ended anywhere;
every petition in the band was at zero relists at this point, so the bucket adds
no case-specific information and double-counts the base rate's own composition
(codex-baseline's rationale makes exactly this point correctly). The case-specific
work is also generic: it does not engage the questions presented individually,
does not notice that the lower court assumed the federal standard arguendo (the
vehicle problem that most cleanly explains the denial), and does not say what in
the petition it read. The conclusion is right for reasons that are right in
outline, but the document would read the same for most baseline-band petitions.
No `big_case_rationale` was given, which is not scored but leaves nothing to
assess there.

**Leakage.** Mode `forward`; `retrieved_outcome_material` false;
`influenced_prediction` not_applicable; `leakage_suspected` false. The log's
`result_capture_coverage` is 0.0 (every call `unobserved`), which is an engine's
standing telemetry shape, not a defect, so each call is graded on its query: reads
of the provisioned record, the statpack and schemas, one corpus query bounded with
`--decided-before 2026-09-16` and grepped for "arbitrat", and the output writes.
Nothing names this case's disposition or reaches past the prediction date; the
prediction predates the resolution by eighteen days.

**Big case (my own read, 0.05).** A private employment-arbitration dispute from an
unpublished California Court of Appeal opinion, waived response, no amici, denied
without writing; stakes end with the parties. I note for the record that the
predictors' `big_case_score` fields were visible in the staged `prediction.json`
when I dumped it, before I wrote this read; the read above rests on the docket,
the petition, and the outcome, not on those numbers.

**Not scored here.** `claim_scores` is the harness's. No merits set is declared,
so no `semantic_grades` block. `vote_accuracy` is omitted on a cert cell.
`process_version`, `prediction_run_id` and `base_rate_salience_version` are
stamped by the harness.
