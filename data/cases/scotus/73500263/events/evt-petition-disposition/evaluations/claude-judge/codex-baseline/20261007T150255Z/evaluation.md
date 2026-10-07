# Evaluation: codex-baseline — scotus/73500263, evt-petition-disposition

**Stage:** cert (event.yaml `stage: cert`, moment `distribution`). **Mode:** forward.
**Outcome:** `denied` on 2026-10-05, `actual_granted` 0, one distribution, no CVSG, no noted dissent; the order recorded that Justice Alito took no part.

## Scores

| Field | Value | How |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` denied == `actual_disposition` denied |
| `brier_score` | 0.000144 | (0.012 − 0)² |
| `segment_base_rate` | 0.051209 | baseline band, sal-v4, bracketed `reached` pooled over Terms 2017–2024 |
| `base_rate_basis` | `risk_set` | prediction froze `band: baseline` with `salience_version: sal-v4`; the table heading is sal-v4 |
| `brier_skill_score` | 0.945088 | 1 − 0.000144 / 0.051209² |
| `reasoning_quality` | 0.84 | below |

Base rate: the prediction's frozen context carries both a band and a salience version, and the committed `metrics/statpack.md` table "Segment base rate by salience band (sal-v4)" names the same version, so the risk-set figure applies. I pooled the bracketed `reached` figures resolved-weighted over every rendered Term strictly before Term 2025, which is 2017–2024 (the caption says 10 of 10 Terms are rendered, so the rendered window is the pack's full window and no lookback divergence arises). From the unrounded `statpack.json` rows that is 593 / 11,580 = 0.051209; the candidate's own arithmetic reached the same number. `vote_accuracy` is omitted (cert stage). No `semantic_grades` block: no semantic set is declared on a cert event.

## What the prediction got right and wrong

The categorical call and the magnitude were right: a 1.2% grant probability against a 5.1% band rate for a petition that was then denied without a call for a response, on the first order list after the long conference.

The reasoning is the most carefully sourced of the three. It read the published Fourth Circuit opinion through a date-bounded search and used it well: it noted that the panel decided the QDRO as a matter of North Carolina contract interpretation and never announced a Chenery rule (an in-document search for "Chenery" returned nothing), and it found the footnote declining the § 1056(d)(3)(C) argument as first raised on appeal, which directly undercuts the petition's "no waiver problems" assertion (petition p. 39–40, which I confirmed reads "no factual disputes, no waiver problems"). It correctly separated the May distribution and June grant of the sealing motion (25M82) from the cert distribution, so it did not over-count distributions. It also read the petition's split section as describing an intra-circuit inconsistency with Gagliano rather than an engaged inter-circuit split, which matches the petition's own heading ("Creates an Intra-Fourth-Circuit Conflict"). The anchor was computed from the right table, the right figure, and the right Term window, with the terminal relist and CVSG cuts correctly described as shape rather than hazards.

Two weaknesses kept it below the top candidate. It never registers that the petitioner is pro se (the snapshot lists David Gasper as his own attorney, not counsel of record, and the petition is signed "Petitioner Pro Se"); it calls him a "private, paid petitioner," which is true but misses the strongest single negative signal on this docket. And its treatment of Justice Alito's nonparticipation was deliberately agnostic ("I do not convert it into a known recusal on the petition"); that caution is defensible, but a reader of the sealing-motion order would reasonably have expected the same nonparticipation on the petition, which is what happened. Neither affects the disposition call. The declared probability is also the highest of the three, though at 1.2% the difference in Brier is immaterial.

## Leakage

Forward cell, graded `not_applicable`, `retrieved_outcome_material: false`, `leakage_suspected: false`. The log carries a CourtListener search bounded to ca4, docket 24-1959, `filed_before 2025-12-09`, so it could only return the opinion below; the chunked reads and in-document searches are of that opinion. Two web calls are `unobserved` and so graded on their queries, which are Supreme Court Rule 10 wording and the Court's rules PDF, not this case; the candidate reports both returned nothing. Nothing carries a `retrieved_doc_date` on or after 2026-10-05 and nothing seeks this petition's disposition. One shell call contains the string `data/qp-topics/` as a `-not -path` exclusion inside a `find` for `AGENTS.md`; no file under that directory was opened and a listing of files named AGENTS.md outside it cannot reveal membership, so I do not count it as a read of the forbidden path. I note it so a later grep of the log is not misread.

## Big case

My own read, formed from the record before weighing the candidate's: 0.05. A single participant's pension calculation turning on the word "may" in one domestic-relations order, decided below on state contract law, denied with no call for a response and no separate writing. The candidate's 0.24 reads the ERISA notice question as somewhat portable; I think the record shows that question was never actually decided below, which is the candidate's own vehicle finding.
