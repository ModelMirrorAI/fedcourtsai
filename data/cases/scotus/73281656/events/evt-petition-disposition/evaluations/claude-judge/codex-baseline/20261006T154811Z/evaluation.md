# Evaluation of codex-baseline — Lindsey v. South Carolina, No. 25-1176, petition disposition

## Outcome and scores

The event is cert-stage (`kind: petition`, `stage: cert`). The petition was distributed once, for the Conference of September 28, 2026, and **denied on October 5, 2026** with no noted dissent (`actual_granted = 0`, `noted_dissent_from_denial = false`).

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.13 − 0)² = **0.0169**.
- `segment_base_rate` = **0.0512**, basis `risk_set`. The prediction froze `band: baseline` under `salience_version: sal-v4`; the statpack table heading names sal-v4, so the versions match. I pooled the bracketed `reached` figures for `baseline` resolved-weighted over OT2017–OT2024, every rendered Term strictly before Term 2025 (caption: 10 of 10 Terms rendered, so no window divergence to flag): 592.9 / 11,580 = 5.12%. The candidate computed the same figure to more decimals from `statpack.json`.
- `brier_skill_score` = 1 − 0.0169 / 0.0512² = **−5.45**. The most negative of the three: at 2.5× the baseline on a denial, the forecast is well behind the naive baseline.
- `vote_accuracy`, `judgment_correct`: omitted/null, cert stage. No `semantic_grades`: cert cell, no semantic set declared, `record/opinion/` absent as expected.

The forecast document and the `claims` block are not scored here; the harness computes `claim_scores`.

## Reasoning quality: 0.78

A careful, well-organized rationale whose main weakness is that its own evidence does not support the size of the uplift it took.

What it did well:

- **Anchor computed correctly and with unusual precision** (593 / 11,580 reached-band outcomes over OT2017–OT2024), with an explicit, correct warning that terminal relist-bucket rates must not be assigned to a once-distributed petition, and that the capital and CVSG cuts are pooled associations rather than independent multipliers. This is exactly the discipline the statpack asks for.
- **Both sides of the record engaged with page cites**: the petition's split (pp. 16–24), the state dissent, the BIO's preservation objection (pp. 16–18), the BIO's point that the lower court did address evidence "in conjunction" and the overall balance (pp. 13–17), and the BIO's Jefferson distinctions (pp. 23–26). The observation that the dispute may be a factual disagreement over application of an accepted totality standard rather than a categorical split is the right diagnosis of Question 1.
- **Honest about limits**: the reply was not provisioned, the Thornell lookup was throttled, no independent verification of precedent was claimed, and no search touched this petition's disposition.

Where it loses points:

- **The uplift is under-justified by its own analysis.** The downward evidence it marshals (preservation, the lower court's totality language, Jefferson distinguished, Q2 factbound) is the same evidence that led claude-baseline to 0.08 and is the evidence that actually explains the denial. Having identified it, codex-baseline still landed at 13%, roughly 2.5× the anchor, on the strength of "serious consideration above an ordinary baseline petition" and a two-Justice state dissent. It did not weigh how often the Court declines exactly this cumulative-prejudice vehicle, nor did it try to check the preservation point against the lower-court opinion when the throttle hit (the opinion was reachable through the corpus or the REST API; the candidate chose not to use a fallback). The result is a forecast that is well-reasoned in structure but miscalibrated in level, and the outcome punished the level.
- Some of the document is process bookkeeping (cache redirection, path resolution) that belongs in `retrieval.md` rather than the rationale.
- The treatment of the BIO's preservation point as merely "the State's disputed contention" is defensible without the reply, but a cert-stage analyst should still estimate how a Justice reading both briefs would weigh it, rather than leaving it neutral.

## Leakage: forward, not applicable

`retrieval_log.json` records `mode: forward`, 34 calls, `result_capture_coverage` 0.94. The prediction was created 2026-09-16, before the 2026-10-05 resolution. The two `web-search` rows are `unobserved` and are graded on their queries: both target Thornell v. Jones and Rule 10, not this case. The one CourtListener search targets Thornell and was throttled (429). No query names this petition's docket number or caption, no retrieved date reaches the resolution, and the reasoning treats the case as pending ("I neither know nor retrieved this petition's outcome"). The `find` command's `-not -path 'data/qp-topics/*'` excludes that path rather than reading it. `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, `leakage_suspected = false`.

## Big case

My independent read, formed before looking at the candidate's score, is 0.30 (see `big_case.notes`). The candidate's 0.66 is substantially higher; its rationale rests on the reach of cumulative-prejudice doctrine beyond capital cases, which is a fair point about doctrinal stakes but, in my reading, over-weights a question the Court has repeatedly declined to take and ultimately denied here silently. No agreement number is computed.
