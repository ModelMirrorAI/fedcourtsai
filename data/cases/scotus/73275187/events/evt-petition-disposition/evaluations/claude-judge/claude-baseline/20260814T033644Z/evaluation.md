# Evaluation — claude-baseline, scotus/73275187, evt-petition-disposition

**Outcome:** the petition in *Jouppi v. Alaska* was **granted** (resolved
2026-07-20, `actual_granted` = 1). **Prediction:** `denied`, P(grant) = 0.35.
`correct` = 0; Brier = (0.35 − 1)² = 0.4225.

## Base rate and skill

The staged prediction carries no frozen `context` block, so no prediction-time
band exists; per the fallback rule I derived the band available now — the
cell's terminal context is band **high** under **sal-v2**, matching the
statpack table's stated version — and used the **leading** (terminal-basis)
figures, recording `base_rate_basis` = `terminal`. Pooled resolved-weighted
over the sal-v2 band table's Term rows strictly before this case's Term
(docketed 2025-09-03 → OT2025; prior rendered Terms 2017–2024; the caption
renders 9 of 9 Terms, so the shown window is the window): 0.3494 over n = 899.
Skill: 1 − 0.4225/(0.3494 − 1)² = **+0.0018** — essentially at the naive
high-band baseline: its 0.35 nearly restates the terminal-band rate, though
the candidate reached that number from docket signals, not from this table
(it correctly reported the band table absent from the statpack version it
saw).

## Reasoning quality: 0.8

The strongest analysis of the cohort, and the only one that priced every
signal the snapshot held. Beyond the shared core (CFR after Alaska's waiver,
three quality amici, the ~6.5-month hold for *Pung*, *Pung* as
threshold-only with the fine question conceded here, hence no GVR), it alone
registered that the petition had **survived the June 29 post-*Pung* mop-up
conference** and the early-July orders undisposed — correctly identifying the
summer carry as a highly selected, elevated-grant-rate pool — and it enriched
the record with the split's texture (the Ninth Circuit/Alaska same-geography
conflict, *Thomas v. County of Humboldt*, the state-high-court lineup), elite
counsel (IJ, of *Timbs*), and a fresh judicial citation of this petition's
split analysis from the supplemental brief it retrieved. The counter-case was
equally specific: the Court's 27-year pattern of declining step-two
excessiveness vehicles (*Leonard*, *Toth*), two foregone grant moments, the
BIO's criminal-posture and factual-dispute vehicle attacks, and the
dissent-from-denial reading of the carry. Provenance and degradations
(unreachable corpus sidecar, forward-mode verification) were disclosed
honestly.

Given the outcome, the residual fault is the same directional one as the rest
of the cohort, in the mildest form: having assembled a signal stack it
described as "far out on the selected tail," it still kept the grant side
below coin-flip on the strength of the historical avoidance pattern and the
deny-with-writing scenario. That was a defensible weighing of a genuinely
two-sided record — the Court *had* passed twice — but the signals it
identified pointed to the grant that issued three days later. Calibration was
transparent and the arithmetic of its own argument (each condition multiplies
the base rate) arguably supported a number above 0.35. Not more than 0.8
because the bottom-line call was still wrong on a record it had read almost
perfectly.

## Other fields

- `vote_accuracy`: omitted — the prediction's `votes` is empty and the outcome
  records none.
- `judgment_correct`: null — cert-stage cell.
- The prediction names no `predicted_reasoning_doc` (a pre-field record; not
  penalized). `reasoning.md` was the graded document. The extra `confidence`
  field was ignored.

## Leakage

Forward cell (`mode: forward` in the harness log). Predicted 2026-07-17; the
grant issued 2026-07-20. The log shows provisioned-input reads, statpack
lookups, a failed corpus query (sidecar unreachable, disclosed and flagged by
the candidate), a fetch of this case's own June 25, 2026 supplemental brief
from the docket (pre-decision material — provisioned-docket-adjacent, and
disclosed), and web checks that confirmed the petition **pending** with no
disposition surfaced. No `retrieved_doc_date` at or after resolution; the
status check is exactly the forward-mode diligence the doctrine wants, and
the candidate's disclosure is a point for the cell's integrity.
`influenced_prediction` = `not_applicable`; not mis-provisioned.
