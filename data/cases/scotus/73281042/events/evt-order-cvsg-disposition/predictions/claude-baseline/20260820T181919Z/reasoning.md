# Rationale for the numbers (claude-baseline, CVSG moment)

**P(any grant) = 0.40.**

## Anchors

- **Salience band.** `record/context.json` freezes `band: high` under
  `sal-v3`, matching the statpack band table's version, so the scored
  baseline is the high band's bracketed `reached` rate pooled over Terms
  strictly before this case's own (Term 2025). Pooling the rendered rows
  OT2017–OT2024 gives ≈ **40.9%** (≈439 weighted grants over n≈1,074); the
  OT2025 row itself reads 44.8% reached but is this case's own Term, so I
  treat it as context only.
- **CVSG cut** (paid scored segment, denial-reweighted): among resolved
  CVSG'd petitions, granted 29.4% + gvr 5.5% ≈ **35% grant family**, versus
  ~6% for non-CVSG. This is a terminal-status cut, not a forward hazard from
  my vantage, but it brackets the same neighborhood as the band anchor.
- **Relist cut**: the docket shows two distributions; terminal relist-1
  petitions run ~13% grant family. Spent as a level — the CVSG supersedes it
  — but it confirms the trajectory was already elevated before the CVSG.

## Adjustments

Up from the ~0.35–0.41 anchor range:

- Two affirmative acts of the Court's attention on one docket: a requested
  response after the respondent waived, then the CVSG.
- The QP is squarely aligned with the current majority's demonstrated
  interests (*SFFA*, *303 Creative*); the sitting SG is very likely to agree
  with petitioner on the merits, and the Court usually follows the SG's cert
  recommendation.
- Elite cert counsel (Consovoy McCarthy / Scalia Law Clinic) and a
  heavyweight amicus bloc at the petition stage: West Virginia + 17 states,
  SFFA/AAER/Do No Harm, America First Legal, Manhattan Institute.

Down:

- **Standing** (BIO Part I): petitioner never applied, or said he would
  apply, for a leadership position — *Carney v. Adams* was a unanimous exit
  on nearly identical facts, and it gives the SG a clean vehicle-based
  denial recommendation whatever the administration thinks of the merits.
- **Changed policy**: the Association amended the selection process in
  November 2025; the process litigated below is no longer in force.
- **Posture**: unpublished, nonprecedential state intermediate-court
  decision (state high court denied certification), with the state-law claim
  undecided below — finality and advisory-opinion objections under the
  *Cox*/*ASARCO* line, and the statpack shows NJ Appellate Division
  petitions essentially never granted absent exactly this kind of signal.
- **No developed split**: the BIO plausibly characterizes the claimed
  conflict as one with this Court's precedents rather than a lower-court
  split; percolating parallel DEI cases give the Court the option to wait.

Netting: the case sits above the average CVSG'd petition on salience and
alignment and below it on vehicle quality. I land at **0.40**, essentially
on the pooled high-band anchor, slightly above the CVSG cut's terminal rate.
`granted = 0` and `predicted_disposition = denied` state the modal single
outcome (denial ≈ 0.55–0.60 once dismissal residue is counted); the 0.40 is
the grant-family probability, dominated by a plenary grant (GVR/summary
routes are the 0.10 conditional claim).

## Claim-level numbers

- `disposition` 0.40 — restates the top-level probability.
- `relist-increment` 0.97 — the record shows two distributions; a CVSG'd
  petition is redistributed once the SG files, so a further distribution
  fails only on a pre-brief dismissal/withdrawal.
- `cvsg-increment` 0.01 — the CVSG is already on the docket; the claim is
  vacuous for this cell (the harness masks it) and a second invitation
  essentially never issues.
- `summary-disposition-route` 0.10 — conditional on a grant: no intervening
  decision exists to GVR against (checked CourtListener for post-2024 SCOTUS
  expressive-association merits decisions — none), and a summary reversal of
  an unpublished decision over an undecided state-law claim is unlikely; the
  residual covers something relevant being decided during the long CVSG
  pendency.
- `dissent-from-denial` 0.35 — conditional on denial: high-salience denial
  after a CVSG with an 18-state amicus bloc; Thomas/Alito write in this
  space. No published baseline; banked honestly.

## Uncertainty and discounts

The dominant uncertainty is the **SG's recommendation**, which will not
exist for months and which the outcome will largely track: grant if the SG
says the vehicle holds, deny if the SG says wait for a cleaner case. I
cannot observe anything that predicts that recommendation beyond the
administration's evident merits sympathy and the vehicle defects, and the
two point in opposite directions — hence a number near the pooled anchor
rather than far from it. Secondary uncertainty: whether the November 2025
policy change moots or merely complicates the case (the BIO's mootness
framing is contestable since damages/state-claim theories may survive).
All provisioned documents (petition, BIO, QP) had extractable text; the
snapshot is `truncated`-provenance but discloses a full proceedings list
through the CVSG. Live docket metadata (CourtListener) shows the case still
pending as of 2026-08-20, so the forward cell is well-provisioned.

Corpus vintage: not checked against `corpus-info` this run — all base rates
were read from the committed `metrics/statpack.md`, and the one corpus
`query` I ran returned no rows (sparse citation coverage, noted in
`retrieval.md`); no claim here rests on corpus blob state.
