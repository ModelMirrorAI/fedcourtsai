# Evaluation — codex-baseline, cell scotus/73369988 / evt-petition-disposition

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
| reasoning_quality | 0.88 |

**Base rate.** The prediction's frozen context carries `band: baseline` **and**
`salience_version: sal-v4`, and the statpack's "Segment base rate by salience band
(sal-v4)" heading matches, so the basis is `risk_set`: the bracketed `reached`
baseline figure pooled resolved-weighted over Terms strictly before the case's
docket Term 2025. The rendered rows are OT2017–OT2024 (5.7%/1271, 5.9%/1312,
5.8%/1192, 5.6%/1500, 4.5%/1739, 4.6%/1399, 4.6%/1524, 4.7%/1643), pooling to
0.0512 over a weighted n of 11,580. The caption renders 10 of 10 Terms, so the
rendered window is the pack's window and there is no lookback divergence to flag.
Skill: 1 − 0.0001 / 0.0512² = 0.962.

**What the prediction got right.** The disposition, no further distribution, no
CVSG, no separate writing, and a probability far under the band anchor. The
forecast document (read for context only, not scored) correctly placed the denial
in the orders following the September 28 conference.

**Reasoning quality (0.88).** A careful, well-bounded rationale. It states its
information boundary precisely (snapshot vintage, what was and was not
provisioned, that petitioner's account of the opinion below is unverified), builds
the correct anchor (sal-v4 bracketed reached rate pooled over OT2017–OT2024, ≈5.12%
over a weighted 11,580, with the rounding caveat), and explicitly declines to use
the terminal zero-relist bucket as a forward hazard, which is the right call and
one the weakest candidate got wrong. The downward conditioning rests on the same
real signals the record supports: no developed conflict on a rule that would change
this judgment; the alternative-analysis vehicle obstacle (the Court of Appeal
assumed the federal manifest-disregard standard and found no violation);
unpublished, record-dependent decision; waiver, no response request, no amici, no
CVSG. The one outside lookup, Justice White's *Commonwealth Coatings* concurrence,
is used for a legitimate doctrinal point (the disclosure rule distinguishes
substantial dealings from trivial relationships, so the QP's categorical framing
overstates the precedent) and is disclosed as the only additional text used.
Deductions: the rationale is more careful about what it does not know than
decisive about why the probability is 1% rather than 0.5% or 2%, so the final
number is less well-motivated than the structure around it; and the state-action
difficulty with the due-process theory, a clean reason QP 3 goes nowhere, is not
mentioned. Minor, and neither bears on the conclusion.

**Leakage.** Mode `forward`; `retrieved_outcome_material` false;
`influenced_prediction` not_applicable; `leakage_suspected` false. The log is
captured at ~0.97 coverage; the one `unobserved` row is a hosted web search whose
two queries (Rule 10 generally; the *Commonwealth Coatings* concurrence) name
neither this case nor its docket, so graded on query it is clean, and the
candidate's own `retrieval.md` reports it returned nothing usable. The five
CourtListener calls locate and read a 1968 opinion. Nothing retrieved concerns this
petition's disposition; the prediction predates the resolution by eighteen days
and the rationale states it did not inspect the live docket.

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
