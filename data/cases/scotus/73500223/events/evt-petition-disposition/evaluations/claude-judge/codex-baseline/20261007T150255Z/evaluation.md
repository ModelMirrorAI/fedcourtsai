# Evaluation: codex-baseline — Majestic Realty Co. v. Salazar, No. 25-1322 (evt-petition-disposition)

## Outcome and scores

The event is a **cert** cell (`event.yaml` stage `cert`). The petition was **denied** on the October 5, 2026 order list after a single distribution for the September 28 long conference, with no relist, no CVSG, and no noted dissent (`outcome.json`: `actual_disposition: denied`, `actual_granted: 0`, `distribution_count: 1`, `noted_dissent_from_denial: false`).

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.08 − 0)² = **0.0064**.
- `segment_base_rate` = **0.0512**, basis `risk_set`. The prediction froze `band: baseline` under `salience_version: sal-v4`, matching the statpack table's heading. Pooled bracketed `reached` figure for `baseline`, resolved-weighted over the rendered Terms strictly before OT2025 (OT2017–OT2024; n = 11,580): 0.0512. This is the same pool the candidate computed from the unrounded statpack fields (593 / 11,580 = 5.12%). The caption renders 10 of 10 Terms, so the rendered window is the pack's whole window and the in-code 10-Term lookback pools the same eight rows. No window divergence to flag.
- `brier_skill_score` = 1 − 0.0064 / 0.0512² = **−1.44**. An 8% forecast on a clean denial is worse than parroting the band rate.

Votes are not scored on a cert cell. `claim_scores` is the harness's.

## Reasoning quality: 0.82

**What it got right.** This is the most disciplined rationale on the cell. The anchor is computed exactly and the method is stated (sum of rate × weighted resolved over the selected Terms and band, 2025 and 2026 rows excluded). The candidate correctly distinguished the terminal relist and CVSG cuts from a forward hazard and used them only for shape. It stated its information boundary precisely: which documents it read, which it did not (the reply, the amici, the appendix), and that the as-stored snapshot's creation date, not its filename date, bounds what it knew. It verified the two precedents its denial case rests on — Cedar Point's "unlike the growers" distinction of open shopping premises and Moody's treatment of a non-expressive mall owner — against the opinion text through CourtListener rather than from memory, and it was careful to use the Moody majority and not separate opinions. The three constraints it named (preliminary-injunction vehicle with a contested record, no established federal split, later precedents that distinguish rather than erode PruneYard) are the reasons this petition was denied without a relist. It also correctly read the single distribution as not a relist and the BIO as not Court-requested.

**Where it went wrong.** Like claude-baseline, the candidate moved above the anchor, to 0.08, on "a substantial constitutional reconsideration request with supporting amici." Its own analysis undercut that move: it concluded the posture and record development were "substantial risks," found no square federal split, and found both doctrinal lines expressly preserved against the petition's theory. On those findings a private petition at first distribution is at or below the band rate, not above it. The adjustment was modest and the candidate labeled it judgmental rather than fitted, which is the honest framing, but the direction was not earned by the analysis. A small inaccuracy: the rationale says the event has "no explicit stage or moment field"; the event record carries `stage: cert` and `moment: distribution`. It did not affect the forecast.

**Net.** Rigorous, verifiable, precise about its limits, and right about the mechanism; its only real fault is sizing the upward adjustment against the grain of its own findings. The forecast document was read for context only and is not scored.

## Leakage

`mode: forward` per the staged retrieval log. The prediction was created 2026-09-17, before the conference. Of 41 calls, 39 are captured. The two `unobserved` calls are a web search and a web open whose queries target the Cedar Point slip opinion and Moody v. NetChoice, not this docket; graded on query, they seek no outcome material. Four captured CourtListener MCP calls retrieved and text-searched the 2021 Cedar Point and 2024 Moody opinions — pre-event precedents that cannot carry this petition's October 2026 disposition. No call names docket 25-1322's result, no `retrieved_doc_date` is on or after 2026-10-05, and there is no `data/qp-topics/` read. The reasoning states the outcome was not sought and not known. `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`. Not a mis-provisioned forward cell.

## Big case

My own read is 0.5 (see `evaluation.json`). I note for the record that I saw the candidates' `big_case_score` values while reading the staged `prediction.json` files before I had written my read down; my number is formed from the record and the outcome and I did not adjust it toward theirs.
