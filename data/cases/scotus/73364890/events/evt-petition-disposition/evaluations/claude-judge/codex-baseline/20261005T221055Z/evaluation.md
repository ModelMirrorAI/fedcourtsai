# Evaluation of codex-baseline — F.E.B. Corp. v. United States, No. 25-1294

**Outcome.** Petition denied on the 2026-10-05 order list after a single distribution for the 2026-09-28 conference; no CVSG, no relist, no noted dissent. `actual_granted` = 0.

**Prediction.** `denied`, P(grant) = 0.01. Correct on the disposition axis.

## Scores

| field | value | how |
| --- | --- | --- |
| correct | 1 | `denied` == `denied` |
| brier_score | 0.0001 | (0.01 − 0)² |
| segment_base_rate | 0.0512 | baseline band, bracketed `reached` figure, sal-v4 table in `metrics/statpack.md`, pooled resolved-weighted over Terms 2017–2024 (592.9 / 11,580 = 0.051203, held as 0.0512) |
| base_rate_basis | risk_set | the prediction froze `band: baseline` under `salience_version: sal-v4`, and the table heading names sal-v4 |
| brier_skill_score | 0.961853 | 1 − 0.0001 / (0.0512)² |
| reasoning_quality | 0.86 | see below |

The case's Term is 2025; the table renders 10 of 10 Terms, and the strictly-prior rows with a baseline figure are 2017–2024, so the rendered window and the pack's window coincide and no window divergence needs flagging. This is a cert cell, so Brier, rate, basis and skill are mine; `correct` is also written per contract for the stamp's comparison. No `vote_accuracy` (cert stage), no `semantic_grades` (no declared set), no `claim_scores` (harness-computed).

## What the reasoning got right

- Correct anchor, correctly pooled: the bracketed reached baseline-band rate over Terms 2017–2024 under the matching sal-v4 vocabulary, 593 / 11,580 ≈ 5.12%, with Terms 2025 and 2026 excluded. It also explains why the relist and CVSG cuts are context rather than hazards, which is the right reading of those tables.
- The strongest part of the document is its use of the appended Eleventh Circuit opinion. It cites the pages where the panel invokes Anderson for deference to documentary inferences, the footnote applying Bufkin v. Collins to a predominantly factual mixed question, the two-day trial with expert testimony, and the panel's rejection of one government rationale while sustaining others. Each of these is a concrete vehicle problem for a petition that casts the case as a purely documentary one, and each is drawn from the provisioned record.
- It reads the petition's argument honestly: a request to revisit Justice Blackmun's reservation in Anderson, with no conflicting appellate holdings identified. It is careful to say that this is an assessment of the supplied argument, not a claim that no split exists.
- It treats the waiver as a modest negative signal rather than a procedural bar, which is accurate, and correctly notes that a call for the government's response as a party is not a CVSG.
- It is candid about its inputs: the provisioned vintages, the truncated appendix, the absence of a brief in opposition, and the failed external fetches that left it relying on the record text rather than a verified current Rule 52.

## Where it is weaker

- The waiver is under-weighted relative to its practical force. The Court does not grant without calling for a response, so a waived petition distributed without a call is on a near-deterministic path to denial at its first conference; the document treats this as one signal among several rather than the gating fact. The 1% number is still well placed.
- A good deal of the cell's effort went into retrieving Rule 52 text that it never obtained; that is process rather than analysis, and the document rightly declines to assert anything about a rule amendment it could not read. It does not affect the soundness of what was written, but it did not add anything either.
- The 0.27 significance score is high for a single-island title dispute, and the rationale leans on a hypothetical reach of a documentary-review rule the petition does not develop. That is a big-case read, not a reasoning-quality matter, and I keep it out of the number.

`reasoning_quality` 0.86: a careful, well-sourced rationale whose main weakness is a slightly diffuse weighting of the dominant signal.

## Leakage

Mode `forward` per the captured log. The prediction was created 2026-09-17 against the 2026-09-16 snapshot; the petition was resolved 2026-10-05. The log's only external calls are web searches and page opens for the text of Federal Rule of Civil Procedure 52 and the Court's rules; all are `unobserved` (coverage 0.65), so I grade them on their queries, none of which names this case, its parties, Wisteria Island, or its docket. No corpus query and no CourtListener call was made; the shell fallbacks hit official rules pages only. The candidate's retrieval note matches the log. Nothing suggests the case was decided when provisioned. `influenced_prediction` = `not_applicable`, `retrieved_outcome_material` = false, `leakage_suspected` = false.

## Big case

My independent read is 0.08: a local quiet-title dispute with a procedural question the Court settled forty years ago, no amicus, a government waiver, and a silent denial.
