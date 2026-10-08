# Evaluation: codex-baseline — scotus/73281694, evt-petition-disposition

**Stage:** cert (event.yaml `stage: cert`, moment `distribution`). **Outcome:** petition
DENIED on the October 5, 2026 order list after the September 28 long conference, with no
noted dissent (`noted_dissent_from_denial: false`), two distributions, no CVSG.

**Prediction:** `denied`, P(grant) = 0.36. **Correct:** 1. **Brier:** 0.1296.

## Base rate and skill

The prediction froze `band: elevated` under `salience_version: sal-v4`; the statpack's
segment table is headed sal-v4, so the basis is `risk_set`. Pooling the bracketed `reached`
figure resolved-weighted over Terms 2017–2024 (eight rendered rows, weighted n = 2,810)
gives `segment_base_rate` = 0.1724. The caption shows 10 of 10 Terms, so no lookback
divergence is owed. Baseline Brier against a denial is 0.0297, so `brier_skill_score` =
1 − 0.1296 / 0.0297 ≈ **−3.36**. Right label, but the number sat nineteen points above the
anchor on a petition that was denied silently, so the band rate alone would have scored
better. The candidate computed the same anchor (17.24%, n = 2,810) and said so.

## What drove `reasoning_quality` = 0.78

A careful, well-sourced analysis that reached the right label for sound reasons, slightly
less decisive than it could have been.

- **It engaged the vehicle with the primary documents.** It read the BIO including its
  appended orders (the January 28, 2025 waiver footnote at 4a), fetched the petition appendix
  to confirm the April 7 order overrules objections without explanation, and fetched the
  reply to weigh the amended-complaint and Michigan v. Long answers. It correctly declined to
  treat the Superior Court's Hunt citation as a merits holding, since the reproduced Hunt
  passage goes to discretionary interlocutory-review criteria. This is the right level of
  scrutiny and it is anchored to page cites.
- **It read the docket signal honestly.** It saw that the second distribution reflects the
  response cycle rather than a completed conference, and refused to read the calendar gap as
  repeated merits deliberation, while keeping the authoritative band and count.
- **It used the Lynn v. BNSF denial as permitted pre-snapshot context** and gave it the right
  weight — weakly cautionary, not decisive.
- **Its anchor and bucket reading were precise**, including the explicit statement that the
  terminal relist/CVSG buckets describe population shape and are not forward hazards.

Why not higher: having identified preservation, finality, the absence of a split, and the
Lynn denial, the rationale still described these as "risks, not established absolute bars"
and landed at 0.36 — more than double the anchor — while the write-up's own weighing points
lower. It gave the invitation and the response request slightly more credit than the
procedural record supports, and it did not identify, as claude-baseline did, that an unexplained
order after an express waiver finding is the pool memo's lead argument rather than one
consideration among several. A fair amount of the document restates what it read and did not
read, which is good disclosure but not analysis. Nothing in it is wrong.

## Leakage

Mode `forward`, 35 calls, `result_capture_coverage` 0.89. The four `web-search` rows are all
`unobserved`, so they are graded on their queries: a Rule 10 phrase search, the Court's Rules
PDF, and this petition's July 14, 2026 reply brief URL twice — none a query for the
disposition, the current docket, or decision coverage. Captured `curl` calls fetched the same
reply brief and the April 17, 2026 petition appendix, both pre-snapshot filings whose URLs
were in the provisioned snapshot. No `retrieved_doc_date` at or after 2026-10-05, no
corpus or MCP calls, and the reasoning disclaims knowledge of the outcome and names no
post-conference fact. The case was genuinely open at prediction time (created 2026-09-16;
resolved 2026-10-05), so the forward default holds: `retrieved_outcome_material: false`,
`influenced_prediction: not_applicable`, `leakage_suspected: false`.

## Big case

My independent stakes read is 0.6 (see `evaluation.json`): a nationally consequential
question in a vehicle the Court declined without a word. Reading the staged
`prediction.json` displayed the candidate's `big_case_score` before I had written mine down;
the read above is my own and was formed from the record and the outcome, but the sequence is
recorded here for honesty.

Nothing in `predicted_reasoning.md` or the `claims` block was scored; the harness scores the
claims in code.
