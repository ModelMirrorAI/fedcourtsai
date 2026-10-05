# Evaluation: claude-baseline — Farr v. Grant, No. 25-1306 (evt-petition-disposition)

## Outcome and scores

Cert-stage cell. The petition was **denied** on 2026-10-05 after a single distribution for the September 28, 2026 conference, with no noted dissent. claude-baseline predicted `denied` at P(grant) = 0.004.

| field | value | how |
| --- | --- | --- |
| correct | 1 | `denied` == `denied` |
| brier_score | 0.000016 | (0.004 − 0)² |
| segment_base_rate | 0.0512 | baseline band, sal-v4, bracketed `reached`, pooled OT2017–OT2024 (n = 11,580) |
| base_rate_basis | risk_set | prediction froze `band: baseline` with `salience_version: sal-v4`, matching the table heading |
| brier_skill_score | 0.9939 | 1 − 0.000016 / 0.0512² |

The base rate pools the eight strictly-prior Term rows the sal-v4 table renders (the caption shows 10 of 10 Terms, so the rendered window is the pack's window and there is no lookback divergence to flag): 5.7, 5.9, 5.8, 5.6, 4.5, 4.6, 4.6, 4.7 percent on n = 1271, 1312, 1192, 1500, 1739, 1399, 1524, 1643, resolved-weighted to 5.12%. The case's Term is 2025 from the frozen context, so OT2025 and OT2026 are excluded.

## Reasoning quality: 0.90

The rationale is the strongest of the three. What drove the score:

- **Right anchor, right population.** It names the baseline `reached` rate under sal-v4, checks the version against the table heading, pools exactly the strictly-prior rows, and reports the pooled figure (~5.1%, n ≈ 11,580) that I independently reproduce.
- **Facts checked against the petition hold up.** The petition does list more than a dozen prior suits and prior cert petitions (07-993, 12-957, 15-745, 18-6779/6780/6781); it does say the case is "res ipsa loquitur — the matter speaks for itself"; the disposition below was a pleadings-stage dismissal affirmed per curiam; the Eighth Circuit cut it quotes (1.2% granted, 1.4% GVR) is the statpack's modern-cert-by-circuit row. Nothing is invented.
- **The adjustments are the right ones and are ordered sensibly.** Pro se serial filer, no legal question beyond a bare "inter-circuit conflict" label on a venue complaint, universal waivers including the Solicitor General with no call for a response, an unpublished per curiam vehicle. It correctly notes that a federal respondent is not a federal petitioner and so does not move the case out of the private risk set.
- **Honest uncertainty.** It says where a reader should discount it (toward 1–2% if one weights paid pro se petitions nearer the pooled rate) and confirms the cell is genuinely forward from the snapshot's own dates.

What kept it from higher: the claim that pro se paid petitions grant at "a small fraction" of the counseled rate is asserted without a source, and the forward document's conditional reasoning is not scored here. These are minor.

The forecast document and the claims block were read for context only and are not scored.

## Leakage: forward, not applicable

The log records `mode: forward` with capture coverage 1.0. Every call is a local read of the prompt, schema, event, context, the 2026-09-16 snapshot, the petition, and the statpack, plus one corpus query for granted 2020s rows carrying no case-specific term. No web search, no MCP call, no `data/qp-topics/` path, no `retrieved_doc_date` anywhere. The snapshot's last entry is the July 8, 2026 distribution for the 9/28 conference; the prediction is dated 2026-09-17 and the denial came 2026-10-05, so the case was open when predicted and nothing was mis-provisioned. `retrieved_outcome_material` = false, `influenced_prediction` = not_applicable, `leakage_suspected` = false.

## Big case: 0.01

My own read, formed from the petition and outcome before looking at the candidate's score: a pro se conspiracy suit against federal agencies and private entertainment-industry parties, dismissed on the pleadings, affirmed per curiam, denied at the first conference with no writing. No question of general importance and no stakes beyond the parties.
