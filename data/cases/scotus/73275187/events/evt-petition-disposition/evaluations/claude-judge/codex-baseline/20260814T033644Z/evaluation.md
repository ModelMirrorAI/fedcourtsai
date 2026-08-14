# Evaluation — codex-baseline, scotus/73275187, evt-petition-disposition

**Outcome:** the petition in *Jouppi v. Alaska* was **granted** (resolved
2026-07-20, `actual_granted` = 1). **Prediction:** `denied`, P(grant) = 0.29.
`correct` = 0; Brier = (0.29 − 1)² = 0.5041.

## Base rate and skill

The staged prediction carries no frozen `context` block, so no prediction-time
band exists; per the fallback rule I derived the band available now — the
cell's terminal context is band **high** under **sal-v2**, matching the
statpack table's stated version — and used the **leading** (terminal-basis)
figures, recording `base_rate_basis` = `terminal`. Pooled resolved-weighted
over the sal-v2 band table's Term rows strictly before this case's Term
(docketed 2025-09-03 → OT2025; prior rendered Terms 2017–2024; the caption
renders 9 of 9 Terms, so the shown window is the window): 0.3494 over n = 899.
Skill: 1 − 0.5041/(0.3494 − 1)² = **−0.1909** — modestly worse than the naive
high-band baseline on this cell.

## Reasoning quality: 0.65

This is the most thorough merits engagement of the cohort: it worked through
the petition and the brief in opposition on their own terms — the asserted
Ninth Circuit/Alaska split, the state's Rule 10 error-correction framing, the
disputed factual record as a vehicle problem — and it read *Pung* itself via
CourtListener rather than taking a summary's word, correctly concluding that
*Pung* decided a threshold question and supplied no rule for a GVR. Its
calibration section is explicit and honest: it cites the statpack's ~3.1%
modern grant rate and 5.36% paid-2025 figure, declines to map the months-long
hold mechanically onto the one-relist bucket, and even notes its corpus query
showed same-conference petitions producing grants, denials, and GVRs. The
conditional structure was right too: it judged plenary cert more plausible
than a GVR if the Court acted on the grant side, which is what happened.

Given the outcome, the failure is in the final weighing: after crediting the
CFR, three amici, unusually certworthy facts, and an apparent *Pung* hold, it
still let the BIO's vehicle arguments and the low unconditional baseline pull
the number to 0.29. It also did not register that the petition had *survived*
the June 29 conference and early-July orders undisposed as of the snapshot —
the one bullish signal it left unpriced. Anchoring the write-up on the
generic paid-docket prior rather than a band- or signal-conditioned segment
understated how selected this petition already was. Sound, well-sourced,
transparent analysis whose bottom line was directionally wrong.

## Other fields

- `vote_accuracy`: omitted — no per-Justice votes were predicted, and the
  outcome records none.
- `judgment_correct`: null — cert-stage cell.
- The prediction names no `predicted_reasoning_doc` (a pre-field record; not
  penalized). `reasoning.md` was the graded document. The extra `confidence`
  field was ignored.

## Leakage

Forward cell (`mode: forward` in the harness log). Predicted 2026-07-17; the
grant issued 2026-07-20. The log shows provisioned-input reads, statpack/
statpack.json lookups, CourtListener searches scoped to intervening Excessive
Fines authority (retrieving *Pung*'s opinion, filed 2026-06-23), and a generic
2020s corpus query. Every legible `retrieved_doc_date` (2025-09-04,
2026-06-23, 2025-04-22) predates resolution; no call sought this petition's
own disposition. `influenced_prediction` = `not_applicable`; not
mis-provisioned.
