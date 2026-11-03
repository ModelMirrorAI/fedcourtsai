# Evaluation of `codex-baseline` — *Gina Silva, et al. v. Todd Blanche, Attorney General* (26A606, `evt-motion-disposition`)

## Stage & Quantitative Scoring

- **Stage:** `interim` (emergency application for a stay of removal submitted to Justice Alito).
- **Baseline & Skill Score:** Because this is an `interim`-stage cell, `segment_base_rate`, `brier_skill_score`, and `base_rate_basis` are left null for `stamp-cell` to compute and stamp from the committed statpack's substantive interim slice pooled over strictly prior application-Terms (`2016 <= T < 2026`). Similarly, `claim_scores` for the `interim-v3` set is computed in code by the harness.
- **Outcome & Accuracy:** On November 2, 2026, Justice Alito denied the application (`actual_disposition: "denied"`, `actual_granted: 0`, `interim_reading: "denied"`, `interim_granted: 0`). `codex-baseline` predicted `denied` with `probability = 0.07`, earning `correct = 1` and `brier_score = 0.0049`, outperforming the stamped segment base rate.

## Reasoning Quality (`0.68`)

`codex-baseline` wrote a careful, methodologically disciplined rationale in `reasoning.md`, but missed two major case-specific signals that caused it to under-adjust from the unconditioned base rate:
1. **Rigorous Statpack Pooling:** `codex-baseline` accurately pooled the ten strictly prior Terms (OT2016–OT2025) from the interim docket section of `metrics/statpack.md` (`160 granted / 1,366 resolved`), and thoughtfully discussed the statpack's caveats regarding parse coverage, denial-first reading of mixed dispositions, and escalation-ladder selection in the reserve.
2. **Missed `pro se` Signal on the Snapshot:** Although the provisioned snapshot (`2026-10-17.json`) explicitly listed lead applicant Gina P. Silva as her own counsel of record (`"Attorney": "Gina P. Silva"`, `"PartyName": "Gina Silva, et al."`, with contact details scrubbed), `codex-baseline` did not note that the application was filed *pro se*. Recognizing self-representation is critical on the interim docket, as *pro se* stay applications are denied by Circuit Justices in chambers at a rate far below the unconditioned substantive pool and almost never trigger a response request or full-Court referral absent renewal.
3. **Missed Lower-Court Lookup:** While `codex-baseline` noted that the snapshot identified Third Circuit proceeding `25-2933` and used CourtListener MCP to look up *Nken v. Holder*, 556 U.S. 418 (2009), it did not query CourtListener for Third Circuit docket `25-2933` (which would have retrieved the July 8, 2026 unpublished opinion showing that the claims below were unexhausted, waived, and fact-bound). Because it treated the underlying case as an opaque docket skeleton, `codex-baseline` made only a modest downward adjustment to `0.07` on the disposition and assigned overly high probabilities to a response request (`0.18`), a full-Court referral (`0.35`), and `big_case_score` (`0.25`).

## Predicted Reasoning (`0.68`)

In `predicted_reasoning.md`, `codex-baseline` correctly forecast the modal procedural path, though with substantial hedging and elevated escalation probabilities:
- **Central Claims:** `codex-baseline` forecast that (1) the application would most likely be denied by a short, unexplained order without a separate opinion within roughly one to four weeks of the October 16 submission; (2) the modal path was denial without a response request (`18%` probability of a response request); (3) the modal path was denial without a full-Court referral (`35%` probability of a referral); and (4) amicus participation (`3%`) and separate writings were unlikely.
- **Verification Against Staged Record:** All four modal directional calls held up against the November 2, 2026 denial by Justice Alito (seventeen days after submission, with `response_requested: false`, `referred_to_court: false`, `amicus_briefs: 0`, and no separate writings). However, the forecast remained generic on the underlying dispute and hedged heavily on escalation (`35%` referral, `18%` response request) because it did not account for the applicant's *pro se* posture or the published lower-court record in CA3 No. `25-2933`.

## Leakage Assessment

- **Mode:** `forward` (prediction timestamp `2026-10-31T18:00:17Z`, two days before the `2026-11-02` denial).
- **Assessment:** Clean (`retrieved_outcome_material: false`, `influenced_prediction: "not_applicable"`, `leakage_suspected: false`). `retrieval_log.json` shows three `unobserved` web-search calls, all of which queried exclusively for *Nken v. Holder*, 556 U.S. 418 (2009) (`site.supremecourt.gov Nken Holder 556 U.S. 418 stay removal four factors 2009`, `Nken v Holder 556 U.S. 418 2009 Supreme Court opinion`, and the `govinfo.gov` PDF URL for 556 U.S. 418), alongside captured corpus and CourtListener queries for *Nken* and prior-Term cert denials. No target-case queries or post-cutoff materials were accessed.
