# Evaluation: gemini-baseline

## Outcome and numerical score

This is a cert-stage evaluation of prediction run `20260917T214606Z`.
The supplied outcome records denial on October 13, 2026, with
`actual_granted = 0`. The predicted label, `denied`, matches exactly:
`correct = 1`. The Brier score is `(0.25 - 0)^2 = 0.0625`.

The prediction freezes an elevated band under sal-v4, Term 2025. The
segment baseline, its basis, and Brier skill are left to the harness;
any comparison must use the stamped segment base rate. No separate rate
is calculated here. Cert votes are not scored. No semantic set is declared,
and the mechanical claims remain for the harness to score.

## Reasoning quality: 0.60

The rationale identifies genuine features of the supplied record: the
response request following a waiver, an immunity-specific route to review,
and the distinction between redistribution after a response and an actual
post-conference relist. It acknowledges that the opposition and reply were
not read and treats vehicle suitability as uncertain. These are useful
grounds for a probabilistic forecast rather than a categorical prediction.

The upward adjustment is much less developed. The rationale cites selected
recent-Term rates rather than explaining a pooled prior-Term anchor, and
does not adequately distinguish the response-request signal from the
attention already represented in its elevated-band anchor. Its general
analogy to immunity summary reversals does not engage the petition's
case-specific obstacles: unresolved causation, the interlocutory posture,
and the dispute over deliberate avoidance of verification rather than an
innocent analytical error. The provisioned petition itself offered material
for that analysis even without the opposition. Consequently, the substantial
grant tail is intelligible but insufficiently justified.

The score evaluates `reasoning.md` only. It neither grades the separate
forecast document nor rewards the correct label as proof that the Court
accepted the rationale. The recorded denial supplies no explanation of the
Court's reasons.

## Leakage and evidence limits

The harness log identifies forward mode. Its September 17 calls precede
the October 13 disposition, and the query strings show no search for a
known denial or read of outcome-revealing material. The lower-court lookup
is not a lookup of this petition's eventual disposition.

Result capture is 0/25: every result is unobserved. Missing dates and
digests are not evidence that nothing was returned. The candidate's
retrieval note also omits two logged corpus-query attempts; their results
are unknown, not demonstrably empty. Neither that reporting limitation nor
ordinary forward retrieval supplies evidence of leakage. Accordingly,
`retrieved_outcome_material = false` means no such material is evidenced
in the available record, and influence is `not_applicable`.

The case-significance assessment reflects the supplied questions and
procedural posture, not agreement with the candidate's own score.
