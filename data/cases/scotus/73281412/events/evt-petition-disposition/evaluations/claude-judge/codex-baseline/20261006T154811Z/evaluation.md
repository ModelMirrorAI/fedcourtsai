# Evaluation of codex-baseline — scotus/73281412, evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`). The petition in No. 25-1128, Alexander v. Philip R. Taft Psy D and Associates, was **denied on October 5, 2026** after the September 28 long conference, with no noted dissent from denial and no further relist (`outcome.json`: `actual_disposition` denied, `actual_granted` 0, `distribution_count` 2).

- `correct` = 1: the candidate predicted `denied`.
- `brier_score` = (0.12 − 0)² = **0.0144**.
- `segment_base_rate` = **0.1722**, basis `risk_set`. The prediction froze `band: elevated` under `salience_version: sal-v4`, matching the statpack's sal-v4 band table heading. I pooled the bracketed `reached` figure for `elevated` over Terms 2017–2024 (weighted n = 2,810; 484.0 weighted grants), the full strictly-prior window the pack renders, which coincides with the in-code ten-Term lookback.
- `brier_skill_score` = 1 − 0.0144 / (0.1722)² = **0.515**. Comfortably above the baseline.

No `vote_accuracy`, `judgment_correct`, or `semantic_grades` on a cert cell. `claim_scores` is the harness's.

## Reasoning quality: 0.80

What drove the grade:

- **Precise, correctly sourced anchor.** The candidate pooled the sal-v4 elevated reached rate from the statpack JSON for Terms 2017–2024 (484 / 2,810 = 17.22%), explicitly excluded the case's own Term and later rows, and explained why the reached rate rather than the terminal or whole-docket rate is the right population. This is the cleanest base-rate handling of the three.
- **Right reading of the procedural signal.** It saw that the first distribution preceded the response request and refused to count the request and the resulting redistribution as two independent signals.
- **Good epistemic discipline on the oppositions.** It summarized the Taft brief's vehicle arguments (unchallenged deliberate-indifference and housing-authority grounds, the alternative suicide-precaution rationale, open qualified-immunity and Monell issues) while labelling them as respondents' arguments rather than findings, and noted that undecided defenses are not independent appellate holdings. That is the correct posture toward a BIO.
- **Useful, well-handled precedent retrieval.** It fetched Taylor v. Riojas and distinguished it accurately (convicted prisoner, Eighth Amendment, qualified immunity at summary judgment, versus pretrial detainee dismissed on the pleadings), using it to keep the number above the unselected-petition level without overreading it.

What held it back:

- **Less substantive engagement with the questions presented than claude-baseline.** It characterizes QP 1 as weakened by the opinion's case-specific qualification but does not say what the Fifth Circuit actually held or why the petition's framing misreads it; the analysis stays one level above the record.
- **The 0.12 is somewhat generous for an analysis that found no clean split and multiple vehicle obstacles**, and the document does not say what would move it toward the lower end. The upward counterweights are listed rather than weighed.
- A note that "the event omits an explicit stage" does not match the committed `event.yaml`, which carries `stage: cert`; this may reflect the record as staged at prediction time and is not penalized.

The forecast document (`predicted_reasoning.md`) was read for context only and is not scored.

## Leakage

Mode `forward`; `influenced_prediction` = `not_applicable`; `retrieved_outcome_material` = false; `leakage_suspected` = false. The prediction was made September 18, 2026, seventeen days before the denial. Log coverage is 0.93: two web-search rows are `unobserved`, so I graded them on their queries, which name Taylor v. Riojas and Rule 10 and not this petition. The captured CourtListener calls fetch Taylor v. Riojas only. The candidate's own retrieval note says it made no search for this case or its outcome, and the log bears that out. No `data/qp-topics/` read. The case was not mis-provisioned forward.

## Big case

My independent read is 0.28 (see `big_case.notes`). The candidate's own stakes score was visible in the staged `prediction.json` when I formed mine; my read rests on the record described in the notes.
