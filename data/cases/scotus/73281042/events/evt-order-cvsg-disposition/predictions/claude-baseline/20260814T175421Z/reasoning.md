# Rationale for P(grant family) = 0.40

## Anchors

This is a cert-stage cell at `moment: cvsg`, forward mode, Term 2025, frozen
band `high` (sal-v2), `distribution_count: 2`. Two committed anchors from
`metrics/statpack.md` frame the number, and they agree:

- **CVSG cut (paid scored segment):** among resolved petitions with a CVSG
  (n=163), denied 62.0%, granted 30.1%, gvr 5.5%, dismissed 2.5% — a
  grant-family rate of **~35.6%**, roughly ten times the modern whole-docket
  rate.
- **Salience band table (sal-v2), the scored yardstick:** my band is frozen at
  prediction, so the bracketed `reached` figure governs. Pooling the `high`
  band's bracketed rates over the rendered Terms strictly before this case's
  own (2017–2024, all rendered): ≈ 427/1059 ≈ **40.3%**.

I start at ~0.38 between the two anchors, and the case-specific signals below
net out approximately to zero against each other, leaving me at **0.40** —
essentially the scored band base rate.

## What pushes up from the anchor

- **The attention trail is unusually strong even for a CVSG case.** The
  respondent *waived*; the Court called for a response anyway, then CVSG'd at
  the second conference. Four cert-stage amicus briefs (18 states, SFFA,
  America First Legal, Manhattan Institute) and top Supreme Court counsel
  (Consovoy McCarthy) mark this as a deliberately groomed test case.
- **The decision below sits in genuine tension with this Court's cases.** A
  state court held the First Amendment shields status-based set-asides because
  they "express" a commitment to diversity — hard to square with Runyon,
  Hishon, Roberts, and 303 Creative's own status/message footnote, and in
  direct tension with the Eleventh Circuit's Fearless Fund. The current
  majority's trajectory (SFFA, Ames) runs squarely against the reasoning
  below.
- **The SG is likely sympathetic.** The administration's DEI-enforcement
  posture (the executive orders and NADOHE litigation the petition cites)
  makes a grant-recommending brief more likely than not, and the Court follows
  grant recommendations at high rates.

## What pushes down from the anchor

- **The Article III standing problem is real, not makeweight.** Saadeh never
  applied for any seat — including during 2022–2025, when the program was
  suspended and every seat was open to him — and argued below that he didn't
  need to show he would have. Carney v. Adams is close to on point, and
  standing was never litigated below, so the record is undeveloped exactly
  where the jurisdictional question lives.
- **The program changed in November 2025.** Every at-large seat is now
  reachable through diversity-bar-association membership open to all comers
  (Saadeh himself belongs to a qualifying association). The Court would be
  reviewing a policy design that no longer exists.
- **The state-law ground is unresolved.** The Appellate Division never decided
  the LAD question, so a reversal could be washed out on remand by an adequate
  and independent state ground — the BIO's "advisory opinion" point has force.
- **Posture:** an unpublished, nonprecedential intermediate state-court
  opinion, with discretionary review denied. The Court grants in this posture,
  but rarely, and the asserted split is shallow — Fearless Fund turned on a
  threshold non-expressiveness finding, and cleaner federal vehicles (AAER v.
  ABA and similar suits) are percolating.

The Court knew all of these vehicle arguments when it CVSG'd — the BIO predates
the invitation by four weeks — which is why I don't discount below the
CVSG-conditional anchor. But relative to the *typical* CVSG case, this one's
vehicle is worse and its ideological pull is stronger; I judge those roughly
offsetting.

## The other claims

- **relist-increment 0.97.** A CVSG guarantees redistribution once the SG
  files; the residual 0.03 covers withdrawal, settlement, or dismissal before
  that happens (the CVSG cut shows 2.5% of CVSG'd petitions ending dismissed).
- **cvsg-increment 0.01.** The CVSG is already on the docket, so the claim is
  vacuous for this cell; the harness masks it. The 0.01 covers nothing more
  than the (essentially theoretical) event of a second, superseding
  invitation.

## Uncertainties and discounts

- My largest uncertainty is the **SG's weighing of vehicle against merits
  sympathy** — a "deny, wait for a better vehicle" brief drops P(grant)
  substantially, and I cannot observe the SG's internal posture.
- Second, **how much the November 2025 program change matters at conference**:
  if the Justices see the case as effectively about a superseded policy, the
  denial path dominates regardless of merits interest.
- The corpus citation-filter query I ran returned no comparable priors (the
  citation column is sparse — see `retrieval.md`), so the quantitative
  anchoring rests entirely on the committed statpack cuts, not on retrieved
  case-level priors. The statpack CVSG cell count is modest (n=163 resolved),
  so the 35.6% anchor carries sampling noise of a few points either way.
- Both provisioned document texts extracted cleanly (`empty_text: false`), so
  my read of the petition and BIO is from their text, not inferred from the
  docket.
