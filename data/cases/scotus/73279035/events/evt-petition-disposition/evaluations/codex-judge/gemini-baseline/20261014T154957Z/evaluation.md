# Evaluation: gemini-baseline

## Outcome and numerical score

This is a cert-stage cell. The authoritative outcome records denial on October
13, 2026, with `actual_granted = 0`; the provisioned October 13 snapshot also
records the denial. gemini-baseline predicted `granted` with probability 0.75.
The exact-label score is **0** and the Brier score is
**(0.75 - 0)^2 = 0.5625**.

The prediction freezes `high` under `sal-v4`, Term 2025. The stamped segment
base rate, its basis, and Brier skill belong to the harness; I supply no
independent baseline. Votes are not scored on cert cells. Mechanical claims
and the forecast document are not graded here; no semantic set applies.

## Reasoning quality: 0.25

The rationale correctly recognizes the CVSG, the substantive surcharge
conflict, and the post-SG conference posture as relevant to case selection.
It also candidly acknowledges not having the government's exact recommendation.
Those strengths do not support the principal adjustment to a 75% grant call.

The central premise is materially wrong. The staged United States brief,
printed pages 1, 8-9, and 22, recommends **denial**, not a grant. It distinguishes
disagreement with the Sixth Circuit's broad remedial rule from suitability of
this vehicle: the top-hat plan, disputed fiduciary status, and absence of a
demonstrated conflict on this particular setting impede review. Printed pages
17-18 also explain that the Fifth Circuit panel decision was vacated for en
banc rehearing. gemini-baseline neither addresses those limitations nor verifies
the favorable recommendation it makes decisive. General government support
for remedial access is not support for granting this petition.

The rationale additionally selects a same-Term 2025 band figure rather than
justifying a strictly-prior-Term anchor. Its separate upward emphasis on a CVSG
also risks counting attention already represented by the high band twice. I
have not reconstructed the historical statpack or assigned a replacement rate.

This low grade reflects an unsupported, contradicted premise and omitted
case-selection analysis, not merely an incorrect outcome. Conversely, the
Court's unexplained denial does not establish why it denied review or endorse
the government's merits position. Only `reasoning.md` determines this grade.

## Leakage and limitations

The captured transcript identifies forward mode and September 18 calls,
before resolution. It includes case/SG searches and a broad corpus query;
the latter is visible in the log even though absent from the retrieval note.
Every result is marked `unobserved`. I do not interpret null document dates,
missing digests, or the self-reported failed search as proof that nothing was
returned. Nevertheless, the queries and rationale provide no affirmative
evidence of the October 13 disposition surfacing while forecasting. The
assessment is `not_applicable`, with `leakage_suspected = false`, subject to
that result-capture limitation. An SG recommendation is not a Court outcome.

The independent significance assessment is 0.55: a potentially broad ERISA
remedies issue presented through a specialized vehicle, not a merits ruling.
