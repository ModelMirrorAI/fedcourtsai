# Reasoning — why P(grant) = 0.01

## Anchor

`record/context.json` freezes this cell at band **baseline** (sal-v2),
`distribution_count` 0, forward mode, Term 2026. Per the prompt contract I
anchor on the baseline band's bracketed **`reached`** rate in the statpack's
"Segment base rate by salience band (sal-v2)" table, pooled over the rendered
Terms strictly before this case's own (OT2017–OT2025): roughly **862 grants
over a 13,163 risk-set denominator, ≈ 6.5%**. That figure is the paid scored
segment's whole grant-family rate, unconditional on trajectory — the right
starting point for a petition that has not yet been distributed.

## Adjustments down (large)

Nearly everything case-specific pushes well below the anchor:

- **No circuit split is alleged anywhere in the petition.** The two "Reasons
  for Granting the Writ" are (I) the evidence was legally insufficient to
  support the employer's undue-hardship defense and (II) the district court
  wrongly denied a Rule 56(d) motion for a medical-expert affidavit. Both are
  error-correction arguments the Court almost never takes.
- **The QPs are fact-bound "did the court err" questions**, with QPs 1/3 and
  2/4 duplicating each other at the appellate and district-court level.
- **The decision below is unreported** (the petition says so at Opinions
  Below; CourtListener has no indexed CA4 opinion for docket 25-1696), and
  rehearing en banc was denied without noted dissent — a weak vehicle marker.
- **The legal standard is freshly settled.** Groff v. DeJoy (2023) restated
  Title VII's undue-hardship test; the petition asks only whether the Fourth
  Circuit applied it correctly to one summary-judgment record. The Court has
  consistently denied fact-bound COVID-vaccine religious-accommodation
  petitions since Groff.
- **Petition-quality signals are poor**: the jurisdictional statement invokes
  28 U.S.C. § 1257 (state-court review) for a federal court of appeals
  judgment (§ 1254 is the correct grant), and the filing is a solo-counsel
  petition against a private nonprofit with no amicus interest visible.
- **No GVR route**: no intervening decision of the Court postdates the March
  2026 CA4 ruling on this issue, so the grant family's GVR component is also
  effectively closed.

The one mild upward consideration is that this is a **paid** petition in a
subject area (religious accommodation) where several Justices are engaged.
That keeps me from going to the floor, but the terminal baseline-band rate for
never-relisted petitions (grant + gvr ≈ 1.2%) is a better description of this
petition than the 6.5% risk-set average, which is carried mostly by petitions
that later climb bands. This one has essentially no climb prospects.

**P(grant family) = 0.01.** `granted` = 0, `predicted_disposition` = `denied`.

## Claims

- `disposition` **0.01** — equals the top-level probability, as required.
- `relist-increment` **0.96** — the frozen state is zero distributions, so the
  claim resolves true if the petition is ever distributed at all. A docketed
  paid petition essentially always reaches a conference; the residual 0.04
  covers pre-conference dismissal (settlement/Rule 46) or withdrawal.
- `cvsg-increment` **0.005** — the paid-segment CVSG rate is ~1.3% overall
  (173/13,404 in the statpack's CVSG cut), and this private, splitless,
  fact-bound employment dispute is far below the average CVSG candidate.

## Uncertainties and discounts

- **No brief in opposition exists yet** (response due August 24, 2026), so I
  have only the petitioner's account of the record. That cuts little here:
  even taking the petition's facts as given, its grant case is error
  correction.
- **This distribution-moment cell ran before any distribution**: the docket
  shows only the petition filing, so the conditioning state is close to an
  arrival-time record. I anchored on the risk-set rate accordingly and
  adjusted down from it.
- Corpus retrieval surfaced no close comparables (the query surface has no
  subject-matter filter on SCOTUS rows), so the subject-specific adjustment —
  the post-Groff denial pattern for vaccine-mandate accommodation petitions —
  rests on general knowledge rather than a corpus-measured rate. If that
  pattern is weaker than I believe, my number is too low by a factor of
  roughly two; it would still round to a denial forecast.
