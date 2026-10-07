# Evaluation: claude-baseline — scotus/73281694, evt-petition-disposition

**Stage:** cert (event.yaml `stage: cert`, moment `distribution`). **Outcome:** petition
DENIED on the October 5, 2026 order list after the September 28 long conference, with no
noted dissent (`noted_dissent_from_denial: false`), two distributions, no CVSG.

**Prediction:** `denied`, P(grant) = 0.25. **Correct:** 1. **Brier:** 0.0625.

## Base rate and skill

The prediction froze `band: elevated` under `salience_version: sal-v4`; the statpack's
segment table is headed sal-v4, so the basis is `risk_set`. Pooling the bracketed `reached`
figure resolved-weighted over Terms 2017–2024 (eight rendered rows, weighted n = 2,810)
gives `segment_base_rate` = 0.1724. The caption shows 10 of 10 Terms, so no lookback
divergence is owed. Baseline Brier against a denial is 0.0297, so `brier_skill_score` =
1 − 0.0625 / 0.0297 ≈ **−1.10**. The call was right, but a petition that ended in a silent
denial is one where the band rate alone would have scored better; the candidate paid for
sitting eight points above its own anchor. The candidate pooled the same anchor (about 17%
over the same eight rows) and said so.

## What drove `reasoning_quality` = 0.85

This is the strongest analysis of the three, and it is right for the right reason.

- **It found the crux and named it.** The rationale isolates the vehicle as the decisive
  issue — the April 2024 waiver ruling, the January 2025 footnote, the unexplained April 2025
  order, the Superior Court's Hunt Refining citation, the adequate-and-independent-state-ground
  and § 1257 finality problems — and predicts that "the pool memo will lead with this." The
  outcome (denial, no writing) is what that reading predicts. It read the BIO and the reply
  rather than the petition's gloss, and gave the reply's rebuttals (Rule 1028(f), Michigan v.
  Long, the merits-authority citation) fair weight without being carried by them.
- **It used comparators correctly.** The Lynn v. BNSF denial four months earlier, retrieved
  from the sibling docket, is the single most informative external fact available in forward
  mode, and it was used for the right inference (the Court was not straining to reach the
  question) with the right caveat (this case drew a call for a response, Lynn did not).
  Percolation alternatives (the Tenth Circuit Goodyear appeal, the North Carolina proceeding)
  were identified as reasons the Court could wait.
- **It read the docket signal honestly.** It recognised that the two distribution entries
  contain no true relist — the first was superseded by the call for a response — so the
  relist-1 bucket overstates momentum, and it said the band already priced the two entries.
- **Calibration and disclosure.** The anchor is computed correctly and the adjustments are
  listed up and down with their basis. It flagged that the call-for-response uplift rests on
  memory rather than a statpack cut, stated a band of 0.15–0.35, and said which direction it
  expected to be wrong in.

Why not higher: the net number still sat well above the anchor on a vehicle the rationale
itself called "dirty," and the dissent-from-denial expectation (a statement from the 2023
concurrence's author) did not materialise — the Court denied silently, which the Lynn
comparator had already signalled. A reading that trusted its own vehicle analysis more would
have landed nearer 0.15. That is a calibration quibble inside a sound analysis, not an
analytical error.

## Leakage

Mode `forward`, 21 calls, `result_capture_coverage` 1.0. Retrieval: two `fedcourts query`
calls (a citation lookup for 600 U.S. 122 that returned a coverage note, and a granted-2020s
list with `retrieved_doc_date` 2025-02-11, unrelated rows); a `curl` of this petition's own
July 14, 2026 reply brief; a `web-fetch` of the sibling docket No. 25-1046 (Lynn v. BNSF,
denied May 4, 2026 — a different petition, and pre-resolution context for this one); and two
CourtListener calls on the 2023 Mallory opinion (doc date 2023-06-27). Nothing is dated on
or after this event's resolution (2026-10-05), no query sought this petition's disposition,
and the reasoning states the September 28 conference had not yet occurred. The redacted path
segment in one shell call is the blinding removing a name, not outcome material. The case
was genuinely open at prediction time, so the forward default holds:
`retrieved_outcome_material: false`, `influenced_prediction: not_applicable`,
`leakage_suspected: false`.

## Big case

My independent stakes read is 0.6 (see `evaluation.json`): a nationally consequential
question in a vehicle the Court declined without a word. Reading the staged
`prediction.json` displayed the candidate's `big_case_score` before I had written mine down;
the read above is my own and was formed from the record and the outcome, but the sequence is
recorded here for honesty.

Nothing in `predicted_reasoning.md` or the `claims` block was scored; the harness scores the
claims in code.
