# Evaluation — `claude-baseline` on `scotus/9526000729` (`evt-motion-disposition`)

## Outcome & Score Summary

On November 23, 2026 — six days after `26A729` (*Ian Buenaventura v. Leslie Buot*) was submitted on November 17, 2026, and two days after `claude-baseline` ran in forward mode — Justice Jackson denied both the stay application and the accompanying motion for leave to file the application and appendix under seal in chambers, with no response requested, no referral to the full Court, zero amicus filings, and no separate writings (`actual_disposition: "denied"`, `interim_reading: "denied"`, `interim_granted: 0`, `response_requested: false`, `referred_to_court: false`, `amicus_briefs: 0`).

- **Disposition call:** `predicted_disposition = "denied"` (`correct = 1`).
- **Probability & Brier score:** `probability = 0.01`, yielding an elicited `brier_score = 0.0001` against `interim_granted = 0`.
- **Harness-stamped baseline and claims:** Because this is an interim-stage cell (`term: 2026`), `segment_base_rate`, `brier_skill_score`, and `claim_scores` (`interim-v3`) are computed and stamped by the harness (`stamp-cell --role evaluator` and `fedcourtsai.pipeline.claims`), and `base_rate_basis` remains `null` structurally because interim baselines pool across strictly-prior application-Terms rather than salience bands (`context.band` is `null` by rule). Because the strictly-prior 10-Term substantive interim pool clears `INTERIM_BASE_RATE_MIN_RESOLVED = 50`, the stamped segment base rate will be non-null.
- **Statpack provenance check:** `uv run fedcourts statpack-at` verified `claude-baseline`'s recorded `statpack_digest` (`sha256:a7d6f5cde0a4c0e9f80d0491dd08e65cd303aa7b14ce6ec1133e915c88af92a4`) against prediction-time statpack build `50244479fc2d` (landed `2026-11-20T18:59:23Z`), against which `claude-baseline`'s base-rate citations were graded (matching the committed pack on strictly-prior OT2016–OT2025 rows).

## Reasoning Quality (`0.78`)

`claude-baseline`'s `reasoning.md` is crisp, honest about uncertainty, and well-calibrated on the primary disposition (`0.01`):

- **Strengths:** Properly identified both the strictly-prior 10-Term `finer_*` pool and the descriptive `private`, `unmarked` applicant-class cut from the prediction-time statpack, and articulated clearly why `private unmarked` grants remain concentrated in counselled federal-question challenges against government action rather than self-represented private state-court disputes. Even from the caption and sealing request alone, `claude-baseline` sensibly inferred that the dispute likely concerned a family or protection matter and reserved a `1%` tail for unseen urgency or an administrative stay.
- **Limitations:** `claude-baseline` performed minimal retrieval — one `fedcourts query` for 8 denied rows and zero CourtListener or public-docket checks — leaving discoverable pre-decision facts unverified (specifically District of Maine docket *In re Buenaventura*, No. `2:25-mc-00465`, confirming enjoined-filer status in Androscoggin County divorce/custody litigation, and Buenaventura's prior SCOTUS stay application `25A572` in the same dispute, which Justice Jackson denied alone in ten days). It also missed Supreme Court Rule 34.7 as the structural reason no application text was posted publicly, and set `referral-increment = 0.20` fairly high by treating post-denial renewal to a second Justice as a one-in-five pre-resolution referral path even though `evt-motion-disposition` resolves upon Justice Jackson's initial chambers denial.

## Predicted reasoning (`0.85`)

`claude-baseline`'s `predicted_reasoning.md` is concise and concrete, and all four of its central claims held up cleanly against the resolved record:

- **Borne-out central commitments:** (1) Justice Jackson denying the stay herself without opinion and with no partial relief or administrative stay within roughly one to three weeks of the Nov. 17 submission (actual: six days, Nov. 23 — slightly faster than the one-week lower edge of "roughly one to three weeks", a minor timing detail); (2) no call for a response and most likely no full-Court referral (`response_requested: false`, `referred_to_court: false`); (3) simultaneous disposition of the sealing motion alongside the stay application without separate comment; and (4) zero amicus briefs and no separate writing or noted dissent by any Justice.
- **Why `0.85` rather than `1.0`:** While every commitment was directionally and procedurally accurate, the forecast left the direction of the sealing motion itself unspecified ("disposed of alongside the application" without committing to grant vs. denial of sealing), hedged referral with a one-in-five renewal branch, and lacked case-specific lower-court or Rule 34.7 detail beyond what the caption disclosed.

## Leakage & Big-Case Notes

- **Leakage (`not_applicable`, `leakage_suspected: false`):** Prediction ran on `2026-11-21T03:12–03:14Z`, two days before the `2026-11-23` chambers denial. All 5 tool calls in `retrieval_log.json` had full result capture (`result_capture_coverage: 1.0`), with no external lookups, no `data/qp-topics/` reads, and a maximum `retrieved_doc_date` of `2026-11-20`.
- **Big-case read (`evaluator_score: 0.01`):** Private *pro se* domestic-relations stay application summarily denied in chambers with sealing denied; `claude-baseline`'s `big_case_score` (`0.03`) is well-aligned with the negligible stakes of the case.
