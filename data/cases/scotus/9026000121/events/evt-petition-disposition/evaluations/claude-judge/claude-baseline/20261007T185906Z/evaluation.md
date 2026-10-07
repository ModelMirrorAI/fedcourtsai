# Evaluation of claude-baseline — scotus/9026000121, evt-petition-disposition

**Cell.** Cert stage (`event.yaml` `stage: cert`, `moment: distribution`), Term
2026 by docket number (No. 26-121). Outcome: petition **denied** on
2026-10-05 after a single distribution for the September 28, 2026 conference,
with no noted dissent. Forward mode. No `record/opinion/` slot, the ordinary
state on a cert cell; no semantic set is declared here, so no `semantic_grades`
block is written.

**Scores.**

| Field | Value | How |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` `denied` matches `actual_disposition` `denied` |
| `brier_score` | 0.000036 | (0.006 − 0)² |
| `segment_base_rate` | 0.0501 | `baseline` band, bracketed `reached` figures, Terms 2017–2025 |
| `base_rate_basis` | `risk_set` | prediction froze `band: baseline` with `salience_version: sal-v4` |
| `brier_skill_score` | 0.9857 | 1 − 0.000036 / 0.0501² |
| `reasoning_quality` | 0.85 | below |
| `leakage_suspected` | false | forward cell, log clean (below) |

**Baseline.** The prediction's frozen context carries both `band: baseline` and
`salience_version: sal-v4`, and the committed `metrics/statpack.md` table is
headed *(sal-v4)*, so the version resolves and the risk-set basis applies.
Pooling the bracketed `reached` rate of the `baseline` column, weighted by its
bracketed `n`, over every rendered Term strictly before 2026 (2017 through
2025; the 2026 row is blank) gives 0.0501 over a weighted n of 12,720. The
caption says the table renders 10 of 10 Terms, so the rendered window is the
pack's whole window and the configured ten-Term lookback would reach the same
nine populated Terms; there is no window divergence to flag. The figure is
pooled from the table's rounded percentages, so it is approximate in the
fourth decimal; the harness's stamp recomputes from the unrounded pack.

**What the prediction got right.** The disposition, and it did so at a
probability (0.006) an order of magnitude under the band anchor it correctly
identified (about 5.0 percent). Against a denial that is a near-perfect Brier,
but the number deserves the credit only if the discount was earned, and here it
mostly was.

**Reasoning quality (0.85).** The rationale is anchored on the right table and
the right cut, states the pooled figure and its n, excludes the case's own
Term, and then lists reasons that stack toward denial, each one real and each
checkable against the provisioned record:

- The federal question was decided only by the intermediate Appellate Court of
  Maryland on an evidentiary ground (the LinkedIn post did not establish when
  the judge began practicing), and the Maryland Supreme Court dismissed under
  Rule 8-602 after granting review on a different fee question. The petition's
  own table of contents and appendix list confirm the per curiam Rule 8-602
  dismissal and the LinkedIn basis, so this is read off the record rather than
  invented.
- No conflict alleged; the petition itself frames Question 1 as one of first
  impression on "extreme facts."
- Question 2 asks for summary reversal in light of a July 2026 Maryland
  Supreme Court decision. The candidate's point that the Court does not GVR on
  a state court's intervening decision is correct practice and is the sharpest
  single observation among the three candidates.
- The response waiver, correctly read as both a signal and a procedural step a
  grant would have to pass through (a call for a response first).
- Vehicle quality: a one-page fee order whose timing against the judge's new
  employment is contested on the petition's own account.

The write-up is candid about its limits (the appendix exhibits it could not
read, the docket not yet indexed on CourtListener, a corpus query that returned
applications rather than comparable paid petitions). Two things keep it off
the top of the scale. The gloss that the statpack's "state-high-court buckets
in the originating-court cut show grant rates at or near zero" is loose: the
rendered state buckets show plain grants around 1 to 4 percent with some GVRs,
and Maryland's courts are not among the rendered rows, so the claim is
directionally fine but overstated as a reading of that table. And the
magnitude of the discount (5 percent to 0.6 percent) is argued qualitatively;
the factors are correlated with one another (state origin, no split, waiver,
and solo counsel largely describe the same population), so stacking them as
independent reasons risks double-counting, even though the direction is right.

**Leakage.** Forward cell; the log records `mode: forward` with full result
capture (27 of 27 calls captured). The three CourtListener calls are a docket
search for No. 26-121 that returned nothing, an opinion search on recusal
doctrine whose newest document is dated 2016, and a Maryland opinion search
for "Basso" whose result is the 2017 published decision. Two `fedcourts query`
corpus calls fetched priors by disposition filter, not this case. No document
date on or after the 2026-10-05 resolution, no query for this petition's
outcome, nothing under `data/qp-topics/`, and the rationale reads the five
pre-decision docket entries without presupposing the result. Not a
mis-provisioned decided case: the prediction's snapshot (2026-10-04) predates
the denial. `retrieved_outcome_material` false, `influenced_prediction`
`not_applicable`.

**Big case.** My own read is 0.05: a private Maryland fee dispute with a
Caperton hook whose dispositive fact is unresolved, denied silently on the
first conference. I note for the record that the predictors' `big_case_score`
values were visible in the staged `prediction.json` I had to read for the
probabilities, so the read is independent in substance but was not formed
strictly before seeing theirs.

**Not scored here.** The `claims` block and `predicted_reasoning.md` are the
harness's and were read only for context; `vote_accuracy` is omitted on a cert
cell by rule.
