# Evaluation of codex-baseline — scotus/73292885, evt-petition-disposition

## Cell and outcome

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`), forward mode. Pestarino v. Pestarino, No. 25-1249: a paid, pro se petition from an unpublished Washington Court of Appeals decision affirming a civil protection order; distributed once (June 17, 2026) for the September 28, 2026 long conference. Outcome: **denied** on October 5, 2026, `actual_granted` 0, no noted dissent, one distribution. No opinion slot is staged, as expected on a cert cell.

## Scores

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.012 − 0)² = **0.000144**.
- `segment_base_rate` = **0.0512**, `base_rate_basis` = `risk_set`. The prediction froze `band: baseline` under `salience_version: sal-v4`, matching the statpack heading, so the bracketed `reached` figure applies, pooled resolved-weighted over the rendered Terms strictly before Term 2025 (OT2017–OT2024; the caption renders 10 of 10 Terms, so no lookback divergence): 593.0 / 11,580 = 5.12%. The candidate pooled the same window from the pack's unrounded JSON fields and reported 5.1209%; my table-derived figure agrees to the rounding.
- `brier_skill_score` = 1 − 0.000144 / 0.0512² = **0.945**.
- `vote_accuracy`, `judgment_correct`, `semantic_grades`: omitted/null — cert cell; no semantic set is declared and the prediction carries no `semantic_claims` block.

## Reasoning quality: 0.85

Strengths: the anchor is exactly right in kind and in window — the reached figure under the matching sal-v4 heading, every rendered Term strictly before the case's own, with the terminal percentage and the whole-docket disposition table explicitly set aside as the wrong populations. The rationale separates terminal tables (relist count, CVSG status) from the forward hazards it is actually forecasting, which is the distinction most rationales blur. It refuses to invent the unavailable brief in opposition, declines to infer a procedural defect from the odd filing chronology without evidence, and states what it did not verify (preservation, the lower opinion, whether the opinion was published). The one authority it leans on, Rahimi's reservation of the due-process question, was retrieved and pinned to a slip-opinion page rather than recalled, and is used correctly: it explains why a properly framed procedural challenge could matter while denying that this petition supplies such a vehicle. The downward adjustment from 5.1% to 1.2% is argued from the record (omnibus question, no identified square conflict, contested premises) and lands close to what a seasoned reader would give. The conditional-versus-unconditional framing of the summary-route figure is stated, which many rationales omit.

Weaknesses: the document is long relative to its content and spends paragraphs on freshness and vintage disclaimers that do not move the number. It engages less with the concrete record than claude-baseline (it does not note that the state supreme court denied discretionary review or that the petition is pro se, both of which bear on vehicle quality), and it characterizes the opposition as having been filed without saying whether the respondent was counseled. None of this is an error; it is a rationale that is careful about its limits rather than about the docket. The stakes score of 0.45 is high for a case that resolved as a silent pro se denial, but that figure is graded by the panel elsewhere and does not enter this number.

## Leakage

Forward cell, `leakage.influenced_prediction` = `not_applicable`, `retrieved_outcome_material` = false, `leakage_suspected` = false. Prediction created 2026-09-16, before the 2026-09-28 conference and the 2026-10-05 denial. Log mode `forward`, 32 calls, coverage 0.78: the seven web-search rows are `unobserved` and graded on their queries — Rahimi, Rule 10, 18 U.S.C. 2265, and one attempt to open the brief-in-opposition PDF already named in the provisioned documents manifest (a pre-decision filing, not outcome material). CourtListener calls fetched only the 2024 Rahimi opinion. No `retrieved_doc_date`; no `data/qp-topics/` read. The rationale states that it did not retrieve the docket's current state and knew no outcome, and it forecasts a denial after a conference still to come. No sign of a decided case provisioned forward.

## Big case

My independent read: **0.05**. Nominally sweeping question presented, but a pro se private family dispute on an unpublished state opinion, denied silently with no writing.
