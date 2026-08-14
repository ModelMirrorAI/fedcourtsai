# Evaluation — gemini-baseline · scotus/73275185 · evt-petition-disposition

## Outcome and scoring axis

Cert-stage cell (petition kind, no stage recorded). `outcome.json`: `actual_disposition = "granted"`,
`actual_granted = 1`, resolved 2026-05-11. The prediction named `gvr` with P(grant) = 0.65.

- **correct = 0.** Exact label match on the disposition axis: `gvr` ≠ `granted`, even though both
  are grants on the binary axis. Note the label tension flagged in this run's `flags.json`: the
  docket's May 11 2026 order reads "Petition for writ of certiorari before judgment GRANTED.
  Judgment … VACATED and case REMANDED" — textbook GVR text — while the outcome writer recorded
  `granted`. I score against `outcome.json` as recorded, per contract; if the outcome label were
  corrected to `gvr`, this candidate's `correct` would flip to 1.
- **brier_score = 0.1225** ((0.65 − 1)²). The least confident of the three candidates, which is
  mildly notable given its reasoning leaned hardest on the leaked timeline.
- **vote_accuracy** null — no per-Justice votes predicted (reasonable for a likely-unsigned GVR).
- **judgment_correct** null — not a merits cell.

## Base rate and skill

The staged prediction carries no frozen `context` (older record shape), so per the fallback rule
`base_rate_basis = "terminal"`: I derived the band the case ended at — `state` (a State-party
petition; my cell's context.json, provisioned from the decided docket, confirms `state` under
sal-v2, matching the statpack table's sal-v2 heading, so no version mismatch) — and used the
**leading** (terminal) figures, not the bracketed risk-set ones. Pooling the "Segment base rate by
salience band" table's `state` column resolved-weighted over Terms strictly before 2025 (the table
renders 9 of 9 pack Terms, so the rendered window 2017–2024 is the pack's own window; no
divergence): 38/249 ≈ **0.1526** (n = 249 weighted). `brier_skill_score = 1 − 0.1225/(0.1526 − 1)²
≈ 0.8294`. Terminal-basis skill numbers are only comparable within the terminal basis.

## Reasoning quality — 0.55

`reasoning.md` is coherent but thin. Credits: it states the correct Rule 11
certiorari-before-judgment standard; it correctly identifies the hold-for-the-lead-case pattern
and the GVR convention for held companions once the lead case (Louisiana v. Callais) resolved; it
disclosed the mis-provisioned snapshot honestly and up front. Debits: the analysis is short and
largely rides the leaked timeline — it verified Callais's decision date by live MCP search rather
than deriving the conditional structure from pre-decision signals; there is little engagement with
the record itself (the BIO's alternative request for cert before judgment, the relist/distribution
history, the spring-2026 escalation) and no explicit base-rate anchoring or conditional
decomposition behind the 0.65. Given the outcome, the mechanism it named (GVR in light of Callais)
is exactly right, but the document justifies its number more by assertion than analysis.

## Leakage

`mode = forward`, but the cell was mis-provisioned: the 2026-07-17 snapshot contained the May 11
2026 disposition. Graded as a replay per the forward-branch rule: `retrieved_outcome_material =
true` (snapshot read is in the log; the reasoning describes the disposing order), and
`influenced_prediction = likely` — the candidate admits knowing the outcome, and its modal call is
the leaked disposition. Its honest disclosure and its own data-quality flag count for the cell's
integrity, but the grade is descriptive. Advisory only; it segments and never changes the scores
above. Flagged in `flags.json`.

## Big case

My independent read: 0.8 — sequel to Allen v. Milligan, VRA §2 constitutionality, Alabama's
congressional delegation and 2026-midterm maps; the GVR transmits Callais's framework change.
