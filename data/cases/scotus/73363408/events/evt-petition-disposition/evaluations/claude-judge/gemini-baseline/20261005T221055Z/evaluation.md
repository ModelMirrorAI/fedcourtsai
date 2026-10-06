# Evaluation: gemini-baseline — Schmidt v. City of Omro (scotus/73363408, evt-petition-disposition)

## Outcome and scoring

Cert-stage cell (`event.yaml` stage `cert`). The petition was distributed once for the September 28, 2026 conference and **denied on October 5, 2026** with no noted dissent (`outcome.json`: `actual_disposition` denied, `actual_granted` 0, `distribution_count` 1).

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.001 − 0)² = 0.000001.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction froze `band: baseline` under `salience_version: sal-v4`, matching the statpack's sal-v4 band table heading. I pooled the bracketed `reached` figures of the `baseline` column over every rendered Term strictly before OT2025 (OT2017–OT2024), resolved-weighted: ≈593 grants over n = 11,580, 5.12%. The caption renders 10 of 10 Terms, so there is no window divergence to flag.
- `brier_skill_score` = 1 − 0.000001 / 0.0512² = 0.9996.
- `vote_accuracy` omitted (cert stage). No `semantic_grades` (cert event, `semantic_claims` null). No opinion slot staged, as expected on a cert denial.

## Reasoning quality: 0.55

The call was right and the direction of every adjustment was right, but the rationale is thin and carries two errors of method and fact.

The anchor is wrong in kind. The candidate anchored on the OT2025 `baseline` row's bracketed 3.9%. That is the case's own Term: the live, still-incomplete slice, which the statpack's own footnote tells a predictor to exclude, and which this cell is not scored against (the scored baseline is the pooled OT2017–OT2024 reached rate, 5.1%). The error is harmless to the number only because the candidate then moved more than an order of magnitude off the anchor, but a rationale that starts from the wrong population is weaker evidence of a sound process.

The factual slip: it says "the respondent (an insurance company and the City of Omro, Wisconsin) has waived its right to respond." The docket's waiver is from Employers Mutual Casualty and its adjuster only; nothing in the record shows the City waived. The reading that an unopposed petition "further confirms" non-viability is also overstated: a waiver is routine and the Court calls for a response when it is interested, so the waiver is weak evidence on its own.

What it gets right is the core: a pro se petition from a state civil procedural dismissal, an idiosyncratic question with no split and no recurring national issue, reading as a fact-bound grievance. Those are the right reasons for a near-zero number. But the document does not engage with the petition's actual arguments (the criminal-advisement analogy, the string of waiver cases, the Hunter reference), does not identify the adequate-and-independent-state-ground problem that most directly defeats the vehicle, and offers no account of why 0.001 rather than 0.01 or 0.003 beyond "negligible." A one-paragraph rationale that reaches the right answer for broadly right reasons, with a mis-set anchor and a misstatement of the docket, sits in the middle of the scale.

## Leakage: forward, clean

Log mode `forward`, `result_capture_coverage` 0.0: every one of the 22 calls is `unobserved`, so each is graded on its query alone and none is credited as having returned nothing. The queries are file-reads and directory listings of the provisioned record, the prompt, the schema and the statpack; one corpus priors query (`fedcourts query --court scotus --decided-before 2026-09-16 --limit 5 --full`, a generic recent-resolution pull not keyed to this case); and the output writes. No web search, no CourtListener MCP call, no query naming this case or docket 25-1293. The prediction (created 2026-09-16) predates the October 5 denial, and a recency pull run on September 16 could not have carried a disposition entered on October 5. The reasoning cites only the provisioned docket. `retrieved_outcome_material` false, `influenced_prediction` not_applicable, `leakage_suspected` false.

## Big case: 0.03 (my own read)

A pro se civil tort and insurance dispute over a home, dismissed below on state timeliness grounds, asking the Court to announce a new Fourteenth Amendment advisement duty for civil dismissals with no lower-court following and no split. Respondents waived, no amicus, denied without comment. Stakes are personal to the petitioner. Formed from the QP, the snapshot and the petition; the predictors' `big_case_score` values sit in the staged `prediction.json` I had to read, so I note that exposure rather than claim it did not happen.

## Retrieval

No retrieval beyond the provisioned inputs and the committed statpack; see the cell's `retrieval.md`.
