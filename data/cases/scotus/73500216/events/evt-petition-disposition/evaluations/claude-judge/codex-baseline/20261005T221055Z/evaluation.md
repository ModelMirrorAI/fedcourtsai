# Evaluation: codex-baseline — scotus/73500216, evt-petition-disposition

## Cell and outcome

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`), forward mode. The petition (No. 25-1316, Pearson v. Guerrero) was distributed once, for the 2026-09-28 long conference, and **denied on 2026-10-05** with no noted dissent (`actual_disposition: denied`, `actual_granted: 0`, `distribution_count: 1`).

## Scores

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.02 − 0)² = 0.0004.
- `segment_base_rate` = 0.0512, `base_rate_basis` = `risk_set`. The prediction's frozen context carries `band: baseline` **and** `salience_version: sal-v4`, matching the heading of the committed statpack's "Segment base rate by salience band" table, so the bracketed `reached` figure applies. Pooled resolved-weighted over the rendered Terms strictly before Term 2025 (OT2017–OT2024): 592.9 / 11,580 ≈ 0.0512. The caption renders 10 of 10 Terms, so no window divergence.
- `brier_skill_score` = 1 − 0.0004 / 0.0512² ≈ 0.8474.
- `vote_accuracy`, `judgment_correct`, `semantic_grades`: omitted — cert stage.

## Reasoning quality: 0.88

This is a careful, well-sourced rationale. Its base-rate work is exactly right: it chose the risk-set `reached` figure because the band was frozen, pooled OT2017–OT2024 from the companion `statpack.json`, and reported 593 / 11,580 = 5.12%, which is the same number I compute from the rendered table. It declined the pack-wide modern-cert rate and the originating-circuit cut as anchors and used the relist and CVSG cuts only for shape, which is the correct reading of those tables.

The legal analysis is proportionate and accurate on the record I hold. It states the AEDPA obstacle with the right nuance: the Fifth Circuit *assumed arguendo* that implied bias could be clearly established law and found the state decision reasonable on these facts (petition Appendix A, which I checked), so the obstacle is a reasonableness holding rather than an absolute bar, and the candidate says so explicitly. It read the petition's own split section closely enough to notice that the favorable cases turn on concealment, equivocation, or contemporaneous victimization that this record lacks. It independently checked *Fields v. Brown* through CourtListener and correctly observed that the petition itself cites that case with a "but see" in its own split discussion (staged petition text), weakening the claim of a clean split. It noted the unpublished, record-bound opinion below. It refused to infer a waiver from the respondent's silence, which is the correct reading of a docket that carries no waiver entry. It also surfaced a real inconsistency in the provisioned snapshot (a petition-filed entry dated April 1 against a May 22 signature, a May-dated URL, and a May 28 docketing), declined to use the spurious interval as a signal, and left the input alone.

Minor deductions: the counterweights are listed but not weighed against the anchor in a way that shows why 2% rather than 1% or 3%, and the candidate's own description of its number as "a judgmental adjustment" is honest but leaves the calibration step opaque. The precedent check on *Fields* is useful context but does not bear on the grant probability much beyond what the petition already concedes. These are small.

## Leakage

`mode: forward`, `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`. Prediction created 2026-09-17 against a snapshot ending at the 2026-07-15 distribution; the conference was eleven days away. The log (39 calls, `result_capture_coverage` 0.95) shows provisioned record reads, statpack and `statpack.json` reads, one corpus citation query for *Smith v. Phillips* (no prior returned), CourtListener searches and document reads for *Fields v. Brown* (2007) and *Smith v. Phillips* (1982), and two `unobserved` web calls whose queries target those two precedents and a Library of Congress U.S. Reports PDF, not this docket. Graded on their queries, the unobserved calls cannot have reached this case's disposition. No call targets this petition's live docket or outcome; no `data/qp-topics/` path appears; the rationale states it does not know the disposition. Not a mis-provisioned decided case.

## Big case

My own read is 0.22 (see `big_case.notes`). The predictors' scores sat inside the staged `prediction.json`, which I had read before writing mine down, so the independence of this read is partial.
