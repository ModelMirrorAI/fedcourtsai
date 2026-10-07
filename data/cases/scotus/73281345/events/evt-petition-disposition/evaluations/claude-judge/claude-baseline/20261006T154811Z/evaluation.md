# Evaluation — claude-baseline

**Cell.** Cert stage (`event.yaml` stage `cert`, moment `distribution`), Holly Ann Elkins v. United States, No. 25-1061, Term 2025. Outcome: petition **denied** on 2026-10-05 after two distributions, no CVSG, no noted dissent (`outcome.json`: `actual_disposition` `denied`, `actual_granted` 0). The candidate's prediction ran forward on the 2026-09-17 snapshot.

## Scores

| Field | Value | How |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` `denied` == `actual_disposition` `denied` |
| `brier_score` | 0.0049 | (0.07 − 0)² |
| `segment_base_rate` | 0.1722 | elevated band, bracketed `reached` figure, pooled resolved-weighted over Terms 2017–2024 |
| `base_rate_basis` | `risk_set` | frozen `context.band` `elevated` with `context.salience_version` `sal-v4`; the statpack table heading names `sal-v4` |
| `brier_skill_score` | 0.835 | 1 − 0.0049 / (0.1722 − 0)² |
| `reasoning_quality` | 0.88 | see below |

**Base rate detail.** The prediction's frozen context carries both a band (`elevated`) and a salience version (`sal-v4`), and the committed `metrics/statpack.md` "Segment base rate by salience band (sal-v4)" table matches that version, so the risk-set basis applies. The table renders all 10 Terms the pack holds (2017–2026); the Terms strictly before 2025 are 2017–2024, eight rows. Pooling the bracketed `reached` elevated figures by their `n` (from `statpack.json`'s `prefix_est_grant_rate` × `prefix_weighted_resolved`): 484 / 2810 = 0.17224. The shipped in-code lookback is 10 Terms, which would reach back to 2015, but the pack holds nothing before 2017, so the pack-bounded window and the rendered window coincide and no divergence needs flagging. Vote fields are omitted: a cert cell's votes are never scored.

## What the prediction got right and wrong

The candidate called the denial at 7% against a 17% anchor, with a 0.7 confidence, and the petition was denied without a relist or a writing. Its procedural forecasts (denial at or just after the September 28 long conference, no further distribution as the modal path, no CVSG, no separate writing) all matched the record. The forecast document and the claims block are not scored here; they are read only for context.

## Reasoning quality (0.88)

Strengths that drove the number:

- **Correct anchor, correctly characterized.** It pooled the bracketed reached elevated figure over the eight prior Terms to about 17%, named it as the yardstick the cell is scored against, and then explained in order why it sat below it.
- **The sharpest account of the procedural signal among the three.** It recognized that the band was earned by a call-for-response redistribution rather than a conference relist, that the petition had never actually been considered and carried over, and that the elevated pool is dominated by petitions with a stronger signal than this one. That is the right way to use a risk-set anchor without being captive to it.
- **Full engagement with both briefs.** It read the brief in opposition in full and the petition through a delegated read, and set out the split as the petition frames it (one circuit on the as-applied side) against the government's answer (no phone-specific split; *Chavarria* confined to motor vehicles; *Morgan* in the Tenth Circuit already treats telephones as instrumentalities).
- **Used the strongest comparables in the record.** It noted that the Court had recently denied *Smith* and *Stackhouse*, the two closely analogous telephone petitions the brief in opposition cites, which is the most direct evidence available that this question was not drawing votes.
- **Vehicle defect, facts, and counsel weighed with proportion.** None was treated as dispositive; each was placed as a pull away from the band's typical grant.
- **Stated where to discount it.** The unread reply, the band-versus-state mismatch, and the limited retrieval were each named with the direction of the error they could produce.

What held it short of higher:

- The "why not lower" paragraph rests on a speculative read of which Justices might want a statement, which is the one place the document reasons from assumed preferences rather than from the record.
- The CVSG claim is set at 0.01 with a note that the number is positive only because of how the harness resolves it, which is a scoring remark rather than a forecast; harmless, but out of place in a rationale.
- Two corpus queries were recency-ranked rather than topical and contributed nothing, as the candidate itself concedes; the honesty is to its credit but the retrieval added no evidence.

## Leakage

`mode` `forward`; `retrieved_outcome_material` `false`; `influenced_prediction` `not_applicable`; `leakage_suspected` `false`. The prediction was created 2026-09-17 and the event resolved 2026-10-05, so the case was genuinely open. The log's 31 calls (capture coverage 1.0) are prompt, schema, snapshot and provisioned-document reads, salience doc and source reads, two `fedcourts query` pulls of recency-ranked granted and denied rows, a CourtListener docket search for *Chavarria* filed after 2025-06-01 (0 results), and a CourtListener docket-entries call on this docket ordered newest-first (0 results, captured). The last is a query on this case's own docket, which is ordinary forward retrieval for an open case and returned nothing in any event. No `retrieved_doc_date` on or after resolution, no read under `data/qp-topics/`. The reasoning discloses that nothing retrieved postdated or revealed the disposition. No sign of a decided case provisioned forward.

## Big case

My own read is 0.3: a genuine Commerce Clause question with doctrinal reach across facility-of-interstate-commerce statutes, but a one-decision, non-telephone conflict, alternative jurisdictional hooks on the record, a private criminal petitioner, and a denial without any noted writing. Public stakes are low. The staged `prediction.json` carries the predictor's `big_case_score`, so that number was visible when I read the file; my read above rests on the substance of the record and the outcome, not on it.

## Semantic grades

None. This is a cert cell; no semantic set is declared and no opinion slot is staged.
