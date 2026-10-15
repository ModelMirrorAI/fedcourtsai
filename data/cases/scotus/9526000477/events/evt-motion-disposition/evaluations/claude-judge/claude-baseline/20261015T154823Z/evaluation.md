# Evaluation — claude-baseline

## Cell

- **Stage: interim.** Stay application 26A477, which asked the Court to stay a Fourth Circuit mandamus order that set a deadline for the FCC to decide. Outcome (`outcome.json`): `denied`, `actual_granted` 0, resolved 2026-10-14. The committed record shows the Court denied the application **as moot** in a per curiam; Justices Sotomayor and Jackson would have denied it outright.
- `correct` and `brier_score` below are my independent reading. The harness recomputes both at the stamp. **The interim baseline and skill are the harness's** (`stamp-cell` pools the substantive slice over prior application-Terms). I wrote neither, and I left `base_rate_basis` null. The prediction froze no band (`band: null`), which is the normal interim shape, so no flag.
- `vote_accuracy` is omitted because this is not a merits cell. There is no `semantic_grades` block because no semantic set is declared on an interim cell. `claim_scores` belong to the harness.
- **Leakage: forward.** The prediction ran under an arrival-position cut (anchor index 0, cutoff 2026-10-09). It was written on 2026-10-14, the day the order issued. Its log shows no retrieval of the disposition, so it is graded `not_applicable`. See the cell-level `flags.json` note on same-day minting.

## Scores

P(grant) 0.72, predicted `granted`. Actual `denied` (as moot). correct = 0, Brier = 0.5184.

## Reasoning quality: 0.60

The candidate starts from the 53/549 ≈ 9.7% interim pool. It makes a large, explicitly argued adjustment. The main reasons are the Court's earlier stay in the same dispute (26A274), the aligned federal respondent, and Purcell proximity. All of these are sound reads of the application.

Its strongest feature is the discount list. The first discount it names is **mootness**: the FCC controls its own timing and could decide the application for review itself, producing a withdrawal or dismissal that scores as ungranted. That is almost exactly how the event resolved. The candidate also notes that partial relief reads as denial, and that an order compelling a *decision* is less disruptive than a vacatur. It admits it could not see the respondents' side.

Given that analysis, 0.72 still puts too little weight on the mootness path. A mandamus deadline of noon on Oct 9 for an agency that already had a proposed order circulating made a moot-out the modal resolution. The candidate identified the mechanism but did not price it. Its retrieval was disciplined: one targeted search, which confirmed prior proceedings. Among the three candidates, this one gives the most accurate account of what could go wrong.

## Leakage

Forward. One CourtListener search returned documents dated 2026-08-25 and 2026-09-04, both prior proceedings. Three errored shell calls looked for another case's committed prediction as a format template. Those calls concern no outcome of this case. No outcome material was retrieved. Graded `not_applicable`.
