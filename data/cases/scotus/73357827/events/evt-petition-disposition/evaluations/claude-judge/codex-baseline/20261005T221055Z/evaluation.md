# Evaluation — codex-baseline — scotus/73357827 — evt-petition-disposition

**Cell:** cert stage (`event.yaml` stage `cert`), forward mode. **Outcome:** petition denied 2026-10-05 at the first conference it was distributed for (the 2026-09-28 long conference), one distribution, no call for a response, no CVSG, no noted dissent. `actual_granted` = 0.

## Scores

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.035 − 0)² = 0.001225.
- `segment_base_rate` = 0.0512 (`base_rate_basis` = `risk_set`). The frozen context carries `band` = `baseline` under `salience_version` = `sal-v4`, matching the statpack table's heading. Pooled bracketed `reached` figure for `baseline`, resolved-weighted, over OT2017–OT2024 (every rendered Term strictly before OT2025): 593 / 11,580. The table renders 10 of 10 Terms, so no window divergence; the configured ten-Term lookback reaches the same eight Terms because the pack holds nothing before OT2017.
- `brier_skill_score` = 1 − 0.001225 / 0.0512² = 0.533.
- No `vote_accuracy`, `judgment_correct`, or `semantic_grades`: cert cell.

## Reasoning quality: 0.75

A careful, well-sourced rationale that reached the right direction but under-adjusted. Its strengths:

- It anchored on exactly the right rate (5.12% from the statpack JSON, the same pooling I used) and correctly refused to re-derive the Term or band from surface cues.
- It did a targeted primary-source check of *Sandusky* and *Crowley* via CourtListener and concluded the asserted split concerns different HAVA provisions than the complaint-procedure claim here, so it discounted the petition's circuit tally. That judgment is sound and matches claude-baseline's independent reading of the Seventh Circuit opinion.
- It read the September 15 supplemental brief, drew the right inference (the newer circuit decisions turn on different injuries, not a square conflict), and treated the reported PILF denials as modest caution rather than a rule.
- It kept clear what was petitioner advocacy versus record fact, including on the DOJ letter.

Its weaknesses: the response waiver with no call for a response was mentioned only as one factor among several "weighing against immediate review," not as the dominant one. On a paid private petition distributed for the long conference without a call for a response, that is the strongest deny signal available, and claude-baseline's treatment of it as the largest discount is the better analysis. The candidate also never obtained the Seventh Circuit opinion (a citation search missed, the govinfo fetch returned nothing), so its account of the standing holding came from the petition; it was candid about that limit. The net result was a number only modestly below the anchor when the posture supported a steeper cut.

## Leakage

Forward mode, `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. The petition was genuinely pending on 2026-09-16 (decided 2026-10-05), so no decided case was provisioned forward. Three web-search rows are `unobserved` and were graded on their queries: the Court's Rules PDF, a search on *Alliance for Hippocratic Medicine*, and the govinfo copy of the Seventh Circuit opinion. None targets this petition's disposition. The captured calls read pre-decision authorities and a pre-decision filing from the snapshot's own URL.

## Big case

My independent read is 0.15, formed before reading the candidate's score. The candidate's own stakes read is recorded on its prediction; I compute no agreement figure.
