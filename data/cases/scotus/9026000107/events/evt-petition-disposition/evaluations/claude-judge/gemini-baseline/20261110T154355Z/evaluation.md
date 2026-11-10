# Evaluation — gemini-baseline

Cell: scotus/9026000107 (*Walls v. Prince George's County*, No. 26-107), `evt-petition-disposition`, stage **cert**. Outcome: **denied** on 2026-11-09 after one redistribution (for the 11/6/2026 conference), no CVSG, no noted dissent.

## Scores

- Predicted disposition `denied`, P(grant) = 0.35. `correct` = 1; `brier_score` = (0.35 − 0)² = 0.1225.
- Segment base rate, skill and basis are the harness's stamp (the prediction froze band `baseline` under `sal-v4`); I quote no rate of my own — compare against the stamped segment base rate.
- No vote accuracy (cert stage; votes are never scored here). No semantic grades (cert stage declares no semantic set).

## Reasoning quality (0.35)

Thin rationale. It correctly predicted denial, but its anchor statement — 'baseline' carries 'less than 1%' — reads the terminal-band row rather than the risk-set (`reached`) figure a frozen-band cell faces (~5%), so the starting point is misread. The upward reasons (six amici, CFR after waiver) are the right signals but are not weighed against anything: there is no engagement with the BIO, the unpublished per curiam below, the contested factual record on whether a waiver application was filed, or the weakness of the split, which it overstates as 'two distinct circuit splits' when the Question 1 authorities are largely state intermediate-court decisions. The jump to 35% is asserted, and the 35% dissent-from-denial figure is unsupported. Scored 0.35.

## Predicted reasoning (0.4)

A short, generic document that never states the disposition itself. Central claims: a further distribution (borne out), no CVSG (borne out), a dissent from denial 'plausible' (not borne out, hedged), and grant-branch content (unresolved, conditional). What held is the modal path for any CFR'd paid petition and commits to little a reader could have got wrong. Graded 0.4.

## Leakage

Mode `forward`; `influenced_prediction` = `not_applicable`, `retrieved_outcome_material` = false. Forward cell (snapshot 2026-10-05, cutoff null). Every logged call is unobserved (result_capture_coverage 0.0, an engine shape), so graded on queries: all are reads of the prompt, provisioned case files and metrics/statpack.md, plus writes and validate; no web, MCP, or corpus calls; no qp-topics read. retrieval.md says no retrieval beyond provisioned inputs. No outcome material.

## Big case

My own read: 0.35 — A Fourth Circuit unpublished per curiam in a single-lot well-and-septic dispute raising legislative-exhaustion and prudential-ripeness questions for takings claims; doctrinally meaningful to the land-use bar and drew an organized property-rights amicus slate, but low public salience, and the Court denied silently after one redistribution.
