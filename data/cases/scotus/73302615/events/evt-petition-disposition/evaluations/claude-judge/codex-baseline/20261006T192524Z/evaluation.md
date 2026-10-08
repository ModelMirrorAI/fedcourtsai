# Evaluation: codex-baseline — scotus/73302615, evt-petition-disposition

**Stage:** cert (event.yaml `stage: cert`). **Outcome:** petition denied on 2026-10-05 after the September 28 long conference, no noted dissent, Justice Kavanaugh not participating; `actual_granted` 0, two distributions, no CVSG.

## Scores

| Field | Value | Basis |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` denied == `actual_disposition` denied |
| `brier_score` | 0.0196 | (0.14 − 0)² |
| `segment_base_rate` | 0.172242 | elevated band, bracketed **reached** figure, sal-v4 table, Terms 2017–2024 pooled resolved-weighted: 484 / 2810 |
| `base_rate_basis` | risk_set | the prediction froze `context.band` = elevated **and** `context.salience_version` = sal-v4, matching the table heading |
| `brier_skill_score` | 0.339 | 1 − 0.0196 / (0.172242)² = 1 − 0.0196 / 0.029667 |
| `reasoning_quality` | 0.82 | below |
| `vote_accuracy` | omitted | cert cell, never scored |
| `judgment_correct` | null | no judgment on either side |

Base-rate window: the sal-v4 table caption says it renders all 10 Terms the pack holds (2017–2026), so the rendered window and the pack's window coincide and there is no divergence to flag. Strictly-prior to the case's Term (2025) leaves eight Terms, 2017–2024. The configured 10-Term lookback would reach back to 2015, but the pack carries nothing before 2017 and the in-code rule shortens the sample rather than refilling it, so the same 484 / 2810 pool results either way. The cell's own `record/context.json` band is terminal and was not used.

## What the prediction got right and wrong

Right: the disposition, and the direction of its departure from the anchor. It computed the same pooled anchor (17.22%, from the JSON pack rather than the rounded table) and moved **below** it to 14%, the only candidate to do so, and the denial bore that out.

The reasoning's best move is its reading of the two distributions: it recognised that the June 2 distribution ended in a call for a response rather than a conference decision, so the August 26 distribution was the first time the Court held the fully briefed petition, and declined to stack a relist bonus on top of a band-conditioned anchor. That is exactly right about this docket and is the point the other two candidates handled less well.

It engaged the brief in opposition's strongest points directly: the act-of-state question reached the D.C. Circuit only through pendent appellate jurisdiction riding on an immunity appeal, the posture is interlocutory, the conflicting authorities are decades old, and the issue recurs rarely. It characterised the pendent-jurisdiction problem as a vehicle risk rather than a proven defect, which is the fair reading. It went and read the August 26 counsel-withdrawal letter linked on the docket and construed it carefully: withdrawal of counsel, not of the petition, a modest downward adjustment rather than a mootness presumption. It also checked Republic of Hungary v. Simon (2025) to confirm it predates the decision below and so supplies no GVR hook.

Weaknesses, modest: the document spends a fair amount of space on process narration (which tables it read, which tool failed) that adds nothing to the legal analysis. The CFR-after-waiver signal is acknowledged but somewhat under-weighted in the prose relative to how much the vehicle concerns are weighted; on this outcome that happened to be the right call, but the asymmetry is asserted more than argued. None of this is unsound.

## reasoning_quality: 0.82

Sound anchor, correct identification of the leakage-safe window, a sharp and correct reading of the docket's procedural shape, real engagement with the opposition's vehicle arguments, careful handling of a pre-decision filing it went and read, and a probability whose departure from the anchor is explained. Graded on `reasoning.md` alone; the forecast document and the claims block were read for context only and are not scored here.

## Leakage

Mode forward; `retrieved_outcome_material` false; `influenced_prediction` not_applicable; `leakage_suspected` false. The prediction was made 2026-09-18 against a petition that was decided 2026-10-05. The log's only external fetches are a statute lookup (unobserved, graded on its query), the docket-linked August 26 letter (retrieved, dated 2026-08-26, pre-decision, disclosed in both prose documents), and three CourtListener calls about Simon. Nothing in the log or the reasoning reaches this petition's disposition, and no `data/qp-topics/` path was read. Not a mis-provisioned decided case.

## Big case

My independent read, formed before reading any candidate's score, is 0.35: a genuine but narrow statutory question in foreign-expropriation litigation, interlocutory, no amici, resolved by a bare denial. The candidate's own score is recorded on its prediction; no agreement number is computed here.

## Blind

Graded from `record/blinded/codex-baseline/` only. The alias is the only identity used anywhere in this cell's output.
