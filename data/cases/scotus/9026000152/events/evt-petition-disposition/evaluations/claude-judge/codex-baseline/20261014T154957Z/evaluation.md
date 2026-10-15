# Evaluation — codex-baseline

**Cell:** cert stage, forward. **Outcome:** denied 2026-10-13 at the first conference (one distribution, no CVSG, no noted dissent). **Prediction:** denied, P(grant) = 0.003.

- `correct` = 1; `brier_score` = 0.000009.
- The prediction froze band `baseline` (`sal-v4`), so the segment base rate, its basis, and the skill score are the harness's (the stamped segment base rate).
- The claims block is scored in code. Cert cell: no vote accuracy, no semantic grades.

## Reasoning quality: 0.85

The analysis is careful and well grounded.
- **Anchor.** It pools the baseline reached-rate figure from the unrounded statpack.json fields, over prior Terms only. It explains why that figure, not the terminal-band or modern-cert figures, is the scored population.
- **Engagement with the petition.** It reads the petition itself, not just the questions presented. It notes the unreported opinions below and that the table of authorities is self-referential. It also treats Question II (the show-cause due-process claim) as the strongest general issue, and undercuts it with the petition's own statement that no final ruling on the show-cause order had issued.
- **Epistemic hygiene.** It treats the absence of entries as absence from the snapshot, not as a concession. It does not let low public significance stand in for low personal stakes. It also names what was not provisioned: the appendix and the supplemental brief.

Small deductions:
- It calls plenary review the likelier grant path over summary correction. That is contestable for a pro se procedural petition and sits somewhat at odds with its own error-correction framing.
- The big-case score of 0.13 is generous for this record.

## Leakage

The cell is forward, predicted 2026-10-04, resolved 2026-10-13.
- There were two general web calls on Supreme Court Rule 10. Neither names the case or the party, and both are unobserved, so I graded them on their queries.
- There was no CourtListener or corpus query.
- Its one `find` over `data/` excludes `data/qp-topics/*` at the path filter, so it opened nothing there. That is not a qp-topics read.
Grade: `not_applicable`, not suspected.

## Big case

My own read is 0.02.
