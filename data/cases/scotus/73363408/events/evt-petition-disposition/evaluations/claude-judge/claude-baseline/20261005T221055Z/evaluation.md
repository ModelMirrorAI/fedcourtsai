# Evaluation: claude-baseline — Schmidt v. City of Omro (scotus/73363408, evt-petition-disposition)

## Outcome and scoring

Cert-stage cell (`event.yaml` stage `cert`). The petition was distributed once for the September 28, 2026 conference and **denied on October 5, 2026** with no noted dissent (`outcome.json`: `actual_disposition` denied, `actual_granted` 0, `distribution_count` 1).

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.003 − 0)² = 0.000009.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction froze `band: baseline` under `salience_version: sal-v4`, matching the statpack's sal-v4 band table heading. I pooled the bracketed `reached` figures of the `baseline` column over every rendered Term strictly before OT2025 (OT2017–OT2024), resolved-weighted: ≈593 grants over n = 11,580, 5.12%. The caption renders 10 of 10 Terms, so there is no window divergence to flag.
- `brier_skill_score` = 1 − 0.000009 / 0.0512² = 0.9966.
- `vote_accuracy` omitted (cert stage). No `semantic_grades` (cert event, `semantic_claims` null). No opinion slot staged, as expected on a cert denial.

## Reasoning quality: 0.90

This is the strongest rationale on the cell. The anchor is the right one and is shown: the sal-v4 baseline band's bracketed reached rate, tabulated Term by Term for OT2017–OT2024 and pooled to 5.1% over n = 11,580, which is exactly the figure this cell is scored against. The relist, CVSG and originating-court cuts are used for shape only and the Wisconsin District II count (8 of 8 denied) is correctly called too thin to carry weight.

The six adjustments are the right ones and are argued, not asserted. Pro se status and the respondents' waiver are the two features that take most of the anchor away, and the candidate correctly notes that a grant from this posture would almost always run through a call for a response first. The adequate-and-independent-state-ground point is the sharpest observation on the cell: the Wisconsin Court of Appeals dismissed on state timeliness grounds, the Wisconsin Supreme Court denied review without opinion, and the federal advisement theory is the petitioner's explanation for the lateness rather than the ground of decision. The reading of the petition's authorities is accurate: I checked the string cites and they are waiver-enforceability cases, not cases about a judicial duty to advise civil litigants, and the Hunter v. United States reference (a criminal plea-agreement appeal-waiver case) is correctly read as not supplying a GVR hook. The caption oddity (City of Omro in the caption, insurer and adjuster as the responding parties) is read correctly as the docket's real state.

The candidate is also transparent about the limits of its own method: it says plainly that the pro se, waiver and state-ground weights come from general knowledge of the Court's practice rather than from a committed cut, and says how to discount it if a future cut disagrees. That is the right epistemic posture.

Two small deductions. The remark that "the petition's own appendix listing suggests the federal claim was first raised in the petition for review" is speculative and is offered as a vehicle problem without the appendix in hand; it is hedged with "suggests," but it is still a factual inference the provisioned record does not support. And the rationale leans on the conditional that any grant would be a summary route (0.6) while simultaneously saying no intervening decision supplies a GVR hook, which is slightly in tension; I do not score the claims block, and this enters only as a note on the write-up's internal coherence.

## Leakage: forward, clean

Log mode `forward`, `result_capture_coverage` 1.0. The 19 calls are shell reads of the prompt, the provisioned record, the petition text, the schema and the statpack, plus one captured corpus priors query (`fedcourts query --court scotus --era 2020s --limit 8`) that the candidate's `retrieval.md` reports returned recency-ranked rows unlike this petition and that did not inform the number. No web search and no CourtListener MCP call. The prediction (created 2026-09-16) predates the October 5 denial, no `retrieved_doc_date` falls on or after it, and the reasoning cites only pre-cutoff docket facts (the January filing, the booklet-format extension, the May 27 waiver, the July 1 distribution). `retrieved_outcome_material` false, `influenced_prediction` not_applicable, `leakage_suspected` false.

## Big case: 0.03 (my own read)

A pro se civil tort and insurance dispute over a home, dismissed below on state timeliness grounds, asking the Court to announce a new Fourteenth Amendment advisement duty for civil dismissals with no lower-court following and no split. Respondents waived, no amicus, denied without comment. Stakes are personal to the petitioner. Formed from the QP, the snapshot and the petition; the predictors' `big_case_score` values sit in the staged `prediction.json` I had to read, so I note that exposure rather than claim it did not happen.

## Retrieval

No retrieval beyond the provisioned inputs and the committed statpack; see the cell's `retrieval.md`.
