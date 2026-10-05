# Evaluation: codex-baseline — Schmidt v. City of Omro (scotus/73363408, evt-petition-disposition)

## Outcome and scoring

Cert-stage cell (`event.yaml` stage `cert`). The petition was distributed once for the September 28, 2026 conference and **denied on October 5, 2026** with no noted dissent (`outcome.json`: `actual_disposition` denied, `actual_granted` 0, `distribution_count` 1).

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.005 − 0)² = 0.000025.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction froze `band: baseline` under `salience_version: sal-v4`, and the statpack's "Segment base rate by salience band (sal-v4)" heading matches. I pooled the bracketed `reached` figures of the `baseline` column over every rendered Term strictly before the case's Term (2025): OT2017–OT2024, resolved-weighted (≈593 grants over n = 11,580, 5.12%). The caption renders 10 of 10 Terms, so the rendered window is the pack's whole window and there is no lookback divergence to flag.
- `brier_skill_score` = 1 − 0.000025 / 0.0512² = 0.9905.
- `vote_accuracy` omitted (cert stage; never scored). No `semantic_grades` (no semantic set on a cert event; `semantic_claims` is null). No opinion slot was staged, which is the ordinary state for a cert denial.

## Reasoning quality: 0.85

The rationale is sound and unusually disciplined about what it does and does not know. Its anchor is exactly the one this cell scores against: the sal-v4 baseline band's bracketed reached rate pooled over OT2017–OT2024 (≈5.12%, n ≈ 11,580), with the whole-docket 2.8% rate and the relist/CVSG terminal cuts correctly set aside as shape-only context. The three downward adjustments are the right ones for this petition. The "conflict" the petition claims is not a conflict on its federal question; the long string of state cases concerns the enforceability of voluntary appeal waivers rather than any duty to advise civil litigants of appeal rights, and the candidate correctly reads them as advocacy rather than opposing holdings. The vehicle is entangled with Wisconsin finality rules and a late notice of appeal. The docket carries no escalation signal. It also notices two things the other candidates handled less carefully: the waiver on the docket is the insurer's and the adjuster's, not necessarily every named respondent's, and the petition's own chronology is internally inconsistent (a reconsideration motion dated after its stated denial).

Two points keep it below the top. First, it never names the two features that most directly explain a near-zero number here: the petitioner is pro se, and the dismissal below rests on a state-law timeliness ground that sits in front of the federal question. It gestures at "possible preservation and state-procedural obstacles" but does not run the argument. Second, the rationale's conditional reasoning that plenary review is "more natural" than a summary route for this petition is a stretch for a novel pro se theory with no lower-court following, though I do not score the claims block and this affects the write-up only as a matter of analytical coherence. The document is also longer than its content requires. None of this is wrong; it is less sharp than the best rationale on this cell.

## Leakage: forward, clean

Log mode `forward`, `result_capture_coverage` 0.875. The prediction was created 2026-09-16, twelve days before the conference and nineteen before the denial, so the case was genuinely open and no outcome existed to retrieve. The 24 logged calls are shell reads of the provisioned record, prompt, schemas and statpack, plus three `web-search` calls (all `unobserved`, so graded on their queries): generic Rule 10, Bowles v. Russell and Court-rules-PDF queries, none naming this case or docket 25-1293. No CourtListener MCP call. One command contains the string `qp-topics` solely as a `find -not -path` exclusion; nothing under that path was read. The candidate's own `retrieval.md` discloses the same calls and reports they returned nothing usable. `retrieved_outcome_material` false, `influenced_prediction` not_applicable, `leakage_suspected` false.

## Big case: 0.03 (my own read)

A pro se civil tort and insurance dispute over a home, dismissed below on state timeliness grounds, asking the Court to announce a new Fourteenth Amendment advisement duty for civil dismissals with no lower-court following and no split. Respondents waived, no amicus, denied without comment. Stakes are personal to the petitioner. The read is formed from the QP, the snapshot and the petition; the predictors' `big_case_score` values sit in the staged `prediction.json` I had to read, so I note that exposure rather than claim it did not happen.

## Retrieval

No retrieval beyond the provisioned inputs and the committed statpack; see the cell's `retrieval.md`.
