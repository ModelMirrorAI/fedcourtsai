# Evaluation — claude-baseline, cell scotus/73369988 / evt-petition-disposition

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
| probability | 0.006 |
| brier_score | 0.000036 |
| segment_base_rate | 0.0512 (`risk_set`) |
| brier_skill_score | 0.9863 |
| reasoning_quality | 0.90 |

**Base rate.** The prediction's frozen context carries `band: baseline` **and**
`salience_version: sal-v4`, and the statpack's "Segment base rate by salience band
(sal-v4)" heading matches, so the basis is `risk_set`: the bracketed `reached`
baseline figure pooled resolved-weighted over Terms strictly before the case's
docket Term 2025. The rendered rows are OT2017–OT2024 (5.7%/1271, 5.9%/1312,
5.8%/1192, 5.6%/1500, 4.5%/1739, 4.6%/1399, 4.6%/1524, 4.7%/1643), pooling to
0.0512 over a weighted n of 11,580. The caption renders 10 of 10 Terms, so the
rendered window is the pack's window and there is no lookback divergence to flag.
Skill: 1 − 0.000036 / 0.0512² = 0.986.

**What the prediction got right.** Everything on the scored axis: denial, no
further distribution, no CVSG, no separate writing, and a probability well below
the band anchor that the outcome vindicated. The forecast document (read for
context only, not scored) called the exact shape of the disposition, down to the
October 5 order list.

**Reasoning quality (0.90).** The rationale is the most complete of the three. It
builds the correct anchor (the sal-v4 bracketed reached rate pooled over
OT2017–OT2024, ≈5.1%), and then conditions down on case-specific signals that are
each real and each legitimately available pre-decision: no alleged split; the lead
question is not outcome-determinative because the Court of Appeal assumed the
federal manifest-disregard standard arguendo and ruled against petitioner under it;
the due-process theory against a private arbitrator has an unaddressed
state-action problem; unpublished state intermediate-court origin; waived response
with no call for a response twelve days before conference; solo-practitioner
counsel and no amici; error-correction framing. It is candid about what it did not
read (the unpublished opinion below is not indexed) and states where to discount
it. The one actually certworthy issue buried in the petition (whether FAA §10
binds state courts post-*Hall Street*) is identified and correctly set aside as
not presented. Deductions: a few supporting assertions are stated more firmly than
the record supports (that the Second District's GVR share "is dominated by criminal
petitions swept in behind lead cases"; that the Court "essentially never" grants a
paid petition without first calling for a response), and the final step from the
≈5% anchor to 0.006 is a judgment call narrated rather than decomposed. Neither
affects the conclusion.

**Leakage.** Mode `forward`; `retrieved_outcome_material` false;
`influenced_prediction` not_applicable; `leakage_suspected` false. The log is fully
captured (coverage 1.0). Its one lookup touching this case is a CourtListener
docket read that returned no grant or denial and a last-modified date of
2026-07-01, i.e. it confirmed the case was still pending, which is exactly the
mis-provisioning check a forward cell should make. The corpus query was over 2020s
granted priors (document date 2025-02-11) for population shape, not case facts.
Nothing retrieved postdates the prediction, let alone the October 5 resolution.

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
