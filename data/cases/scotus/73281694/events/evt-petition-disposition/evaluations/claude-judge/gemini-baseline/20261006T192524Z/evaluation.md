# Evaluation: gemini-baseline — scotus/73281694, evt-petition-disposition

**Stage:** cert (event.yaml `stage: cert`, moment `distribution`). **Outcome:** petition
DENIED on the October 5, 2026 order list after the September 28 long conference, with no
noted dissent (`noted_dissent_from_denial: false`), two distributions, no CVSG.

**Prediction:** `granted`, P(grant) = 0.82. **Correct:** 0. **Brier:** 0.6724.

## Base rate and skill

The prediction froze `band: elevated` under `salience_version: sal-v4`, and the statpack's
segment table heading names sal-v4, so the basis is `risk_set`. Pooling the elevated band's
bracketed `reached` figure resolved-weighted over every rendered Term strictly before the
case's Term (2025) — 2017 through 2024, eight rows, weighted n = 2,810 — gives
`segment_base_rate` = 0.1724. The caption shows 10 of 10 Terms, so the rendered window is the
pack's full window and no lookback divergence is owed. The naive baseline's Brier against a
denial is 0.0297; `brier_skill_score` = 1 − 0.6724 / 0.0297 ≈ **−21.62**. The forecast was
far worse than parroting the band rate.

## What drove `reasoning_quality` = 0.25

The rationale is a single paragraph that rests on one true and important fact — the 2023
Mallory majority reserved the Commerce Clause question and Justice Alito's concurrence
invited it — and the call for a response after a waiver. Both are real grant signals and both
were in the provisioned inputs. The problems:

- **It never engaged the vehicle.** The retrieval log shows the candidate read the snapshot,
  the questions presented, and the documents manifest, but not `petition.txt` or
  `brief-in-opposition.txt`. The BIO's leading arguments — an April 2024 waiver ruling, a
  January 2025 order footnote restating the waiver, an unexplained trial-court order, no
  Pennsylvania appellate opinion, contested § 1257 finality, no split — are exactly what a
  cert pool memo would lead with, and the rationale's one hedge ("a vehicle issue that isn't
  apparent on the docket") concedes the author did not look where the vehicle issue was
  plainly written. Its claim that "the summary rejection below suggests the constitutional
  question is cleanly presented" is the opposite of what the BIO shows: an unexplained order
  after a waiver finding is an adequate-and-independent-state-ground problem, not a clean
  presentation.
- **The adjustment from the anchor is unexplained in magnitude.** It names the band rate
  (about 18%, close to the correct 17%) and then moves to 0.82 "significantly" on the
  strength of the invitation alone, with no comparator. The sibling denial in Lynn v. BNSF
  (No. 25-1046, May 2026) was cited in the BIO and would have told it the Court had just
  declined the same question in a cleaner-looking railroad petition.
- **Calibration language mismatched the evidence.** "Practically tailor-made for a grant" and
  0.82 express near-certainty about a question the Court has denied repeatedly in weak
  vehicles. A reading that weighed the invitation against the vehicle would land well under
  0.5.

What it got right: the Court's interest in the question is real; the call for a response is a
genuine positive signal; the base-rate anchor was correctly located. The analysis is not
wrong on its own facts; it is incomplete in a way the provisioned record would have cured.

## Leakage

Mode `forward`. The log carries 27 calls, all `result_capture: unobserved` (coverage 0.0,
an engine's standing shape). Graded on the queries: in-tree file reads of the provisioned
inputs and statpack excerpts, then output writes and `validate`. No web, MCP or corpus call,
no `retrieved_doc_date`, no query reaching this petition's disposition, and the reasoning
treats the September 28 conference as pending. The case was genuinely open at prediction
time (created 2026-09-16; resolved 2026-10-05), so the forward default holds:
`retrieved_outcome_material: false`, `influenced_prediction: not_applicable`,
`leakage_suspected: false`.

## Big case

My independent stakes read is 0.6 (see `evaluation.json`): a nationally consequential
question in a vehicle the Court declined without a word. I note that reading the staged
`prediction.json` displayed the candidate's `big_case_score` before I had written mine down;
the read above is my own and was formed from the record and the outcome, but the sequence is
recorded here for honesty.

Nothing in `predicted_reasoning.md` or the `claims` block was scored; the harness scores the
claims in code.
