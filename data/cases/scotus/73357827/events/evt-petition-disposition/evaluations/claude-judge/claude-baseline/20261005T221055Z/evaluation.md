# Evaluation — claude-baseline — scotus/73357827 — evt-petition-disposition

**Cell:** cert stage (`event.yaml` stage `cert`), forward mode. **Outcome:** petition denied 2026-10-05 at the first conference it was distributed for (the 2026-09-28 long conference), one distribution, no call for a response, no CVSG, no noted dissent. `actual_granted` = 0.

## Scores

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.015 − 0)² = 0.000225.
- `segment_base_rate` = 0.0512 (`base_rate_basis` = `risk_set`). The prediction's frozen context carries `band` = `baseline` and `salience_version` = `sal-v4`, and the statpack's *Segment base rate by salience band* heading names `sal-v4`, so the risk-set basis applies. I pooled the bracketed `reached` figure for `baseline`, resolved-weighted, over every rendered Term strictly before the case's Term (OT2025): OT2017 through OT2024, 593 / 11,580. The table caption renders 10 of 10 Terms, so the rendered window is the pack's window and no window divergence arises; the configured ten-Term lookback (OT2015–OT2024) reaches the same eight Terms because the pack holds nothing before OT2017.
- `brier_skill_score` = 1 − 0.000225 / 0.0512² = 0.914.
- No `vote_accuracy`, `judgment_correct`, or `semantic_grades`: cert cell.

## Reasoning quality: 0.90

This is a well-grounded rationale whose structure matched what the Court did. It anchored on the correct risk-set rate (its own pooling, 5.1%, is the number I computed), then discounted it for reasons that each held up:

- It identified the waived response with no call for a response as the single largest discount, and read the long-conference distribution as the Court not being inclined to look further. That is exactly how the petition resolved.
- It checked the petition's claimed circuit split against the Seventh Circuit opinion and the petition's own authorities and found the split concerned different HAVA provisions (provisional ballots, registration lists) than the complaint-procedure section at issue. codex-baseline's independent primary-source check reached the same conclusion, which corroborates the reading.
- It correctly placed the judgment below on Article III standing rather than on the section 1983 question, making QP1 unreachable in this vehicle, and noted the fact-bound, unanimous posture.
- It treated the 2026 cert denials in the Public Interest Legal Foundation cases, reported in the September 15 supplemental brief, as legitimate forward signal on adjacent organizational-standing questions.
- It gave the upward factors (the concurrence's invitation, the DOJ letter, one amicus) a stated, bounded weight rather than ignoring them.

What keeps it short of the top: the claim that *Medina* (2025) "largely" closes the section 1983 route is stated more flatly than the authority supports, and the petitioner-counsel track record is a weak prior the candidate itself flagged as such. Neither affected the direction of the call. The uncertainties section is candid about the one scenario (a post-conference call for a response) that would have made the number too low.

## Leakage

Forward mode, `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. The petition was genuinely pending on 2026-09-16 and was not decided until 2026-10-05, so this was not a mis-provisioned decided case. The log is fully captured. The one dated retrieval (2026-07-07) is an unrelated Wisconsin Supreme Court records case returned by a caption search; the two web fetches are pre-decision filings linked from the provisioned snapshot. Nothing about this petition's disposition was retrieved.

## Big case

My independent read is 0.15, formed before reading the candidate's score. The candidate's own stakes read is recorded on its prediction; I compute no agreement figure.
