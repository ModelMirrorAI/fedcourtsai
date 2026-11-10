# Evaluation: codex-baseline

## Outcome and accuracy

This is a cert-stage cell. The November 9, 2026 outcome is `denied`, with `actual_granted = 0`. codex-baseline predicted denial and P(grant) = 0.05: **correct = 1**, **Brier = 0.0025**. Cert votes are not scored. No semantic set applies, and quantitative claims, baseline and skill remain the harness's responsibility. Any baseline comparison uses the stamped segment base rate; no independently pooled evaluation anchor is supplied here.

## Reasoning quality: 0.90

The rationale is methodologically strong for a record without substantive filings. It distinguishes administrative response extensions from cert grants, first distribution from relisting, the private petitioner's salience class from the federal respondent's identity, and unavailable documents from affirmative evidence of a defective petition. It expressly avoids inferring the legal issue from the caption alone.

Its prior-Term reached-risk-set calculation was checked against the reconstructed candidate-era sal-v4 statpack and is arithmetically consistent. It excludes the current Term and does not multiply overlapping circuit, relist or CVSG cuts as if independent. It correctly explains why terminal relist and CVSG summaries are not forward transition hazards and why historical grant/GVR labeling limits route inference. Its judgmental auxiliary probabilities are labeled as such. These features support the rationale grade independently of the denial outcome and independently of the structured claims' eventual scores.

Historical base-rate use was checked against statpack build `886549a3ac32bdba039691b6d2ca7dc57bb72561`, digest `sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde`, reconstructed by `fedcourts statpack-at` from statpack history at the prediction run. This differs from the current evaluation-era pack. The evaluator does not substitute that historical calculation for the harness's stamped segment base rate.

The limitation is substantive rather than procedural: this remains a prior-and-posture forecast, not an analysis of a verified question presented, split, or lower-court rationale. The opposition now available to the evaluator was fetched after the prediction and is not used to penalize its absence from the candidate's analysis. The larger Brier loss than the other candidates does not reduce this document-only reasoning grade.

## Predicted reasoning

**Grade: 0.85.** The central calls are denial by an unexplained order after the November 6 conference, no additional distribution, and no CVSG. The staged docket records exactly one distribution and a bare November 9 denial, while the outcome records one distribution and no CVSG. These are specific procedural commitments, although the document cannot supply a discriminating legal ground.

The grant-route discussion is conditional on an event that never happened and is unresolved. The no-dissent/no-statement proposition is only partly observable: the outcome affirmatively records no noted dissent, but no exhaustive writing inventory establishes the absence of a non-dissent statement. It is marked unresolved as a whole, not counted as a miss. The forecast grade is separate from both the rationale grade and the structured claims.

## Leakage

The harness records forward mode and October 17 tool activity, before the November 9 resolution. Captured metadata shows local provisioned-input and aggregate-statpack reads, plus generic Supreme Court rules requests. The four web rows are `unobserved`; the overall coverage is 0.875, and their asserted empty returns cannot be independently confirmed. Their visible queries do not seek this case or its disposition. No evidence shows the already-decided exception to forward mode. Assessment: no demonstrated outcome material, influence `not_applicable`, `leakage_suspected = false`.

## Stakes

My independent stakes read is 0.15, based on the evaluator's later-provisioned opposition: an individual motion-to-reopen dispute, a contested claim of circuit disagreement, and the government's asserted preservation and factbound vehicle problems. Denial is not adoption of those arguments. The candidate's decision to leave its own stakes estimate null is not penalized, and this case-level assessment does not affect the rationale grade.
