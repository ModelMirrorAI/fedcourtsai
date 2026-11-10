# Evaluation — codex-baseline

Cell: scotus/9026000107 (*Walls v. Prince George's County*, No. 26-107), `evt-petition-disposition`, stage **cert**. Outcome: **denied** on 2026-11-09 after one redistribution (for the 11/6/2026 conference), no CVSG, no noted dissent.

## Scores

- Predicted disposition `denied`, P(grant) = 0.22. `correct` = 1; `brier_score` = (0.22 − 0)² = 0.0484.
- Segment base rate, skill and basis are the harness's stamp (the prediction froze band `baseline` under `sal-v4`); I quote no rate of my own — compare against the stamped segment base rate.
- No vote accuracy (cert stage; votes are never scored here). No semantic grades (cert stage declares no semantic set).

## Reasoning quality (0.75)

Strong, disciplined rationale. Same correct anchor (bracketed `reached` `baseline`, sal-v4, pooled 2017–2025 from the JSON counts: 638/12,720 ≈ 5.0%), explicitly declined to multiply terminal relist/CVSG cuts as transition probabilities, and treated contested facts as advocacy. It verified Pakdel's actual holding rather than trusting either brief, and correctly identified the decisive tension — finality vs. exhaustion on a disputed factual record — as the reason the case could be a fact-bound vehicle; that is the most plausible reading of a silent denial. Like claude-baseline, the uplift from ~5% to 22% is judgmental and somewhat generous, which the candidate acknowledges. Scored 0.75.

## Predicted reasoning (0.75)

Central claims: denial, one further distribution, a late-October/November disposition, no CVSG, silent denial. All borne out, and the timing call (one more distribution, decision in late Oct/Nov) was specific and exactly right where a hold-for-companion path was a live alternative. Much of the rest (no CVSG, silent denial) is the modal path for any paid petition, which keeps it below the top anchor. Graded 0.75.

## Leakage

Mode `forward`; `influenced_prediction` = `not_applicable`, `retrieved_outcome_material` = false. Forward cell (snapshot 2026-10-05, cutoff null). All calls ran 2026-10-06. External retrieval was limited to Pakdel (594 U.S. 474) via CourtListener and two web calls on Pakdel/Court rules that returned nothing usable (unobserved rows, graded on their queries: none targets this case). The candidate states it made no search for this case, its docket, or the companion petition. No qp-topics read (its find excluded the path). No outcome material.

## Big case

My own read: 0.35 — A Fourth Circuit unpublished per curiam in a single-lot well-and-septic dispute raising legislative-exhaustion and prudential-ripeness questions for takings claims; doctrinally meaningful to the land-use bar and drew an organized property-rights amicus slate, but low public salience, and the Court denied silently after one redistribution.
