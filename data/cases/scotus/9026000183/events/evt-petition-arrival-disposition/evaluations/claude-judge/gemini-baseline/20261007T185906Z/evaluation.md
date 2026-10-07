# Evaluation: gemini-baseline — United Airlines v. Kincannon, No. 26-183 (arrival-moment cert cell)

## Outcome and the scored numbers

The petition was **denied** on 2026-10-05 after a single distribution (Conference of
9/28/2026), with Justice Kavanaugh noting he would grant. `actual_granted` = 0;
`noted_dissent_from_denial` = true.

- `correct` = 1: the candidate predicted `denied`.
- `brier_score` = (0.28 − 0)² = **0.0784**.
- `segment_base_rate`, `brier_skill_score`, `base_rate_basis`: **omitted / null.**
  The prediction froze `band: baseline` under `salience_version: sal-v3`. The
  committed `metrics/statpack.md` renders its "Segment base rate by salience band"
  table under **sal-v4**, so the table is no baseline for this band and the
  prompt's only answer to that mismatch is the omission, recorded in this run's
  `flags.json`. For the reader: the committed `statpack.json` still carries a
  sal-v3 block for OT2017–OT2025 whose baseline-band bracketed `reached` figures
  pool to about 5.0% over n ≈ 12,720, and the harness's own version-pinned
  pooling may resolve a rate from it at the stamp; that is the harness's number,
  not one I may write here.
- `vote_accuracy`: omitted (cert stage; the prediction carries no votes anyway).
- `judgment_correct`: null (no judgment on either side). No `semantic_grades`
  (cert cell; `semantic_claims` is null).

## Leakage

Forward cell, graded as such and not rubber-stamped. The prediction was created
2026-08-16; the event resolved 2026-10-05. The captured log has every result
`unobserved` (coverage 0.0), so each call is graded on its query: provisioned
reads, one `fedcourts query` on a class-action topic, and two web searches — the
case caption with "class certification" and the Detwiler companion. Both
searches ran seven weeks before the order; nothing could have returned this
petition's disposition, and the reasoning reads the zero-distribution arrival
state rather than any order. `retrieved_outcome_material` = false,
`influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Reasoning quality: 0.42

What is sound: the direction. The candidate anchors on the baseline band, names
the real upward signals (former Solicitor General as counsel of record, a
published Fifth Circuit opinion with a separate writing, the petition's
asserted multi-circuit split, the Detwiler hold request opening a GVR path), and
holds the number well under even odds because the Court might prefer Detwiler
as the vehicle or avoid the vaccine-mandate context. The expectation of amicus
support was borne out (two business amici filed).

What drags the score down:

- **The anchor is a single Term, not the pooled prior-Term rate.** The rationale
  quotes "approximately 5.4% (Term 2025 anchor)" where the contract pools every
  rendered Term strictly before OT2026. One Term's row is the noisiest cut
  available and the choice is not explained.
- **The counter-case is missing.** Nothing on the abuse-of-discretion standard
  that governs certification review, the interlocutory Rule 23(f) posture (the
  district court can still amend the order), or that the brief in opposition
  had not yet been filed — the three considerations that most plausibly explain
  a first-conference denial. The downward adjustment is one sentence of
  speculation about the Court's preferences rather than vehicle analysis.
- **Petitioner's framing is taken at face value.** The Fifth Circuit "explicitly
  conflicts with" Speerly is the petition's claim restated; the candidate does
  not ask whether the split is an application split (which the opposition
  argued, and which denials at this stage usually reflect).
- **The Detwiler path is priced as if the companion petition were pending.**
  The petition itself says that petition was *due* 2026-08-13 under extension
  No. 25A1336, so on the prediction date no cert petition existed; the
  rationale treats "if Detwiler is granted" as a live route without saying how
  uncertain its predicate was.

Net: a short, directionally reasonable rationale that lands at 0.28 — the
highest of the three and the furthest from the realized outcome — by stacking
grant signals without weighing the vehicle problems. The number was not
unreasonable for an arrival cell, but the document does not earn it.

## Stakes read

`big_case.evaluator_score` = 0.35, formed from the record before weighing the
candidate's own score (its score sits in the staged `prediction.json`, so I
read the file but set my number from the docket, the petition, the opposition,
and the order). Moderate stakes: a doctrinal Rule 23 question with business
amicus interest and a Justice noting he would grant, against an interlocutory,
fact-bound certification order denied at its first conference.

## Claims and forecast document

Not scored here: the `claims` block is the harness's (`cert` set), and
`predicted_reasoning.md` was read only for context on how the number was
formed. Observed for the record only: that document forecast at least two
relists; the petition was distributed once and denied.
