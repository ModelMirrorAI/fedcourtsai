# Evaluation of codex-baseline — Patterson v. Michigan, No. 25-1263 (evt-petition-disposition)

**Stage:** cert (event.yaml `stage: cert`, `moment: distribution`). **Outcome:** petition denied on 2026-10-05 after a single distribution for the 2026-09-28 conference; no CVSG, no noted dissent. **Mode:** forward.

## Scores

| Field | Value | Basis |
| --- | --- | --- |
| correct | 1 | `predicted_disposition` denied = `actual_disposition` denied |
| brier_score | 0.000025 | (0.005 − 0)² |
| segment_base_rate | 0.0512 | baseline band, sal-v4, risk-set |
| base_rate_basis | risk_set | prediction froze `band: baseline` with `salience_version: sal-v4`; the statpack table heading is sal-v4 |
| brier_skill_score | 0.9905 | 1 − 0.000025 / 0.0512² |
| reasoning_quality | 0.88 | see below |

The base rate pools the bracketed `reached` baseline figures over the Terms the table renders strictly before this case's Term 2025, which is 2017–2024 (the table renders all ten Terms the pack holds, so the rendered window and the in-code lookback coincide and no window divergence needs flagging). Exact numerators from `metrics/statpack.json` (`prefix_est_grant_rate × prefix_weighted_resolved`) sum to 593 grants over a weighted reached denominator of 11,580, a pooled rate of 0.05121, recorded as 0.0512. `vote_accuracy` is omitted: cert cell, never scored.

## What the prediction got right

The call was right and the number was confidently low, which the outcome rewards. The rationale is the strongest of the three in two respects. It anchors on exactly the right table and population (baseline band, reached figures, prior Terms only, the private-petitioner class), and computes the pooled rate from the JSON rather than from rounded percentages, with the arithmetic shown. Its adjustment then rests on the affirmative content of the petition rather than on docket silence: the interlocutory posture (verified against Cox Broadcasting through CourtListener, with the honest caveat that Cox recognizes exceptions and the petition argues none), the individualized first question, the absence of any asserted conflict, and the disconnect between the requested numeric THC threshold and a fair-notice argument. Each of those reads the petition correctly. The explicit statement that the Michigan appellate denials are pre-SCOTUS history and not outcome material is the right discipline for a forward cell.

## Where it is weaker

The document is longer than its content needs and spends a fair amount of text on provenance hedging (statpack commit vintage, snapshot freshness, the `uv` cache) that does not move the analysis. The relist-bucket and CVSG-cut discussion is explicitly set aside as not usable, which is correct but makes the section mostly a demonstration that the author knows what not to do. The move from 5.1% to 0.5% is stated as judgmental, and no intermediate reasoning says why the combination lands at a tenth of the anchor rather than a fifth or a fiftieth; that is the ordinary condition of these forecasts, but a stronger version would have tied the size of the cut to the relist-0 and originating-court shapes it chose not to use. None of this is an error.

## Leakage

Forward cell. The log's three web calls are uncaptured and are graded on their queries, which were Supreme Court Rule 10 and the Rules PDF, generic authority rather than this case. The two captured CourtListener calls retrieved a 1975 precedent. No `retrieved_doc_date` on or after 2026-10-05 and no query reaching this docket's later history. A `find` command excluded `data/qp-topics` by path and read nothing under it. `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`.

## Big case

My own read, formed before consulting the candidate's score, is 0.08: an interlocutory, fact-bound state OWI prosecution with no reasoned opinion below, no response, and a bare denial. The candidate's 0.32 weighs the hypothetical reach of a national THC-notice rule more heavily than I would for a vehicle that could not plausibly have produced one, but the rationale states that distinction clearly.
