# Evaluation: claude-baseline

## Outcome and quantitative score

This is a cert-stage petition-disposition event. The supplied outcome records
`denied`, `actual_granted = 0`, resolved October 5, 2026. claude-baseline's September
17 prediction named `denied` with P(any grant) = 0.012. Exact-label correctness
is **1** and the Brier score is **(0.012 - 0)^2 = 0.000144**. A denial supplies
no substantive explanation endorsing or rejecting the petition's legal theory.

The scored prediction froze Term 2025 and `baseline` under `sal-v4`. The
committed `metrics/statpack.md` heading matches that version. I use its bracketed
reached-baseline figures, not the leading terminal rates or the evaluator's
decided-docket context. The table renders all ten of its ten Terms; the eligible
rows are OT2017–OT2024. In descending Term order, their rate/weighted-n pairs are
5.7%/1271, 5.9%/1312, 5.8%/1192, 5.6%/1500, 4.5%/1739, 4.6%/1399,
4.6%/1524, and 4.7%/1643. Pooling the displayed rates gives
592.925 / 11,580 = **0.05120250431778929**, on the **risk_set** basis.
These are denial-reweighted estimates at the rendered table's precision, not
raw observed counts or a fresh corpus census. OT2025 and OT2026 are excluded.
The single-event skill score is **0.9450737326637661**, computed as
1 - 0.000144 / 0.05120250431778929^2; it is not an aggregate performance claim.

## Reasoning quality: 0.84

The rationale identifies the useful predecision signals: a response waiver,
distribution without a recorded response request, an unpublished lower-court
disposition, and no demonstrated like-for-like appellate conflict. Its distinction
between military-specific remedial vehicles and a civilian implied action
against a private hospital is supported by the petition's own account. The
petition's discussion of section 337(a) and the separate private-remedy inquiry
also supports treating the remedy theory as an obstacle rather than equating
political controversy with certworthiness. claude-baseline correctly uses a prior-Term
risk-set anchor and labels terminal-bucket statistics as secondary shape checks.

The main limitations are evidentiary and quantitative. Assertions about repeated
denials of related petitions and the aging-out of the EUA posture are not
independently established by the provisioned record; the candidate appropriately
discloses reliance on general knowledge after throttled searches. Solo-practitioner
counsel is not, by itself, an established vehicle defect. The proposed 5% response
request probability and 15% conditional grant probability are judgmental, not
estimated from matched cases. The recency-ranked corpus examples supply little
case-specific calibration. These limitations prevent a near-perfect assessment
despite a well-supported denial direction and explicit uncertainty range.

## Leakage and scoring boundaries

The harness records forward mode, 28 calls on September 17, and complete result
capture. Its two CourtListener search results are recorded as throttled. The
corpus query carries an extracted September 16 document date; no call or prose
shows the October 5 resolution of this petition. The prediction treats the
September 28 conference as future. I therefore record no retrieved outcome
material, `not_applicable` influence, and no suspected leakage. Captured digests
are an audit trail, not full result bodies independently re-read here.

I read the pointed-to forecast for context only. Neither its ancillary forecasts
nor the structured claims affect reasoning quality; claim scores remain the
harness's. Cert votes are unscored, and no semantic set is declared at this stage.
I omit the optional independent stakes assessment rather than form one after
seeing candidate stakes material. No external retrieval was needed to evaluate
the supplied record.
