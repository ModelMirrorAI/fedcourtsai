# Evaluation: claude-baseline — Majestic Realty Co. v. Salazar, No. 25-1322 (evt-petition-disposition)

## Outcome and scores

The event is a **cert** cell (`event.yaml` stage `cert`). The petition was **denied** on the October 5, 2026 order list after a single distribution for the September 28 long conference, with no relist, no CVSG, and no noted dissent (`outcome.json`: `actual_disposition: denied`, `actual_granted: 0`, `distribution_count: 1`, `noted_dissent_from_denial: false`).

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.10 − 0)² = **0.0100**.
- `segment_base_rate` = **0.0512**, basis `risk_set`. The prediction froze `band: baseline` under `salience_version: sal-v4`, and the statpack's band table heading is sal-v4, so the versions match. I pooled the bracketed `reached` figure for `baseline` resolved-weighted over every rendered Term strictly before OT2025: OT2017–OT2024 (5.7% n=1271, 5.9% n=1312, 5.8% n=1192, 5.6% n=1500, 4.5% n=1739, 4.6% n=1399, 4.6% n=1524, 4.7% n=1643), giving 592.9 / 11,580 = 0.0512. The caption says 10 of 10 Terms are rendered, so the rendered window is the pack's whole window; the in-code 10-Term lookback (OT2015–OT2024) reaches two Terms the pack does not hold and so pools the same eight rows. No window divergence to flag.
- `brier_skill_score` = 1 − 0.0100 / 0.0512² = **−2.81**. A 10% forecast on a petition denied cleanly is worse than parroting the band rate; the baseline Brier here is tiny (0.0026), so every point above the anchor is expensive.

Votes are not scored on a cert cell. `claim_scores` is the harness's.

## Reasoning quality: 0.78

**What it got right.** The anchor is exactly right: the candidate read the sal-v4 table, pooled the bracketed reached figure over OT2017–OT2024 (5.1%, n=11,580), and explained why it rejected the terminal relist-0 and whole-docket figures. The three factors it named for denial are the ones that decided this petition: Cedar Point (2021) and Moody (2024) both expressly preserved PruneYard, the posture is an interlocutory state-court preliminary-injunction reversal with a live §1257 finality problem, and the ask is an overruling with no lower-court split on the federal question. The §1257 / Cox Broadcasting point is a real vehicle defect the brief in opposition presses and the candidate was the only one to name it specifically. It read the petition and BIO in full and correctly noted the BIO was filed without a call for response. It stated honestly that CourtListener was throttled, that its memory of prior PruneYard-challenge denials was unverified, and that it did not know the outcome.

**Where it went wrong.** The candidate doubled the anchor to 0.10 on counsel identity and amicus count. Pacific Legal Foundation's grant record is real but is concentrated in petitions with a split or a clean final judgment; here neither existed, and four ideologically aligned cert-stage amici on an overruling ask with no split is organized interest rather than a signal the Court's screening treats as weighty. The candidate itself called the interlocutory posture "a hard problem the reply cannot argue away" and read the two recent majority opinions as "a Court content with the line" — conclusions that argue for staying at or below the anchor, not for doubling it. Its relist number (0.35) likewise overread the signal: the petition was not relisted. The analysis was sound in its parts but the net adjustment ran against the weight of its own findings.

**Net.** Thorough, well-sourced, correct on the mechanism and the main obstacles, honest about its retrieval limits, but it sized the upward adjustment larger than its own analysis supported. The forecast document was read for context only and is not scored.

## Leakage

`mode: forward` per the staged retrieval log. The prediction was created 2026-09-17, eleven days before the conference and eighteen before the denial. I scanned the log for this case's disposition surfacing as decided: no call carries a `retrieved_doc_date`; the one query that named this docket (CourtListener docket search for 25-1322) was throttled and returned nothing, and would in any case have shown an open docket on that date; two corpus `query` calls fetched recent granted scotus rows and an empty citation lookup; no `data/qp-topics/` read. The reasoning explicitly states the conference had not occurred. `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`. Not a mis-provisioned forward cell.

## Big case

My own read is 0.5 (see `evaluation.json`). I note for the record that I saw the candidates' `big_case_score` values while reading the staged `prediction.json` files before I had written my read down; my number is formed from the record and the outcome and I did not adjust it toward theirs.
