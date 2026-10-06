# Evaluation — gemini-baseline — scotus/73357827 — evt-petition-disposition

**Cell:** cert stage (`event.yaml` stage `cert`), forward mode. **Outcome:** petition denied 2026-10-05 at the first conference it was distributed for (the 2026-09-28 long conference), one distribution, no call for a response, no CVSG, no noted dissent. `actual_granted` = 0.

## Scores

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.15 − 0)² = 0.0225.
- `segment_base_rate` = 0.0512 (`base_rate_basis` = `risk_set`). The frozen context carries `band` = `baseline` under `salience_version` = `sal-v4`, matching the statpack table's heading. Pooled bracketed `reached` figure for `baseline`, resolved-weighted, over OT2017–OT2024 (every rendered Term strictly before OT2025): 593 / 11,580. The table renders 10 of 10 Terms, so no window divergence; the configured ten-Term lookback reaches the same eight Terms because the pack holds nothing before OT2017.
- `brier_skill_score` = 1 − 0.0225 / 0.0512² = −7.58. The forecast was nearly three times the band rate on a petition that was denied without any of the escalation signals it predicted, so it scores well below the naive baseline.
- No `vote_accuracy`, `judgment_correct`, or `semantic_grades`: cert cell.

## Reasoning quality: 0.30

The rationale named the right band and an approximately right anchor (about 5%), and it did retrieve and read the Seventh Circuit opinion. From there the analysis went wrong in ways the outcome exposed:

- It took the petition's characterization of a "deep and acknowledged" circuit split at face value. Both other candidates checked the cited authorities and found the split concerns provisional-ballot and registration-list provisions, not the complaint-procedure section at issue. This rationale shows no such check.
- It read the respondents' waiver as a reason the Court would "highly likely" call for a response or a CVSG. The Court had already distributed the petition for the long conference without calling for a response, which is the standard signal pointing the other way. The outcome confirms it: denied at the first conference, no CFR, no CVSG.
- It treated the DOJ letter, known only through the petitioner's description, as "strong federal interest" without that qualification, and inferred a dissent from denial from "conservative justices" on an election-integrity theory rather than from anything in the record. No dissent was noted.
- The vehicle problem, a unanimous fact-bound standing dismissal that leaves QP1 unreachable, is acknowledged in one sentence and said to temper the probability "slightly." It is the central fact about this petition's grant prospects.

The write-up is also brief and lists no inputs, sources, or uncertainties, so a reader cannot tell what in the retrieved opinion informed the number. The score reflects an analysis that leaned on petitioner advocacy where the record offered checkable counter-evidence, and inverted the most informative docket signal.

## Leakage

Forward mode, `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. The petition was genuinely pending on 2026-09-16 (decided 2026-10-05), so no decided case was provisioned forward. The log's result-capture coverage is 0.0, an engine's standing shape rather than a defect, so each call was graded on its query: one caption search for the Seventh Circuit opinion, two chunk reads of it, and local reads of the provisioned record and statpack. No query reaches for this petition's disposition, and the reasoning treats the petition as pending.

## Big case

My independent read is 0.15, formed before reading the candidate's score. The candidate's own stakes read is recorded on its prediction; I compute no agreement figure.
