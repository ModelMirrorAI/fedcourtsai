# Evaluation of codex-baseline — Bell v. Gilley, No. 25-1141 (scotus/73281628), evt-petition-disposition

## Outcome and scores

Cert-stage cell. The petition was **denied** on 2026-10-05 after two distributions (April 15 for the May 1 conference, which never reached consideration because a response was requested April 22; August 5 for the September 28 long conference), with no noted dissent.

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.38 − 0)² = **0.1444**.
- `segment_base_rate` = **0.1724**, basis `risk_set`. The prediction's frozen context carries `band: elevated` and `salience_version: sal-v4`, which matches the heading of the statpack's *Segment base rate by salience band (sal-v4)* table. I pooled the bracketed `reached` figure for `elevated`, weighted by its `n`, over every rendered Term strictly before the case's Term 2025: 2017–2024 (17.5/400, 15.9/347, 13.8/334, 16.1/397, 20.5/342, 19.0/300, 17.5/354, 17.9/336), giving 17.24% over a weighted n of 2,810. The caption says the pack renders 10 of 10 Terms, so the rendered window is the whole pack and there is no lookback divergence to flag.
- `brier_skill_score` = 1 − 0.1444 / 0.1724² = **−3.86**. The candidate's number was far worse than the naive band rate on this denial.

## Reasoning quality: 0.60

What the analysis did well. The candidate read all three provisioned documents, legitimately fetched the pre-decision reply brief, verified Azar v. Garza through CourtListener, and computed the anchor exactly as the contract asks (17.24% over 2,810, prior Terms only, same salience version). It correctly identified the posture as a Munsingwear vacatur request where any grant would be a `gvr`, correctly refused to treat the two distributions as two conference survivals, and correctly noted the pseudo-relist caveat the statpack itself raises. Its account of the opposition's arguments (no independent certworthiness, jurisdictional dismissal, petitioner-caused mootness) was accurate and complete, and it was candid that 38% was a judgmental synthesis with no matched subgroup in the pack.

Where it went wrong given the outcome. It more than doubled the anchor on two signals it itself discounted: the "cheap" summary remedy and a response request that it conceded "is not four votes for relief." It read the reply as "materially improving Bell's answer" and treated the government's categorical objections as mere litigating positions, but the realized denial is consistent with the Solicitor General's equitable arguments (self-caused mootness via the petitioner's own early-termination motion, no certworthiness absent mootness) carrying the day, exactly the downward factors the candidate listed and then under-weighted. The upward adjustment from 17% to 38% was not supported by anything in the pack and rested on a reading of the equities the Court did not share. The secondary forecasts (no CVSG, summary route if granted, modest relist and dissent chances) were sensible, but those are scored in code and do not enter this grade.

Net: well-sourced and well-structured analysis whose calibration moved too far from the anchor on signals the candidate had already identified as weak.

## Leakage

Forward mode; `influenced_prediction` = `not_applicable`, `retrieved_outcome_material` = false, `leakage_suspected` = false. I checked that the case was genuinely open when predicted: the prediction was created 2026-09-17 and the denial came 2026-10-05. The log's only external material is the August 5, 2026 reply brief, two Azar v. Garza lookups, and two unobserved web-search rows whose queries name only Azar v. Garza (graded on the query, as the capture marker requires). No `retrieved_doc_date` is on or after the resolution date, and the reasoning treats the September 28 conference as upcoming. The candidate's own flags file is not staged, so its clean disclosure in `reasoning.md` and `retrieval.md` is the disclosure channel I could see; it is consistent with the log.

## Big case

My own read is 0.18: a mootness-vacatur request on which no opinion could issue, with the only stake being whether one published circuit precedent stays on the books. The candidate's 0.34 is higher than mine; I supply only the independent read, not an agreement number.
