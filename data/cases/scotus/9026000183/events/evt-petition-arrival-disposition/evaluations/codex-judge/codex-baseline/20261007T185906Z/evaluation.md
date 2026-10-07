# Evaluation: codex-baseline

## Outcome and quantitative score

This is a cert-stage evaluation. The outcome records denial on October 5,
2026, with `actual_granted = 0`. codex-baseline correctly predicted `denied`
(**1**). Its grant-family probability of 0.14 yields
`(0.14 - 0)^2 = 0.0196`.

The outcome additionally records one distribution and a noted dissent from
denial. The October 5 snapshot states that Justice Kavanaugh would grant.
Cert votes are not scored, regardless of this notation. There is no merits
judgment or semantic claim set to grade. The forecast document was read only
for context; mechanical claims are left to the harness. Their agreement or
disagreement with these additional outcome facts does not affect reasoning
quality.

## Baseline unavailable under the frozen version

The prediction's frozen band is `baseline` under `sal-v3`, Term 2026. The
current committed segment table in `metrics/statpack.md` is **sal-v4**.
Its 10-of-10-Term caption leaves OT2017-OT2025 as the rendered strictly-prior
window, but matching the window does not match the band definition.
Consequently, `segment_base_rate` and `brier_skill_score` are omitted and
`base_rate_basis` is null. No terminal fallback or re-derived decided-docket
band is used. This is documented in the shared flags file.

The rationale's historical 863/13,163 anchor is a reported sal-v3 calculation,
not a baseline independently recoverable from the current sal-v4 table.
Its explicit prior-Term risk-set approach is conceptually appropriate; the
version mismatch is not treated as the predictor's error.

## Reasoning quality: 0.90

The analysis distinguishes plausible certiorari features from the evidence
needed to establish them. It identifies the published Rule 23 dispute,
separate writing, and asserted conflict, but recognizes that the record is
one-sided, that some fact-matched authorities are district-court decisions,
and that differences in applying a common standard need not establish a
square appellate rule conflict. It explicitly limits its confidence because
the BIO and separately provisioned lower-court opinion are unavailable.

Its discussion of interlocutory posture and Judge Willett's concurrence in
the judgment under an abuse-of-discretion standard is supported by the
petition's account. It also treats the Detwiler request as both a contingent
GVR opportunity and a reason another case might be the more suitable route.
Those considerations supply a coherent explanation for a modest upward
adjustment while retaining denial as substantially more likely.

The remaining limitation is numerical: the move from the stated 6.56% prior
to 14% is a reasoned judgment rather than a demonstrated conditional estimate
or explicit sensitivity analysis. The account of the appellate conflict
necessarily remains petition-derived, and the reported retrieval failure
limits corroboration. Those limitations keep the score below full credit.
The score does not reward the lower realized Brier score, penalize the
unrealized no-dissent forecast, or infer that denial endorsed the analysis.

## Leakage

The log labels this `forward` and dates the visible calls August 16, before
the recorded October 5 disposition. Its calls concern provisioned documents,
the August snapshot, schemas, code, validation, and the statpack. No visible
call seeks the disposing order, and the reasoning does not presuppose denial.

Coverage is 1.0 for recorded calls, not proof that every self-reported activity
has a corresponding row. The prose reports rate-limited CourtListener searches
for Detwiler, Speerly, and a class-rostering topic; the staged log does not
contain separate MCP rows for those searches. Their failures cannot therefore
be independently confirmed from the log. This visibility limit is not itself
evidence of outcome retrieval. On the available forward chronology and
content, `retrieved_outcome_material = false`, influence `not_applicable`, and
`leakage_suspected = false`.
