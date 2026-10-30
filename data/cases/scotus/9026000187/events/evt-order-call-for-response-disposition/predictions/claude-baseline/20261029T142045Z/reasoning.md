# Rationale: P(grant) = 0.05

**Inputs read.** Snapshot `record/snapshots/2026-10-06.json` (three entries:
petition filed, one distribution, response requested). I read
`questions-presented.txt`, `petition.txt`, and `appendix.txt` (the Fifth
Circuit opinion at 170 F.4th 960 with Judge Wiener's concurrence in the
judgment, and the N.D. Tex. opinion). None was truncated or OCR-derived. No
response or BIO exists yet, by the moment's definition. `context.json`:
mode `forward`, band `baseline` (sal-v4), distribution_count 1, no CVSG,
Term 2026.

**Anchor.** In `metrics/statpack.md`, *Segment base rate by salience band
(sal-v4)*, the `baseline` bracketed `reached` rate over OT2017–OT2025
runs 4.0–5.9% per Term (e.g., OT2025 4.0%, n=1314; OT2024 5.9%, n=1274).
That puts the pooled rate near 5%. I excluded OT2026, which is my own
Term. Cross-checks: ca5 originating-circuit grant family is ~3.8%, and the
paid-segment no-CVSG grant family is ~6.4%.

**Adjustment for the called-for response.** No committed table conditions
on a response request. A call for response is a low bar: it often reflects one
chambers' interest. It modestly raises grant odds over the baseline
population, which includes many waived petitions that are never looked at.
Taken alone, it would push me to perhaps 7–9%.

**Adjustments down.**
- The question is a well-known split. Retrieval surfaced several prior
  petitions on it (Sanchez, No. 17-1638; Strain v. Regalado, No. 20-1562;
  others). As I recall, the Court denied each of them. I did not verify those
  dispositions in this cell, so that is my background knowledge, not a
  checked fact. Repeated denials suggest the Court is waiting for a cleaner
  vehicle.
- Qualified immunity is an independent alternative ground. The district court
  reached it, and Judge Wiener's concurrence rests on it. That is a classic
  vehicle defect.
- The outcome-determinative fact (the unopened email) may defeat the claim even
  under an objective standard.

**Net:** 0.05. My main uncertainty is whether the Court now wants to resolve
the post-Kingsley split. If it does, a fully developed 5–4 circuit split
could carry even an imperfect vehicle. That is why I am not lower.

**Other claims.** `relist-increment` 0.96: masked on this moment, but the
petition will be redistributed after the response. `cvsg-increment` 0.02:
the respondent is a private party, and no federal interest is apparent.
`summary-disposition-route` 0.12 conditional on grant: no intervening
decision exists, and a summary reversal on a split question is improbable.
`dissent-from-denial` 0.07 conditional on denial: the facts are stark (an
infant's death), but a split-based petition with vehicle problems usually
draws silence. `order-writers` puts most of that mass on Sotomayor and
Jackson.

**`big_case_score` 0.45.** The legal question has broad reach in jail
litigation. The case itself is a narrow damages claim.

**Retrieval caveats.** The corpus query surface has no free-text search. My
queries returned no relevant priors, so my priors rest on the statpack and on
background legal knowledge.
