# Rationale — P(any grant) = 0.05, predicted disposition `dismissed`

## Anchors

- **Salience band (frozen): `high` under sal-v3.** The scored yardstick is the
  band's bracketed `reached` rate pooled over Terms strictly before this
  case's (OT2025). Pooling the statpack's per-Term table over 2017–2024 gives
  ≈41% (weighted n≈1074). Statpack figures are the committed
  `metrics/statpack.md`; the corpus rows I retrieved carried
  `last_live_polled` stamps of 2026-08-03, which is the freshest vintage
  indicator available to this cell (`fedcourts corpus-info` is not servable
  through the cell's corpus service — it errors on the ranged backend without
  the remote URL — so I could not print the blob-wide stamp).
- **CVSG cut:** resolved CVSG'd petitions run granted 29.4% + gvr 5.5% ≈ 35%
  grant family, versus ~6% for the no-CVSG paid segment.

Absent any post-snapshot information I would have priced this at ~0.45:
slightly above the ~41% band anchor, because the case-specific signals are
unusually strong (a CVSG issued three days after the *first* conference; an
alleged three-circuit split the petition documents; Verrilli as counsel of
record; Chamber/NAM and Shipbuilders Council cert-stage amici), offset by the
BIO's genuine vehicle arguments — the interlocutory posture (the Fourth
Circuit reversed a dismissal; no final judgment), the claim that the Fourth
Circuit adopted no categorical rule so the petition "does not present the
question presented," and en banc denied without a single vote (suggesting the
panel decision may be less categorical than the petition frames it).

## The decisive adjustment

This is a `forward` cell whose snapshot is seven months old, and retrieval is
unrestricted. The live record shows the case settling out from under the
petition: SCOTUSblog's docket timeline shows a **motion to hold the petition
in abeyance submitted May 18, 2026 by petitioners**; Law360 reports the
plaintiffs **dismissed General Dynamics from the underlying suit and reached
settlements with the remaining defendants**; respondent counsel's own case
page confirms Huntington Ingalls/Marinette Marine/Serco affiliate settlements
as of March 19, 2026 (Faststream had settled in September 2025). The case's
own disposition has **not** occurred (CourtListener shows `date_terminated:
null`, and nothing I found reports a grant, denial, or dismissal), so this is
forward signal, not leakage — flagged in `flags.json` because it is decisive.

A grant now requires the settlement to fall apart. My mass:

| path | P |
| --- | --- |
| settlements finalize → Rule 46 dismissal / withdrawal | 0.75 |
| denial (clean-up of a mooted petition, or SG-recommended deny on a resumed case) | 0.18 |
| grant family (settlement collapses, case resumes post-CVSG course) | 0.05 |
| other | 0.02 |

P(any grant) = 0.05 ≈ P(collapse ~0.10) × P(grant | resumed ~0.45). The
`dismissed` label is what the pipeline records for Rule 46 dismissals — the
corpus's recent dismissed priors (e.g., Oregon v. Maney, 25-960, dismissed
2026-07-17 after one distribution) show exactly this shape.

## Claim-level notes

- `disposition` 0.05 — equals the top-level probability, per the contract.
- `relist-increment` 0.25 — the record freezes distribution_count = 1; the
  dismissal path needs no further conference, while the denial and grant paths
  (~0.23 combined) essentially guarantee redistribution, plus a small chance
  the Court distributes the abeyance motion or the petition anyway.
- `cvsg-increment` 0.02 — vacuous on this cell (the CVSG is on the docket;
  the harness masks it); stated because the set is mandatory.
- `summary-disposition-route` 0.10 — conditional on a grant: no intervening
  decision to GVR in light of; a resumed grant would be plenary.
- `dissent-from-denial` 0.04 — conditional on a denial: mootness-driven
  denials of settled commercial cases draw no writing; small residual for a
  substantive denial after an SG deny recommendation.

## Where to discount me

- The settlement/abeyance picture rests on secondary reporting (a Law360
  headline, SCOTUSblog's timeline, and counsel's case page, each read through
  a summarizing fetch); supremecourt.gov's docket page returned 403, so I
  could not read the authoritative docket entries after January 12, 2026. If
  the abeyance motion was denied, or reporting mis-states the settlement
  scope, the dismissal mass is too high and the truth moves toward my
  counterfactual 0.45.
- The 0.10 settlement-collapse figure is judgment, not a base rate: no
  statpack cut prices "settled while CVSG pending."
- Timing of class-settlement final approval (and hence of the dismissal) is
  genuinely uncertain; that mostly moves *when*, not *what*.
