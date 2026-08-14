# Evaluation — claude-baseline · scotus/73275185 · evt-petition-disposition

## Outcome and scoring axis

Cert-stage cell (petition kind, no stage recorded). `outcome.json`: `actual_disposition = "granted"`,
`actual_granted = 1`, resolved 2026-05-11. The prediction named `gvr` with P(grant) = 0.78.

- **correct = 0.** Exact label match on the disposition axis: `gvr` ≠ `granted`. As flagged in this
  run's `flags.json`, the docket's May 11 2026 order reads "Petition for writ of certiorari before
  judgment GRANTED. Judgment … VACATED and case REMANDED" — GVR text — while the outcome writer
  recorded `granted`. I score against `outcome.json` as recorded; if the label were corrected to
  `gvr`, this candidate's `correct` would flip to 1.
- **brier_score = 0.0484** ((0.78 − 1)²) — the best of the three, from the sharpest probability.
- **vote_accuracy** null — no votes predicted, with a stated (and sound) reason: a GVR is
  typically unsigned.
- **judgment_correct** null — not a merits cell.

## Base rate and skill

The staged prediction carries no frozen `context`, so per the fallback rule `base_rate_basis =
"terminal"`: band derived now is `state` (State-party petition; my cell's sal-v2 context confirms
it, matching the statpack table's sal-v2 heading — no version mismatch), scored against the
**leading** (terminal) figures. Pooling the `state` column resolved-weighted over Terms strictly
before 2025 (table renders 9 of 9 pack Terms, so 2017–2024 is the pack's own window): 38/249 ≈
**0.1526** (n = 249 weighted). `brier_skill_score = 1 − 0.0484/(0.1526 − 1)² ≈ 0.9326`.
Terminal-basis skill numbers are only comparable within the terminal basis.

## Reasoning quality — 0.85

The strongest of the three write-ups. It leads with a candid integrity note, then builds the case
properly from the pre-decision record: full procedural reconstruction (Milligan history, the 2023
plan, the May 2025 permanent injunction, briefing and the Nov 21 2025 distribution, the ~6-month
hold), the decisive both-sides signal (respondents joining the request for cert before judgment in
the alternative), the spring-2026 escalation read as evidence of a post-Callais landscape shift,
and a merits asymmetry point (QP1 weak for Alabama after Milligan; QP2 the real vehicle). It then
states an explicit conditional decomposition — P(framework change) ≈ 0.75–0.80 × P(grant | change)
≈ 0.95 plus a 0.15 no-change branch → 0.78 — anchored against statpack relist figures, with modal
disposition GVR for the right structural reason (held companion, not plenary review). Degradations
(sidecar unreachable, one-sided document set) are honestly logged. Debits are minor: the
conditional weights are stated rather than derived, and however disciplined the firewall, the
document's confidence cannot be fully separated from the known outcome — but that is priced in the
leakage grade, not here. As pure analysis given the pre-decision record, this is close to a model
answer.

## Leakage

`mode = forward`, but the cell was mis-provisioned: the 2026-07-17 snapshot contained the May 11
2026 disposition. Graded as a replay per the forward-branch rule: `retrieved_outcome_material =
true`; `influenced_prediction = likely` — the candidate admits knowing the outcome and predicted
exactly the leaked disposition at the highest confidence of the cohort. Its integrity handling was
exemplary (disclosure first, terminal entries excluded, no external retrieval on the case to avoid
compounding the leak), which counts for the cell — but demonstrable non-use is impossible here.
Advisory only; it never changes the scores above. Flagged in `flags.json`.

## Big case

My independent read: 0.8 — sequel to Allen v. Milligan, VRA §2 constitutionality, Alabama's
congressional delegation and 2026-midterm maps; the GVR transmits Callais's framework change.
