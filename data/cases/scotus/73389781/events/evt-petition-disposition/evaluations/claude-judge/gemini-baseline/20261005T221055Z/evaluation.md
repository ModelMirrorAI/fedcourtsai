# Evaluation of gemini-baseline — scotus/73389781, evt-petition-disposition

## The cell

A **cert** cell (`event.yaml` stage `cert`, moment `distribution`): Christy Ann Martin v. John Fredrick Martin, No. 25-1307, a paid petition from the Court of Appeals of Mississippi asking whether Turner v. Rogers and Bearden v. Georgia forbid civil-contempt incarceration to collect a private money judgment without an express present-ability-to-pay finding. `outcome.json` records `actual_disposition: denied`, `actual_granted: 0`, resolved 2026-10-05, one distribution, no CVSG, no noted dissent. The 2026-10-05 snapshot carries the disposing entry: "Petition DENIED", October 5, 2026, the order list after the September 28 long conference, with no relist.

## Scores

- `correct` = 1: the candidate predicted `denied`; the outcome is `denied`.
- `brier_score` = (0.01 − 0)² = 0.0001.
- `segment_base_rate` = 0.05120, `base_rate_basis` = `risk_set`. The prediction's frozen context carries `band: baseline` and `salience_version: sal-v4`, matching the heading of the committed `metrics/statpack.md` "Segment base rate by salience band (sal-v4)" table, so the rate is the `baseline` column's bracketed `reached` figure pooled resolved-weighted over the rendered Terms strictly before the case's Term 2025: OT2017–OT2024 (4.7/1643, 4.6/1524, 4.6/1399, 4.5/1739, 5.6/1500, 5.8/1192, 5.9/1312, 5.7/1271), giving 592.9/11,580 = 5.120%. The caption says 10 of 10 Terms are rendered, so the rendered window is the pack's and nothing is flagged; the ten-Term configured lookback reaches past OT2017 but the pack holds nothing earlier, so the pool is the same eight Terms either way. `statpack.json`'s unrounded rates give 5.121%.
- `brier_skill_score` = 1 − 0.0001 / 0.05120² = 0.962.
- `vote_accuracy`, `judgment_correct`, `semantic_grades`: omitted or null. Cert stage; `semantic_claims` is null, as expected. `claim_scores` is the harness's and is not written.

## Reasoning quality: 0.60

Graded on `reasoning.md` only. The document is three paragraphs and reaches the right place by the right route in outline: it names the baseline band's `reached` rate pooled over prior Terms as the anchor, identifies the state courts' findings that the petitioner could work and chose not to, the suspended and never-executed sentence, and the appellate reservation of inability to pay as a continuing defense, and draws the correct conclusion that the petition's no-hearing premise is contradicted by the record. The CVSG reasoning is right.

It is thin where the stronger candidates were specific, and it has one methodological slip. The slip is using the terminal relist-0 rate (1.2%) as a downward prior for a petition at its first distribution: that cut describes petitions that ended with no relist, which is known only in hindsight, and a petition sitting at one distribution still belongs to the population that may relist, which is exactly why the risk-set `reached` figure is the registered anchor. The candidate treats the two as compatible without saying why. The thinness: the preservation defect, which the opposition presses and which the opposition's own appendix documents, goes unmentioned; the asserted split is not examined; Turner's actual holding is invoked by name only; and no passage of the record is cited. The retrieval log shows reads of the questions presented and the brief in opposition but no read of `petition.txt`, which is consistent with the document's one-sided reliance on the respondent's account and its lack of engagement with the petition's own arguments. The number was right, and the reasons given are correct, but a reader cannot tell from this document how a 5% anchor became 1% rather than 3% or 0.5%.

## Leakage

Forward cell (`retrieval_log.json` mode `forward`, capture coverage 0.0: every marker-carrying call is unobserved, the engine's standing shape, so each call is graded on its query rather than credited with returning nothing). The queries are file reads of `AGENTS.md`, the prompt, `event.yaml`, `context.json`, the documents directory, the 2026-09-16 snapshot, the questions presented, `metrics/statpack.md`, and the brief in opposition, then the output writes and a validate run. No search, no web, no CourtListener MCP, no `data/qp-topics/` read, no `retrieved_doc_date`. Nothing names this case beyond the provisioned paths. The prediction was created 2026-09-17, before the September 28 conference and the October 5 denial, so no outcome existed to retrieve. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. The candidate's `flags.json` is not staged, so its only disclosure channel in my view was its prose and its one-line `retrieval.md`.

## Big case

My independent read is 0.15: a two-party divorce-decree contempt dispute over roughly $21,000, a suspended sentence never executed, an intermediate state court below, no amicus, and a bare denial with no relist or separate writing. The debtors'-prison question has some salience in the abstract, but this record would not have reached it. One honesty note: the predictor's `big_case_score` sits in the staged `prediction.json` I read before forming this, so the read is not strictly unanchored; I formed the number from the record and the outcome and did not adjust it toward theirs.
