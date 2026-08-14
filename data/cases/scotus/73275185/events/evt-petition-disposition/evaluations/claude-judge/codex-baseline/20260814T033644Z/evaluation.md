# Evaluation — codex-baseline · scotus/73275185 · evt-petition-disposition

## Outcome and scoring axis

Cert-stage cell (petition kind, no stage recorded). `outcome.json`: `actual_disposition = "granted"`,
`actual_granted = 1`, resolved 2026-05-11. The prediction named `gvr` with P(grant) = 0.74.

- **correct = 0.** Exact label match on the disposition axis: `gvr` ≠ `granted`. As flagged in this
  run's `flags.json`, the docket's May 11 2026 order reads "Petition for writ of certiorari before
  judgment GRANTED. Judgment … VACATED and case REMANDED" — GVR text — while the outcome writer
  recorded `granted`. I score against `outcome.json` as recorded; if the label were corrected to
  `gvr`, this candidate's `correct` would flip to 1.
- **brier_score = 0.0676** ((0.74 − 1)²).
- **vote_accuracy** null — no votes predicted, with a stated reason (no reliable justice-by-justice
  allocation without leaning on the leaked terminal entry).
- **judgment_correct** null — not a merits cell.

## Base rate and skill

The staged prediction carries no frozen `context`, so per the fallback rule `base_rate_basis =
"terminal"`: band derived now is `state` (State-party petition; my cell's sal-v2 context confirms
it, matching the statpack table's sal-v2 heading — no version mismatch), scored against the
**leading** (terminal) figures. Pooling the `state` column resolved-weighted over Terms strictly
before 2025 (table renders 9 of 9 pack Terms, so 2017–2024 is the pack's own window): 38/249 ≈
**0.1526** (n = 249 weighted). `brier_skill_score = 1 − 0.0676/(0.1526 − 1)² ≈ 0.9059`.
Terminal-basis skill numbers are only comparable within the terminal basis.

## Reasoning quality — 0.75

A solid, well-calibrated write-up. Credits: clean leakage disclosure up front, then a properly
firewalled analysis; correctly frames the weak ordinary case for cert before judgment (no
intervening circuit judgment, fact-heavy record, Milligan recently rejected similar attacks) before
weighing the grant-side signals (the long post-distribution hold, the BIO's alternative request
that the cases travel together, the expedite motion, the called-for stay response, the May 14
redistribution); anchors on the statpack honestly (3.1% modern overall, 5.4% 2025-Term paid, 4.4%
Eleventh Circuit) and — a nice touch of discipline — declines to assign a relist count the docket
does not state; picks GVR as the modal grant-side form for the right reason (a clarifying ruling in
the related case rather than plenary review of a fact-bound record). Debits relative to the best of
the cohort: no explicit conditional decomposition behind the 0.74, and less engagement with the
substance of the questions presented and the merits asymmetry; the step from a ~5% segment prior to
74% is justified qualitatively rather than quantitatively.

## Leakage

`mode = forward`, but the cell was mis-provisioned: the 2026-07-17 snapshot contained the May 11
2026 disposition. Graded as a replay per the forward-branch rule: `retrieved_outcome_material =
true`; `influenced_prediction = likely` — the candidate admits knowing the outcome and predicted
exactly the leaked disposition. Its disclosure and restraint (no external retrieval on the case
after the leak surfaced) count for the cell's integrity, but demonstrable non-use is impossible.
Advisory only; it never changes the scores above. Flagged in `flags.json`.

## Big case

My independent read: 0.8 — sequel to Allen v. Milligan, VRA §2 constitutionality, Alabama's
congressional delegation and 2026-midterm maps; the GVR transmits Callais's framework change.
