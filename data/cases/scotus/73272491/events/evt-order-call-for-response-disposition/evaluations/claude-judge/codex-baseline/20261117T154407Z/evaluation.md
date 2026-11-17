# Evaluation - codex-baseline

**Cell:** scotus/73272491, `evt-order-call-for-response-disposition` (cert stage, response-requested moment). **Outcome:** petition denied 2026-11-16, after one post-response distribution, with no noted dissent.

## Scores

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.20 - 0)^2 = 0.04.
- No vote score (cert cell). Segment base rate, skill and claim scores are the harness's and are left unset.

## Reasoning (`reasoning_quality` 0.55)

Methodologically careful and accurate about the record: it reads the docket correctly (two amicus briefs, June 2 distribution for June 18), anchors on the risk-set figure for the frozen band over strictly-prior Terms, explains why the relist, CVSG and amicus cuts are shape checks rather than multipliers, and distinguishes a routine post-response redistribution from a true relist. It is candid that the move from the anchor to 20% is judgment.

The judgment is where it falls short. A roughly fourfold lift rests on the call for a response, amicus support and doctrinal tension - but the document itself lists the countervailing facts (no split, repeated prior denials of the same request, summary order below, an overruling ask) and then gives them too little weight. The prior denials on the identical question are the single most informative fact in the petition and are treated as one consideration among several. The vehicle discussion leans favourable (issue preserved and decided below) without pricing in that the same was true of earlier denied petitions.

It also chose not to refresh the docket in a forward cell, forgoing the brief in opposition that was available by its run date; it says so openly, and that is a permissible choice, but it left its stated main uncertainty (the government's position) unresolved when it could have been resolved. The result was the least sharp probability of the three on an outcome that was the base case.

## Predicted reasoning (`predicted_reasoning_quality` 0.80)

Central claims: denial after the response; denial at the first conference that can consider the completed papers rather than after relists; an autumn 2026 decision; no CVSG; no separate writing as the likeliest outcome. Every one was borne out, and they were committed to from the June vantage without sight of the later docket, so the procedural path and timing were genuinely at risk. It stays short of the top because the stated reason for denial cannot be checked against a bare order and because each call was the conventional expectation for the posture, hedged with fallback clauses (extensions possibly into early 2027).

## Leakage

Forward mode; prediction created 2026-10-29, resolution 2026-11-16. The candidate did not retrieve this case's docket. Two web-search rows are `unobserved` and are graded on their queries, which seek the Court's Rule 10 text, not this case. One CourtListener lookup for Erlinger was throttled. `retrieved_outcome_material` false, `not_applicable`.

## Big case

Own read 0.35: institutionally meaningful question (overruling Libretti), low public salience, and a routine silent denial in the event.
