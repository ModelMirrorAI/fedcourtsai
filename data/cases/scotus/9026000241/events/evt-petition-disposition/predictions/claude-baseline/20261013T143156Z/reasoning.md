# Why P(grant) = 0.005

**Inputs read:**
- Snapshot `record/snapshots/2026-10-13.json` (forward mode, no cutoff).
- `record/context.json`: band `baseline` under sal-v4, `distribution_count`
  1, no CVSG, Term 2026.
- The provisioned QP section, the petition, and the appendix (the Fifth
  Circuit opinion and the district court's memorandum and recommendation).
- No brief in opposition exists, because the respondents filed a waiver on
  Sep 29, 2026.

**Anchor.** The statpack's sal-v4 "Segment base rate by salience band" table
has a `baseline` column, and its version matches my context. Pooling the
bracketed `reached` figures over the Terms strictly before 2026 (2017–2025)
gives roughly 5% (Term values range from 3.8% to 5.9%, each on n≈1,200–1,700).
That number is the grant rate among every paid petition that ever sat in
`baseline`. Most of it comes from petitions that later climbed the ladder
(response requested, relists). The relist-count cut's relist-0 row (granted
1.2%, gvr 0.5%) is the terminal floor.

**Adjustments, all downward:**
- **Response waived, none requested.** The Court essentially never grants a
  paid petition without first calling for a response. A grant here therefore
  needs two unlikely steps: a call for a response, then a grant.
- **Vehicle.** The Fifth Circuit's opinion is an unpublished per curiam on the
  summary calendar. It held the petitioners' *Nieves*-exception evidence (the
  Lt. Price testimony and the uncharged employee) forfeited because it was
  first raised on appeal. The petitioners also did not dispute probable cause
  on appeal. A forfeiture ground blocks the QP from being reached.
- **Claimed split.** The petition claims a split with the Eighth Circuit
  (*Murphy v. Schmitt*, 2025). But a forfeiture-based unpublished affirmance
  cannot create a real split, and the QP is framed as error correction about
  *Gonzalez*.
- **Counsel and presentation.** The petition comes from a small Houston firm
  and contains visible drafting errors. Experienced Supreme Court counsel are
  absent.
- **No GVR route.** *Gonzalez* predates the decision below, and the panel
  applied it.

I land at 0.5%, well under the `baseline` reached rate and below the
relist-0 terminal grant-family rate (about 1.7%). That relist-0 rate includes
petitions with responses and stronger presentations.

**Increments:**
- **Relist-increment, 0.05.** A second distribution would mostly require a
  call for a response, or a reschedule (which counts as a distribution).
- **CVSG-increment, 0.002.** I see no federal interest.
- **Summary-disposition-route, 0.30.** This is conditional on a grant. In the
  rare world where the Court acts, a *Gonzalez*-style summary vacatur is
  plausible.
- **Dissent-from-denial, 0.01.**

**Uncertainty.** I did not use CourtListener or the corpus query tooling. The
provisioned record was decisive enough that extra retrieval would not
plausibly move a sub-1% number. The main tail risk is a call for a response
that I did not anticipate.
