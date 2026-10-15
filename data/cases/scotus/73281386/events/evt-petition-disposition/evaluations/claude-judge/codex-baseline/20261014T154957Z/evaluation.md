# codex-baseline — evaluation

## Cell

Cert stage (`event.yaml` `stage: cert`). Outcome: `actual_disposition` **granted**, `actual_granted` 1, `disposition_route` plenary, resolved 2026-10-13 after two distributions, no CVSG. The prediction froze a band (`baseline`, sal-v4, Term 2025), so the segment base rate, `base_rate_basis` and `brier_skill_score` are the harness's stamp and left null here; read the comparison against "the stamped segment base rate". `correct` is the exact-label match on the disposition axis: `gvr` and `summary-reversal` both count as grants on the binary axis but are distinct labels from `granted`, so a summary-disposition call scores 0 against a plenary grant. Claims and the forecast document are scored in code and are not graded here. Cert cell: no vote accuracy, no semantic grades.

## Score

- Predicted `gvr`, P(grant) 0.72 → `correct` 0 (label), Brier (0.72 − 1)² = **0.0784**.
- The binary call was right and the probability well above the stamped baseline-band anchor; the label miss is on the route. The candidate's own allocation put only 14.4% on a plenary grant against 43% GVR and 14.6% summary reversal.

## Reasoning quality — 0.68

Strong points: it read both briefs in depth and anchored on the right primary evidence — the June 6, 2025 order in the earlier petition (stay pending a timely subsequent petition, instruction to narrow, recorded disagreement) and the thin D.C. Circuit remand order. It weighed the BIO's compliance and vehicle arguments seriously (the 30(b)(6)-vs-administrator distinction, forfeiture, unpublished mandamus posture), handled the band mismatch transparently without rewriting the frozen conditioning, and its base-rate work and probability decomposition are internally consistent and honestly labelled as judgmental.

What held it back: the route analysis leaned heavily toward a corrective summary disposition and gave short shrift to the possibility, which the petition's second question invites, that the Court would want to decide the FOIA-coverage/discovery question on full briefing — the case's second trip to the Court and the presence of a clean legal question cut toward plenary review more than the candidate allowed. Its supporting research on Cheney was mostly unsuccessful (throttled), which it disclosed accurately.

## Leakage

Forward cell, prediction 2026-09-16, outcome 2026-10-13. Log shows only provisioned-file reads, the statpack, two uncaptured web calls whose queries target Cheney (2004), and CourtListener searches for Cheney. Nothing aimed at this petition's disposition, no post-resolution document date, no `data/qp-topics/` read. `not_applicable`, not suspected.

## Big case

My own read: 0.74 (see evaluation.json).
