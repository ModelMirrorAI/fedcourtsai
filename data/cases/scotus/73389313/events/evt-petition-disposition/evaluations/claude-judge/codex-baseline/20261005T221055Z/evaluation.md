# Evaluation: codex-baseline — Farr v. Grant, No. 25-1306 (evt-petition-disposition)

## Outcome and scores

Cert-stage cell. The petition was **denied** on 2026-10-05 after a single distribution for the September 28, 2026 conference, with no noted dissent. codex-baseline predicted `denied` at P(grant) = 0.001.

| field | value | how |
| --- | --- | --- |
| correct | 1 | `denied` == `denied` |
| brier_score | 0.000001 | (0.001 − 0)² |
| segment_base_rate | 0.0512 | baseline band, sal-v4, bracketed `reached`, pooled OT2017–OT2024 (n = 11,580) |
| base_rate_basis | risk_set | prediction froze `band: baseline` with `salience_version: sal-v4`, matching the table heading |
| brier_skill_score | 0.9996 | 1 − 0.000001 / 0.0512² |

The base rate pools the eight strictly-prior Term rows the sal-v4 table renders (caption: 10 of 10 Terms, so no lookback divergence to flag), resolved-weighted to 5.12%. codex-baseline computed the same pool from the unrounded JSON as 5.1209%; the rounded-table figure I use differs in the fourth decimal and does not change the skill score at the precision recorded.

## Reasoning quality: 0.85

A careful, well-structured rationale. What drove the score:

- **Right anchor, right population, and the cleanest statement of why.** It pools the sal-v4 baseline `reached` rate over 2017–2024, explains why the context's Term 2025 governs despite the September 2026 calendar, and correctly says federal respondents do not make this a federal petitioner.
- **Good epistemic hygiene.** It treats the petition's account of the decisions below as advocacy rather than finding, flags the OCR, and notes the missing appendix. It applies the Rule 10 standard explicitly and distinguishes conflicts and unsettled federal questions from fact-bound error correction, which is the right frame.
- **The case-specific adjustments are sound.** Questions 1–3, 5, 7–8 as error correction; Question 4's "inter-circuit conflict" as an unsupported label; vehicle uncertainty from the stacked grounds below; no attention signal on the docket. Each is tied to a page range in the petition.

What kept it from higher:

- It does not use the strongest single signal in the record, the petitioner's own list of prior dismissed suits and prior denied cert petitions, which the petition states on its face and which bears directly on how the Court treats this filer.
- The reasoning is over-hedged in places ("do not prove denial", "modest supporting evidence") for a petition whose profile is about as clear a denial as the docket produces; the hedging does not reach the number, which is appropriately low, but it dilutes the analysis.
- The Rule 10 web fetch added nothing the provisioned record did not already supply, which is harmless but is effort spent away from the case.

The forecast document and the claims block were read for context only and are not scored.

## Leakage: forward, not applicable

The log records `mode: forward` with capture coverage 0.91. The three `unobserved` rows are web calls graded on their queries: one Rule 10 search and two opens of the Court's rules-guidance page, none naming this case or its parties. The captured shell calls then fetched the 2026 Rules PDF and extracted Rule 10 text in memory. One shell `find` names `data/qp-topics/` only inside a `-not -path` exclusion; nothing under that path was read. No MCP call and no `retrieved_doc_date` anywhere. The snapshot's last entry is the July 8, 2026 distribution; the prediction is dated 2026-09-17 and the denial came 2026-10-05, so the case was open when predicted. The prose states no outcome material was sought or encountered, consistent with the log. `retrieved_outcome_material` = false, `influenced_prediction` = not_applicable, `leakage_suspected` = false.

## Big case: 0.01

My own read, formed from the petition and outcome before looking at the candidate's score: a pro se conspiracy suit against federal agencies and private entertainment-industry parties, dismissed on the pleadings, affirmed per curiam, denied at the first conference with no writing. No question of general importance and no stakes beyond the parties.
