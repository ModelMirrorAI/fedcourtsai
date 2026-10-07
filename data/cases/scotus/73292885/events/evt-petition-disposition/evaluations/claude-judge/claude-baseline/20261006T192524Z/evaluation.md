# Evaluation of claude-baseline — scotus/73292885, evt-petition-disposition

## Cell and outcome

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`), forward mode. Pestarino v. Pestarino, No. 25-1249: a paid, pro se petition from an unpublished Washington Court of Appeals decision affirming a civil protection order; distributed once (June 17, 2026) for the September 28, 2026 long conference. Outcome: **denied** on October 5, 2026, `actual_granted` 0, no noted dissent, one distribution. No opinion slot is staged, as expected on a cert cell.

## Scores

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.01 − 0)² = **0.0001**.
- `segment_base_rate` = **0.0512**, `base_rate_basis` = `risk_set`. The prediction froze `band: baseline` under `salience_version: sal-v4`, matching the statpack heading, so the bracketed `reached` figure applies, pooled resolved-weighted over the rendered Terms strictly before Term 2025 (OT2017–OT2024; the caption renders 10 of 10 Terms, so no lookback divergence): 593.0 / 11,580 = 5.12%. The candidate pooled the same eight rows and reported about 5.1% on roughly 11,580, which agrees.
- `brier_skill_score` = 1 − 0.0001 / 0.0512² = **0.962**.
- `vote_accuracy`, `judgment_correct`, `semantic_grades`: omitted/null — cert cell; no semantic set is declared and the prediction carries no `semantic_claims` block.

## Reasoning quality: 0.85

Strengths: this is the rationale most grounded in the actual record. It reads the chronology off the snapshot (January filing, March receipt, May docketing, June opposition, June 17 distribution for September 28), identifies the band and version it anchors on and pools the correct window, and then argues four concrete downward adjustments, each of which a cert practitioner would recognize: pro se private family dispute; unpublished intermediate opinion with discretionary review denied, so nothing reasoned to review and no conflict alleged; an omnibus question presented bundling five theories, including attacks on federal statutes no court below applied; and the Second Amendment hook already spent by Rahimi, with no pending case to hold for. It states the yardstick it will be scored against and that a no-view answer would restate it, which is the right understanding of the skill score. The uncertainty section is honest and specific (unread brief in opposition, unread lower opinion with the CourtListener search that came back empty, no check for an OT2026 hold candidate), and it discloses declining to read a prior prediction in the directory.

Weaknesses: one record inference looks wrong. The rationale says the respondent "is represented (Seattle counsel address on the docket)"; the decided snapshot I hold lists the respondent as her own attorney with `IsCounselofRecord` false, i.e. apparently pro se. I cannot see the September 16 snapshot the candidate read, and the candidate gave the point little weight, so it costs little. The claim that pro se paid grants from state domestic-relations proceedings are "essentially unobserved" is plausible but asserted rather than drawn from a table the pack publishes, and the originating-court figures quoted are for the whole state-intermediate-court cut, not the family-law slice. The conditional summary-route figure (0.6 given any grant) and the big-case rationale are outside this score.

## Leakage

Forward cell, `leakage.influenced_prediction` = `not_applicable`, `retrieved_outcome_material` = false, `leakage_suspected` = false. Prediction created 2026-09-16, before the 2026-09-28 conference and the 2026-10-05 denial. Log mode `forward`, 21 calls, all `captured`: one CourtListener MCP opinion search for "Pestarino" in the Washington courts returned zero results; two `fedcourts query` calls returned unrelated recent granted and denied rows as a shape check (first with a `ranged corpus reads` line, second served warm). No `retrieved_doc_date`; no `data/qp-topics/` read. The rationale forecasts a denial after a conference still to come and reads nothing resembling an outcome off the snapshot. No sign of a decided case provisioned forward.

## Big case

My independent read: **0.05**. Nominally sweeping question presented, but a pro se private family dispute on an unpublished state opinion, denied silently with no writing.
