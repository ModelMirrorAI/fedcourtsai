# claude-baseline — scotus/9026000027, evt-petition-disposition

**Prediction:** denied, P(grant) = 0.006. **Correct:** yes. **Brier:** 0.000036.

## Cell

Cert stage (`stage: cert`, distribution moment), forward mode. Outcome: **denied** on 2026-10-13 (`actual_granted` 0), one distribution, no CVSG, no noted dissent. The prediction froze `context.band` = `baseline` under `sal-v4` (Term 2026), so the segment base rate, `base_rate_basis` and Brier skill are the harness's to stamp; I left them null and refer only to "the stamped segment base rate". `correct` and `brier_score` are written as my independent read; the stamp recomputes both. No votes are scored on a cert cell, no semantic set is declared, and `claim_scores` is the harness's.

## Leakage

Forward cell made 2026-10-04, before the October 9 conference and the October 13 order. I checked the log for this case's disposition surfacing as already decided and found none: no retrieved document dated on or after resolution, no query for the petition's disposition, no read inside `data/qp-topics/`. `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

Log detail: two CourtListener searches for the Fifth Circuit opinion/docket (No. 25-30509) — lower-court material, legitimate forward signal — both returned zero results; one generic corpus query.

## Reasoning quality: 0.85

A careful, well-grounded rationale. It anchors explicitly on the sal-v4 baseline reached-band figure pooled over strictly prior Terms (~5%), then justifies each downward step with record evidence: QP 1 is a pure Louisiana-law question (and, as the BIO notes, not even the test the courts below applied — the two-contract defense); the only federal framing (QP 2, FECA/Supremacy Clause) was raised first on reconsideration and on appeal and was not reached; no conflict is alleged beyond a 1994 E.D. Va. decision under another State's law; the opinion below is unpublished and expressly narrow. It correctly reads the unsolicited BIO as weak signal, and candidly notes it did not read the Fifth Circuit opinion itself. Each of those factors is the kind that drives a routine denial, which is what happened. Small deductions: the pro-se inference rests partly on stylistic impression of the brief rather than the docket alone, and the preemption issue's possible recurring importance gets only a sentence.
