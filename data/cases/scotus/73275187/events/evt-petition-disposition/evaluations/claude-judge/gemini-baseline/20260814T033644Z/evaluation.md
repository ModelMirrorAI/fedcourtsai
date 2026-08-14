# Evaluation — gemini-baseline, scotus/73275187, evt-petition-disposition

**Outcome:** the petition in *Jouppi v. Alaska* was **granted** (resolved
2026-07-20, `actual_granted` = 1). **Prediction:** `denied`, P(grant) = 0.15.
`correct` = 0; Brier = (0.15 − 1)² = 0.7225.

## Base rate and skill

The staged prediction carries no frozen `context` block, so no prediction-time
band exists; per the fallback rule I derived the band available now — the
cell's terminal context is band **high** under **sal-v2**, which matches the
statpack table's stated version — and used the **leading** (terminal-basis)
figures, recording `base_rate_basis` = `terminal`. Pooled resolved-weighted
over the "Segment base rate by salience band (sal-v2)" Term rows strictly
before this case's Term (docketed 2025-09-03 → OT2025; prior rendered Terms
2017–2024; the caption renders 9 of 9 Terms, so the shown window is the
window): Σ(rate·n)/Σn over n = 899 → **0.3494**. Skill:
1 − 0.7225/(0.3494 − 1)² = **−0.707**. The forecast was far worse than the
naive high-band baseline on this cell — it priced the grant at less than half
the terminal-band rate and the petition was granted.

## Reasoning quality: 0.55

What the write-up got right: it correctly identified the question presented
(the *Bajakajian* gravity-of-the-offense abstraction split), the paid petition
with three quality amici, the Court-requested response after Alaska waived,
and — the analytic centerpiece — the six-month hold aligned with *Pung v.
Isabella County*, plus the correct doctrinal point that *Pung* resolved the
threshold "is it a fine?" question rather than *Jouppi*'s step-two
excessiveness standard, making a GVR unlikely. That GVR-discounting was sound
and vindicated: the Court did not GVR, it granted plenary review.

Where it went wrong, given the outcome: having correctly ruled out the GVR, it
treated denial as the near-default residual (0.15) rather than reasoning that
a petition the Court affirmatively CFR'd, held rather than denied for six
months, and redistributed after *Pung* was a strong candidate for exactly the
plenary grant that followed. It also read the post-*Pung* redistribution as
end-of-term "cleanup" without registering that, as of the 2026-07-17 snapshot,
the petition had *survived* the June 29 conference and the early-July orders
undisposed — a bullish signal a sharper read would have priced. Minor sloppiness:
it labels the call for a response "CVSG/CFR" (no Solicitor General involvement
here), and the prose anchors on generic hold-then-deny/GVR frequencies without
engaging the statpack's band or signal-conditioned cuts quantitatively. The
dissent-from-denial hypothesis was reasonable but was allowed to dominate. A
coherent, well-organized analysis with correct mechanics whose final weighing
leaned hard against the signals it had itself assembled.

## Other fields

- `vote_accuracy`: omitted — no per-Justice votes were predicted, and the
  outcome records none.
- `judgment_correct`: null — cert-stage cell.
- The prediction names no `predicted_reasoning_doc` (a pre-field record; not
  penalized). `reasoning.md` was the graded document.
- Claims: the staged prediction carries no claims block; `claim_scores` is the
  harness's in any case.

## Leakage

Forward cell (`mode: forward` in the harness log). Predicted 2026-07-17; the
grant issued 2026-07-20. The log shows provisioned-input reads, statpack and
corpus-CLI baseline lookups, and two web searches aimed at intervening
Excessive Fines authority (surfacing *Pung* and *Ellingburg*) — legitimate
forward signal about other cases, not this petition's nonexistent outcome. No
`retrieved_doc_date` at or after resolution; no query sought this case's
disposition. `influenced_prediction` = `not_applicable`; not mis-provisioned.
