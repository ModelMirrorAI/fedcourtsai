# Rationale — P(grant) = 0.003

## The cell

Arrival-moment cert cell (`moment: arrival`), forward mode, paid petition,
band `baseline` frozen under `sal-v3` (matching the committed statpack's
table version), `distribution_count` 0, Term 2026, snapshot
`2026-08-28.json` (provenance `truncated`). The record shows exactly what the
moment's definition promises: the docketing entry and nothing else — petition
filed July 23, 2026, docketed August 27, 2026, response due September 28,
2026, from CA9 Nos. 25-270 / 25-1026 (decided May 13, 2026; rehearing denied
June 15, 2026).

## Anchor

The frozen band is `baseline`, so the yardstick is the baseline band's
bracketed `reached` rate — the whole paid scored segment's grant rate,
unconditional on trajectory, which is also exactly the arrival population's
own base rate the arrival-moment guidance names. Pooling the "Segment base
rate by salience band (sal-v3)" table's baseline `reached` figures over Terms
2017–2025 (strictly before this case's Term 2026, all nine rendered prior
Terms): weighted mean ≈ **6.5%** (≈857 weighted grants over n≈13,163;
per-Term range 5.4%–7.9%).

## Adjustments — all downward, and large

- **Pro se, both petitioners.** Randy Quaid appears as his own attorney (the
  snapshot lists him as petitioner-side attorney, not counsel of record, with
  a personal mailing address); "et ux." is Evi Quaid. The paid-segment anchor
  is dominated by counseled petitions; a pro se paid petition sits far below
  the segment mean.
- **Fact-bound private dispute, no split, no question of general importance.**
  Forward retrieval (CourtListener; see `retrieval.md`) shows the petition
  arises from Quaid v. Granet, C.D. Cal. No. 2:23-cv-06850 (filed August 2023,
  terminated April 2024 — an early dismissal) and a companion suit, appealed
  as consolidated CA9 Nos. 25-270 and 25-1026. Appellees are Craig Granet (an
  attorney appearing for himself) and R. Scott and Lannette Turicchi — the
  buyers of the Quaids' former Montecito property, the subject of the
  petitioners' litigation campaign running since at least 2021 (a prior suit
  against attorney Bruce Berman is on the same district docket). Nothing in
  this shape presents a certworthy federal question.
- **Repeat relitigation posture.** Serial suits against the same opponents,
  dismissed early and affirmed on appeal with rehearing denied, are the
  classic profile of a petition denied at first conference.

Landing point: **0.003** — about 1/20th of the segment anchor, at the level
where pro se fact-bound paid petitions actually resolve. I do not go lower
because the grant family includes GVR and the outcome vocabulary's tail
(dismissal is scored separately, but a mis-parse or an unusual order is never
quite zero).

## The other claims

- `relist-increment` 0.95: from a zero-distribution state this resolves on
  any first distribution, which nearly every accepted paid petition gets; the
  residual is withdrawal or pre-conference procedural dismissal.
- `cvsg-increment` 0.002: no federal interest of any kind.
- `summary-disposition-route` 0.5: stated conditional on a grant, per the
  contract. The statpack's grant family splits roughly evenly between plenary
  grants and GVRs overall (668 granted vs 577 gvr), and in the baseline band
  GVR is about a third of the family; conditional on this petition somehow
  drawing a grant, a cert-order disposition is at least as plausible as
  plenary review, so I state the near-even split rather than a number driven
  by either tail story. This claim carries most of my per-claim uncertainty —
  the condition is a tail event I put at 0.003.
- `dissent-from-denial` 0.005: a handful of noted dissents per Term over
  thousands of denials, and nothing here attracts one.

## Uncertainty and discounts

- **No petition text.** No `record/documents/` was provisioned, so I never
  saw the questions presented; the pipeline simply had nothing to fetch. My read of the petition's
  substance is inference from the docket metadata plus the lower-court
  record, not from the QP text. If the petition somehow raises a clean
  procedural question (e.g. something jurisdictional the Ninth Circuit
  published on), I would not see it from here — that is the main way 0.003 is
  wrong, and it is bounded by the pro se/vehicle problems regardless.
- **Corpus priors were uninformative.** The one `fedcourts query` I ran
  ranked by recency and returned recent substantive applications, not
  comparable pro se cert petitions; the statpack carried the real anchor. No
  claim here rests on the query's rows.
- The snapshot is dated 2026-08-28 with cutoff 2026-08-28 — one day ahead of
  the run date, which is a provisioning timestamp artifact, not information
  from the future; the snapshot content is the docketing-day record.
