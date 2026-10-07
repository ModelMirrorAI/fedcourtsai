# Evaluation: codex-baseline

## Outcome and quantitative score

This is a cert-stage arrival cell. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`. The candidate predicted `denied`, so correctness is 1. Its grant-family probability was 0.018; Brier loss is `(0.018 - 0)^2 = 0.000324`. These numbers are unchanged by the qualitative assessment.

No segment baseline or Brier skill is reported. The prediction froze `baseline` under `sal-v3` for Term 2026, whereas the committed `metrics/statpack.md` band table is headed `sal-v4`. A frozen band cannot be evaluated against another version's population or relabeled as a terminal-band observation. Accordingly, `base_rate_basis` is null and both numeric fields are absent; the cell-level flags record the mismatch. The table renders all ten of its Terms, so there is no rendered-window discrepancy. The historical 6.56% anchor described by the candidate is not independently reconstructed from the differently versioned current table, and the version change is not a fault in the original analysis.

## Reasoning quality: 0.86

The rationale makes a coherent distinction between a low unconditional grant probability and the petition-specific evidence. It identifies the asserted application-of-settled-law posture and absence of a developed split, while treating the reportedly published panel dissent as a counterweight rather than ignoring it. It explains the waiver's relevance and explicitly limits its reliance on the dissent because the full lower-court opinion was unavailable. That separation of verified metadata from the petition's own characterization is a strength.

The principal limitation is the numerical adjustment: the sharp reduction from the stated prior to 1.8% is a reasoned judgment, not an empirically supported likelihood adjustment. The unavailable appendix and opinion also constrain the assessment of vehicle quality and whether the supposed error is unusually compelling. The score rewards the transparent analysis, not merely the correct denial call. A denial alone does not establish that the Court adopted any of the candidate's proposed reasons.

The forecast document was read only for context. Neither it nor the structured quantitative claims contributes to reasoning quality; mechanical claim scoring belongs to the harness. No semantic grades are written on this cert cell. Cert votes are not scored, regardless of their availability. No independent big-case assessment is supplied.

## Leakage assessment

The harness log labels the prediction forward. Its 13 listed calls occurred on August 16, before the October 5 resolution; the reasoning discusses an unresolved petition. The reported appellate decision is dated October 17, 2025, not the Supreme Court denial. The waiver discussed in the reasoning is also pre-resolution forward information and is not leakage merely because it postdates docketing.

All listed call results are marked captured, but the log mainly records repository/schema inspection and does not separately show the CourtListener calls reported in the retrieval note. Thus 1.0 capture coverage is not proof that every reported retrieval appears. Broad local prediction searches in the log do not by themselves establish access to this petition's later outcome. The query containing a negative `qp-topics` glob excludes that directory rather than reads it; redaction markers likewise establish no leakage. On the staged evidence there is no affirmative indication of a mis-provisioned, already-decided case: outcome material is assessed false, influence not applicable, and leakage suspected false.
