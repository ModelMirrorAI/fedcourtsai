# Evaluation: claude-baseline — scotus/73500263, evt-petition-disposition

**Stage:** cert (event.yaml `stage: cert`, moment `distribution`). **Mode:** forward.
**Outcome:** `denied` on 2026-10-05, `actual_granted` 0, one distribution, no CVSG, no noted dissent; the order recorded that Justice Alito took no part.

## Scores

| Field | Value | How |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` denied == `actual_disposition` denied |
| `brier_score` | 0.0001 | (0.01 − 0)² |
| `segment_base_rate` | 0.051209 | baseline band, sal-v4, bracketed `reached` pooled over Terms 2017–2024 |
| `base_rate_basis` | `risk_set` | prediction froze `band: baseline` with `salience_version: sal-v4`; the table heading is sal-v4 |
| `brier_skill_score` | 0.961866 | 1 − 0.0001 / 0.051209² |
| `reasoning_quality` | 0.88 | below |

Base rate: the prediction's frozen context carries both a band and a salience version, and the committed `metrics/statpack.md` table "Segment base rate by salience band (sal-v4)" names the same version, so the risk-set figure applies. I pooled the bracketed `reached` figures resolved-weighted over every rendered Term strictly before Term 2025, which is 2017–2024 (the caption says 10 of 10 Terms are rendered, so no lookback divergence arises). From the unrounded `statpack.json` rows that is 593 / 11,580 = 0.051209; the candidate's hand pooling of the rendered percentages (about 5.1%, n ≈ 11,580) agrees. `vote_accuracy` is omitted (cert stage). No `semantic_grades` block: no semantic set is declared on a cert event.

## What the prediction got right and wrong

The call and the number were right, and the reasoning is the strongest of the three. It identified every docket signal that mattered and got each one from the record: the petitioner is pro se here though represented below (the snapshot lists him as his own attorney, not counsel of record; the petition is signed "Petitioner Pro Se"), the respondent waived on June 11 (represented by an ERISA defense firm), a single distribution for the September 28 conference, no amicus, no CVSG. It correctly separated the sealing-motion distribution from the cert distribution. It read the Fourth Circuit opinion and drew the two vehicle points precisely: the panel decided a state-law contract question de novo and never addressed a Chenery or § 503 post-hoc-rationale problem, and the § 1056(d)(3)(C) theory underlying QP 2 was declined below as first raised on appeal (footnote 5). It also read the petition's split section accurately: the petition itself pitches an intra-Fourth-Circuit conflict with Gagliano, which I confirmed from the petition's heading, so the inter-circuit "split" is asserted rather than engaged. The recusal inference from the sealing-motion order was borne out: the denial order records the same nonparticipation.

The anchor was taken from the right table and figure, pooled over the right Terms, and the terminal relist and CVSG cuts were correctly described as understating the forward hazard. The landing paragraph gives an explicit floor (about 0.005) with a reason, which is the kind of calibration discipline the number should rest on.

Minor reservations. The "$385.26 per month" stake does not appear in the petition text; I take it to come from the opinion below, which the candidate read but which is not in the record, so I could not verify it. The statement that "roughly a quarter of the paid segment ever sees a second distribution" is plausible from the relist table but was not shown. Neither affects the analysis. The candidate also disclosed that an earlier run on this event existed and that it did not read it, which is the right disclosure.

## Leakage

Forward cell, graded `not_applicable`, `retrieved_outcome_material: false`, `leakage_suspected: false`. The log's external calls are two `fedcourts query` runs over 2020s SCOTUS rows (the single captured `retrieved_doc_date`, 2025-02-11, belongs to a returned corpus row, not this case), one CourtListener opinion search for "Gasper EIDP" restricted to ca4 opinions (the captured result is dated 2025-12-08, the opinion below), and one chunked read of that opinion. No web searches, nothing dated on or after 2026-10-05, nothing that could reach this petition's disposition, nothing naming `data/qp-topics/`. The candidate's retrieval note matches the log.

## Big case

My own read, formed from the record before weighing the candidate's: 0.05. A single participant's pension calculation turning on the word "may" in one domestic-relations order, decided below on state contract law, denied with no call for a response and no separate writing. The candidate's 0.05 is in the same place.
