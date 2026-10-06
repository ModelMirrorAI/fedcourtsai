# Evaluation: gemini-baseline — Farr v. Grant, No. 25-1306 (evt-petition-disposition)

## Outcome and scores

Cert-stage cell. The petition was **denied** on 2026-10-05 after a single distribution for the September 28, 2026 conference, with no noted dissent. gemini-baseline predicted `denied` at P(grant) = 0.001.

| field | value | how |
| --- | --- | --- |
| correct | 1 | `denied` == `denied` |
| brier_score | 0.000001 | (0.001 − 0)² |
| segment_base_rate | 0.0512 | baseline band, sal-v4, bracketed `reached`, pooled OT2017–OT2024 (n = 11,580) |
| base_rate_basis | risk_set | prediction froze `band: baseline` with `salience_version: sal-v4`, matching the table heading |
| brier_skill_score | 0.9996 | 1 − 0.000001 / 0.0512² |

The base rate pools the eight strictly-prior Term rows the sal-v4 table renders (caption: 10 of 10 Terms, so no lookback divergence to flag), resolved-weighted to 5.12%.

## Reasoning quality: 0.55

The conclusion is right and the number is well placed, but the rationale is thin. What drove the score:

- **Right anchor.** It names the prior-Term pooled baseline `reached` rate over 2017–2024 as "roughly 5%", which is the correct population and the correct window, though it never states the pooled figure or the n.
- **The two signals it uses are real.** Pro se petitioner on a paid docket, every respondent including the federal parties waived, a single distribution. Those are the right features.
- **It did not read the petition.** The log shows the questions-presented file read and not `petition.txt`. The judgment that the petition is "clearly frivolous" rests on the eight questions alone. Here that judgment happens to be defensible, because the questions themselves assert a 25-year government conspiracy and a right to the Presidency under 42 U.S.C. § 1985, but the method generalizes badly: a petition whose questions are poorly drafted can still carry a real conflict in its body, and nothing in this rationale would have caught one.
- **No engagement with the cert standard.** There is no Rule 10 analysis, no treatment of the "inter-circuit conflict" label in Question 4, no mention of the serial-filer history the petition recites, and no explanation of why a deviation from 5% to 0.1% rather than to 1% is warranted. "Vehicle quality is nonexistent" is a conclusion, not an argument.

The rationale is two short paragraphs. It is correct and not misleading, so it earns more than a bare pass; it does not do the analytical work the other candidates did, so it earns clearly less than they do.

The forecast document and the claims block were read for context only and are not scored.

## Leakage: forward, not applicable

The log records `mode: forward` with capture coverage 0.0, which is this engine's standing shape rather than a defect: every call is `unobserved`, so each is graded on its query. All queries are local reads of the prompt, AGENTS.md, the event, context, the 2026-09-16 snapshot, questions-presented, the statpack, and the schema, followed by the output writes and `validate`. No web search, no MCP call, no `data/qp-topics/` path. The snapshot's last entry is the July 8, 2026 distribution; the prediction is dated 2026-09-17 and the denial came 2026-10-05, so the case was open when predicted. The prose cites nothing beyond the provisioned record. `retrieved_outcome_material` = false, `influenced_prediction` = not_applicable, `leakage_suspected` = false.

## Big case: 0.01

My own read, formed from the petition and outcome before looking at the candidate's score: a pro se conspiracy suit against federal agencies and private entertainment-industry parties, dismissed on the pleadings, affirmed per curiam, denied at the first conference with no writing. No question of general importance and no stakes beyond the parties.
