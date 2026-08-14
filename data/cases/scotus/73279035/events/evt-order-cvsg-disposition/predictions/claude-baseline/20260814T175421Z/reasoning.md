# Rationale — P(any grant) = 0.45

## Anchor

This is a `forward`, cert-stage cell at `moment: cvsg`, with a harness-frozen
band of **`high`** under `sal-v2` (Term 2025, `distribution_count: 2`,
`cvsg_date: 2026-04-06`). Per the contract I anchored on the **bracketed
`reached`** rate for the `high` band in the statpack's "Segment base rate by
salience band (sal-v2)" table, pooled over the Terms strictly before this
case's own (2017–2024, all eight rendered rows preceding Term 2025):
weighted mean ≈ **40%** (n ≈ 1,059; per-Term reached rates 33.6%–44.7%).

Two consistency checks sit beside it. The statpack's CVSG cut (paid scored
segment) gives the grant family among CVSG'd petitions as **granted 30.1% +
gvr 5.5% ≈ 36%** (n = 163 resolved). The relist-count cut puts a
twice-distributed petition at granted 26.7% + gvr 12.8% ≈ 40%. All three
figures bracket the same region, so the anchor is robust to which cut you
prefer.

## Adjustments

**Up from the anchor:**

- **The split is real, acknowledged, and freshly deepened.** The Sixth Circuit
  below (144 F.4th 828) expressly "sided with the Fourth Circuit" (Rose v. PSA
  Airlines, 80 F.4th 488) against six circuits (CA2, CA5, CA7, CA8, CA9, CA11)
  on whether surcharge is available under § 1132(a)(3), and the Fifth
  Circuit's 2025 Aramark decision reaffirmed the majority side. This is the
  classic grant driver, and the Court has repeatedly granted in this exact
  line (Mertens, Great-West, Amara, Montanile).
- **The Court's engagement ladder is fully climbed.** Respondent waived; the
  Court requested a response sua sponte (Dec 29, 2025), then CVSG'd four days
  after the first conference at which the case was considered. Each step is an
  affirmative act of attention beyond what the band alone encodes.
- **Vehicle finality.** The same QP1 was denied in Rose (23-734, denied
  April 15, 2024) where the BIO stressed the interlocutory posture; here the
  Sixth Circuit disposed of the whole suit, and the petition squarely argues
  the Mertens/Great-West posture answers the liability-unresolved objection.
  The Court passing on Rose and then escalating here reads as it having
  waited for a final-judgment vehicle.
- **Strong presentation.** UVA Supreme Court clinic (Xiao Wang) for
  petitioners, a Bray amicus on the remedies history, Gregory Garre opposing —
  a well-lawyered petition the cert pool takes seriously.

**Down from the anchor:**

- **The top-hat objection is a genuine vehicle risk, and it is exactly the
  kind of point a CVSG surfaces.** The BIO's core argument: every circuit
  permitting surcharge did so against an ERISA *fiduciary*, and this top-hat
  plan is statutorily exempt from ERISA's fiduciary duties (29 U.S.C.
  § 1101(a)(1)), so no circuit would decide *this* case differently and the
  split is not implicated on these facts. If the SG credits that, a deny
  recommendation follows, and the Court usually follows a deny
  recommendation.
- **Liability was never resolved below**, so respondent can frame the case as
  fact-bound and hypothetical.
- **QP2's breadth** (preemption of state-law claims on a separate trust
  contract) may make the package less attractive than a clean QP1-only
  vehicle.

Decomposed: I put P(SG recommends grant in whole or part) at ~0.45 — the
Department of Labor's institutional position has favored surcharge's
availability, but the top-hat posture gives the SG an easy vehicle out — with
P(grant | grant recommendation) ≈ 0.8 and P(grant | deny recommendation)
≈ 0.15. That yields ≈ 0.44. Net of the qualitative pushes in both directions I
settle at **0.45**, essentially at the CVSG-conditional base rates with the
case-specific pluses and the top-hat minus roughly offsetting.

`predicted_disposition` is **denied** as the single most likely label (0.55),
with the grant mass overwhelmingly plenary grant; GVR/summary routes are
negligible absent any intervening decision. `granted = 0` states the same
binary.

## Claims

- `disposition` 0.45 — restates the top-level probability.
- `relist-increment` 0.97 — the docket shows **two** distributions; a CVSG'd
  petition is redistributed once the SG files, so the only paths to no further
  distribution are settlement/withdrawal or an off-conference disposition,
  both rare.
- `cvsg-increment` 0.02 — a CVSG is already on the docket, so the claim is
  vacuous for this cell and the harness masks it; the number is nominal.

## Uncertainty and discounts

The dominant uncertainty is the **SG's recommendation**, which does not exist
yet and will not for months; my number is an average over it, so it should
look miscalibrated in hindsight once the brief lands. Second, I could not
measure how much of the `high` band's 40% reached-rate is already driven by
CVSG cases specifically — the band folds relist and CVSG signal together, so
treating the CVSG cut and the band rate as independent checks overstates
their independence. Third, my read of the DOL/SG's institutional lean on
surcharge comes from general knowledge of its past ERISA positions, not from
a retrieved filing; discount that link accordingly. Retrieval notes: the
corpus citation lookup for the Mertens/Great-West/Amara/Montanile line
returned no rows (the citation column is sparse — a coverage gap, not absence
of precedent), so the ERISA-line priors rest on the petition, the BIO, and
general knowledge rather than corpus rows. Both provisioned documents had
extractable text (`empty_text: false`); the petition text is truncated at 118
pages, which cost nothing material since the appendix is what is cut.
