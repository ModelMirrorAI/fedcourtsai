# Rationale — P(grant family) = 0.55 at the CVSG moment

## Anchors

Two committed anchors from `metrics/statpack.md`, read against my frozen
context (`band: high`, `salience_version: sal-v3`, `distribution_count: 2`,
`cvsg_date: 2026-06-29`, Term 2025, forward mode):

- **Salience band.** The sal-v3 segment table's `high` band, bracketed
  `reached` rate pooled over Terms strictly before this case's own (2017–2024,
  weighted by the bracketed n): ≈ **41%** (≈ 439 grants over n ≈ 1,074). The
  table's salience version matches my context's, so the band is a valid anchor.
- **CVSG cut** (paid scored segment): among CVSG'd petitions, granted 29.4% +
  gvr 5.5% ≈ **35% grant family** (n = 163 resolved), against ~6% for the
  non-CVSG segment.

The two anchors agree on the mid-to-high 30s as the population rate for a
petition in this position.

## Adjustments up (to 0.55)

- **A federal court of appeals invalidated a state election statute on
  federal constitutional grounds.** That posture is a classic certiorari
  trigger independent of any split: the Court rarely leaves a federal
  invalidation of a state statute standing unreviewed, and the petitioner is
  the Commonwealth itself.
- **The Court's own engagement is unusually strong even within the CVSG
  class**: it called for a response on 4/1/2026 after *every* respondent had
  waived, relisted once (4/17 and 6/25 conferences), and then issued the CVSG.
- **Two petitions, cross-party support.** The docket is vided with No. 25-962
  (the RNC's petition from the same judgment); the RNC respondents filed in
  *support* of this petition, and Pennsylvania legislative leaders filed as
  amici. The en banc denial drew two dissents claiming a 7–4 circuit split
  over Anderson-Burdick's scrutiny tiers.
- **The SG will likely support review.** The current administration has
  litigated in favor of state ballot-integrity enforcement; a grant or
  GVR-in-light-of-Coalfield recommendation is the likelier filing, and the
  Court follows SG grant recommendations at a high rate.
- **The mootness exit also feeds the grant family.** The petition's lead ask
  is a GVR in light of Center for Coalfield Justice (Pa. 2025); and if the
  pending Baxter case moots the federal question, a Munsingwear vacatur — which
  this pipeline's vocabulary counts as `gvr`, i.e. a grant — is a natural
  disposition, since the Commonwealth would seek vacatur of the adverse Third
  Circuit precedent.

## Adjustments down (why not higher)

- **62% of resolved CVSG'd petitions in the pack were still denied.** The
  CVSG is a signal of attention, not a commitment.
- **A live vehicle problem.** The BIO's strongest card: Baxter v. Philadelphia
  Board of Elections is pending in the Pennsylvania Supreme Court on whether
  the date requirement violates the state constitution's Free and Equal
  Elections Clause (argued September 2025; my web check on 2026-08-20 surfaced
  no decision, so it has been under advisement ~11 months). A state-ground
  invalidation moots the federal QP; part of that path's mass ends in a plain
  denial or dismissal rather than a vacatur.
- The panel decision rests partly on a state-law reading the petition itself
  says Coalfield Justice has already undercut — which supports the GVR route
  but argues against needing plenary review.

Net: I place the case well above the band/CVSG population rates because its
signals (state petitioner, statute struck down, companion petitions, called-for
response, likely SG support) are each individually associated with grants and
they all point the same way here; the mootness overhang is what keeps me at
0.55 rather than 0.65+.

## Claim-level notes

- `relist-increment` 0.97: mechanical — after a CVSG the petition is
  redistributed once the SG files, and every disposition path (grant, GVR,
  deny) passes through at least one further conference; the residual mass is
  an off-conference dismissal/withdrawal before any redistribution.
- `cvsg-increment` 0.02: vacuous here (CVSG already on the docket); stated per
  contract, harness masks it.
- `summary-disposition-route` 0.35 (conditional on grant): the lead ask is
  itself a GVR and the Baxter-mootness path ends in vacatur, but the CVSG
  tilts toward plenary consideration.
- `dissent-from-denial` 0.45 (conditional on denial): high-salience,
  CVSG'd, with a claimed split and prior separate writings in the Ritter
  sequence; no published baseline — banked, stated honestly.

## Uncertainty and discounts

- Largest uncertainty: **Baxter's timing and content**, which I cannot
  observe in advance, and **the SG's actual recommendation**.
- The statpack's CVSG cut is small (n = 163) and not conditioned on the band;
  the band table is not conditioned on CVSG — neither isolates a
  band-high-plus-CVSG population, so the joint anchor is my judgment, not a
  committed number.
- Base rates are from the committed `metrics/statpack.md` (the statpack in the
  repo at run time); corpus rows I touched via `fedcourts query` showed
  `last_live_polled` 2026-08-16/19, but no anchor rests on corpus row state.
- Provisioned documents were complete (petition, QP, BIO all with extracted
  text; BIO is a 94-page concatenation of several respondents' briefs, which I
  read selectively for the lead arguments).
- Forward-mode etiquette: my web searches surfaced only companion-case status
  (Baxter pending) and pre-decision background; nothing about this petition's
  own disposition, which cannot yet exist (CVSG issued 6/29/2026, SG brief not
  yet filed as of prediction).
