# Rationale — why P(grant) = 0.015

**Anchor.** This is an arrival-moment cell (`moment: arrival`), forward mode,
with a frozen band of `baseline` under `sal-v3` — matching the statpack band
table's version, so the table is a valid anchor. The scored yardstick for a
frozen `baseline` band is the bracketed `reached` rate, which for the weakest
band is the whole paid scored segment's rate — exactly the arrival-population
anchor the prompt prescribes. Pooling the baseline `reached` rates over the
Term rows strictly before this case's own Term (2026), i.e. OT2017–OT2025
(n = 1691, 1560, 1456, 1792, 1579, 1239, 1358, 1312, 1176; total 13,163
weighted resolved), gives a pooled grant-family rate of roughly **6.5%**. The
petitioner is not a federal party, so the `federal` arrival-class segment does
not apply.

**Adjustments down, and why they are large.** Nearly everything
case-specific points below the anchor:

- **Pure error-correction framing.** All four QPs are "did the court err"
  questions; QPs 3 and 4 are addressed to the *district court's* judgment,
  which is not even the judgment under review. No circuit split is alleged
  anywhere in the petition (I searched the text), and the table of
  authorities is dominated by district-court decisions.
- **The decision below is an unpublished, unreasoned per curiam.** The
  Fourth Circuit affirmed in a single paragraph ("we have reviewed the record
  and find no reversible error"), without oral argument, and no judge
  requested an en banc poll. There is no reasoned opinion for the Court to
  review, the classic poor-vehicle profile.
- **Post-Groff posture.** Groff v. DeJoy (2023) recently restated the Title
  VII undue-hardship standard; the petition asks the Court to police its
  application to one summary-judgment record, which is not cert-worthy work.
  The Court has also repeatedly denied certiorari in COVID-19
  vaccine-mandate religious-objection cases.
- **The second question is a Rule 56(d) discovery-management ruling** —
  discretionary, fact-bound, and reviewed for abuse of discretion.
- Small-firm counsel, private nonprofit respondent, no amici at arrival.

The residual above a pure floor reflects the grant *family* including GVR: a
religious-accommodation decision from the Court this Term could produce a
GVR of a case in this posture. Hence **0.015**, roughly a quarter of the
baseline-band pooled anchor.

**Claim numbers.**

- `disposition` 0.015 — restates the top-level probability.
- `relist-increment` 0.96 — the record shows **zero distributions**, so this
  is P(ever distributed). A timely paid petition with a response due is
  nearly always distributed for conference; the complement covers dismissal
  under Rule 46, withdrawal, or procedural default before distribution.
- `cvsg-increment` 0.005 — the paid-segment CVSG incidence is about 1.3%
  (173/13,423 in the statpack CVSG cut), concentrated in cases with a
  federal interest or a developed split; this private fact-bound dispute has
  neither, so I set it well below the unconditional incidence.
- `summary-disposition-route` 0.55 — conditional on any grant. The statpack's
  modern-cert disposition section shows GVRs are roughly 46% of the grant
  family docket-wide (576 gvr vs. 674 granted), and in the baseline band the
  terminal split (granted 0.8% / gvr 0.4%) puts GVR at about a third. I set
  it above both because, conditional on *this* petition being in the grant
  family, plenary review of an unreasoned unpublished per curiam is the least
  plausible route — a GVR in light of an intervening decision is the
  realistic one.
- `dissent-from-denial` 0.025 — no published baseline (banked). Statements
  respecting denial are rare, and the religious-liberty Justices have written
  on constitutional free-exercise vehicles, not fact-bound Title VII
  summary-judgment affirmances.

**Timeliness check.** Rehearing was denied March 30, 2026; ninety days ran to
June 28, 2026; the docket's petition entry is dated June 26, 2026. Timely, so
no procedural-dismissal discount.

**Uncertainty and where to discount me.** I read the QPs, the petition's
reasons-for-granting sections, and the appended district-court and Fourth
Circuit dispositions, but skimmed rather than exhaustively read the 59-page
petition text. My retrieval was thin: one corpus `query` (a `--citation`
lookup misused as a cases-citing-Groff search — it returned nothing, as the
tool's own note explains) and CourtListener lookups confirming the CA4 docket
and the absence of a published opinion. I did not independently verify how
many parallel vaccine-accommodation petitions the Court has denied this Term;
that belief rests on general knowledge through my training data. If the Court
takes a Groff-application case this Term, the GVR tail (and hence
`probability`) is modestly understated.
