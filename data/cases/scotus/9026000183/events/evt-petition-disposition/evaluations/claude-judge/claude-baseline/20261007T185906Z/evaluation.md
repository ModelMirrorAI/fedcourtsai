# Evaluation — claude-baseline — scotus/9026000183 / evt-petition-disposition

**Verdict:** disposition correct (`denied` == `denied`), probability 0.13 against a denial. Brier **0.0169**; skill vs the band baseline **-5.706** (negative: the forecast put roughly 2.2–2.6× the risk-set rate on a grant that did not happen, and the Brier penalty of that overshoot exceeds the baseline's own).

## Cell

Cert-stage petition event (`event.yaml` stage `cert`, moment `distribution`), **forward** mode. Outcome: **denied** on 2026-10-05 at the Term's opening order list after a single distribution for the 2026-09-28 conference, with a noted vote ("Justice Kavanaugh would grant") recorded as `noted_dissent_from_denial: true`; `actual_granted` = 0. No CVSG, no relist.

## Baseline

The prediction froze `band: baseline` under `salience_version: sal-v4`, and the committed `metrics/statpack.md` band table heading names sal-v4, so the basis is `risk_set`: the bracketed **reached** figure for `baseline`, pooled resolved-weighted over the rendered Terms strictly before 2026 (2017–2025; the caption renders 10 of 10 Terms, so the rendered window is the pack's whole window and matches the in-code lookback). Pooled from the pack's exact per-Term figures: 638 weighted grants over 12,720 weighted resolved = **0.0502**. Baseline Brier against a denial: 0.00252.

## Reasoning quality: 0.80

The most case-specific rationale of the three. It read both briefs in full, quotes Judge Willett's "one stroke" reservations, places the petition in the Court's Rule 23(f) line (*Wal-Mart*, *Comcast*, *Tyson Foods*, the *Lab Corp v. Davis* dismissal), and then argues the discount explicitly: the split is built from general articulations plus no-common-policy cases, so the opposition's "other side of the *Wal-Mart* line" answer is credible; the two-court rule and abuse-of-discretion review; and the ideological cross-pressure that the Justices most inclined to tighten Rule 23 are also the most sympathetic to religious objectors. That last point is a genuine insight the outcome bears out: the petition drew a single noted would-grant and no written dissent. The *Detwiler* hold is correctly discounted on timing and on its sincerity-only reach. The grant mass is decomposed coherently. Two deductions: the anchor arithmetic is wrong (637 grants over "about 11,720" gives 5.4%; the table's denominators sum to 12,720 and the rate is 5.0%), a small but real error in the one number the rationale is built on; and the final 0.13, highest of the three, is 2.6× the anchor after a downward case the candidate itself finds credible. Disclosure of the 2026-10-01 grant list surfacing in a corpus query, and of not looking for this case on it, is a point for the cell's integrity.

## Leakage

Forward cell (log mode=forward); prediction created 2026-10-04T20:41Z, the denial issued 2026-10-05. Log: 26 calls, coverage 1.0. CourtListener searches for Detwiler and for this caption returned lower-court dockets only (latest retrieved_doc_date 2025-09-23) and no SCOTUS docket; a docket_number=26-183 search returned nothing. One corpus `query` for granted 2020s rows (retrieved_doc_date 2026-03-26) surfaced other petitions from the 2026-09-28 conference granted 2026-10-01; the candidate disclosed this in reasoning.md and retrieval.md and states it did not look for this case on that list. That is pre-resolution forward signal about other cases, legitimately available, not outcome material about this petition, and the disclosure is a point for the cell. No `data/qp-topics/` read. No outcome material retrieved.

Grade: `retrieved_outcome_material` false, `influenced_prediction` not_applicable, `leakage_suspected` false.

## Big case

Evaluator read 0.42. Rule 23 commonality/predominance for a Title VII religious-accommodation class of roughly a thousand United employees who refused a COVID-19 vaccine mandate, with the Fifth Circuit's novel three-stage 'class rostering' plan as the concrete target; former Solicitor General as counsel and two trade-association amici. A grant would have reached class-action practice broadly and the setting is newsworthy, but the question is procedural and interlocutory, the Court denied after one conference, and only one Justice noted a would-grant with no written dissent. Mid-range stakes, below the top tier. Formed from the record and outcome; the predictors' big_case_score fields were visible inside prediction.json when I read it, which I note but did not use.

## Not scored here

`claims` and `predicted_reasoning.md` are not graded (the harness scores the claims block in code). No votes scored on a cert cell. Not a merits cell, so no `semantic_grades` block.
