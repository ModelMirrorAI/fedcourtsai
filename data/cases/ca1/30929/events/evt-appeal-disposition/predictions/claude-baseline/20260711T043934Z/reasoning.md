# Ortiz-Romero v. Gov't Development Bank of PR — appeal disposition (ca1/30929, No. 19-2084)

## The question

Will the First Circuit grant relief to the appellant — i.e., disturb the
district court's judgment — and under which disposition label will the appeal
resolve?

## The record (from the provisioned snapshot, `2026-07-11.json`)

- Civil, private, **civil-rights** appeal (nature of suit 3440 Other Civil
  Rights) from the District of Puerto Rico (3:18-cv-01993, Judge Jay A.
  García-Gregory).
- The underlying suit was filed **2018-12-20**; judgment entered
  **2019-09-11** — under nine months from filing, which strongly suggests the
  case ended on a motion (dismissal or early summary disposition), not a
  trial. The **plaintiff, Pedro Ortiz-Romero, is the appellant** (notice of
  appeal 2019-10-10; docketed in the First Circuit 2019-11-01).
- Appellees are the **Government Development Bank of Puerto Rico** and two
  officials associated with it, Christian Sobrino Vega and Guillermo
  Camba-Casas.
- The last docketed activity in the snapshot is a **2020-03-24 show-cause
  order**: because the Commonwealth of Puerto Rico filed a Title III petition
  under PROMESA (48 U.S.C. §§ 2161 et seq.) on May 3, 2017, and § 2161(a)
  incorporates the Bankruptcy Code's automatic-stay provisions, the panel
  directed the parties to brief within fourteen days whether the automatic
  stay applies to all or part of the appeal.

## Governing standards and priors

1. **Merits baseline.** A plaintiff-appellant in a civil-rights case who lost
   below faces steep odds: federal courts of appeals reverse on the order of
   10% of civil appeals, and lower still where the district court disposed of
   the case at the motion stage on immunity/plausibility grounds — the common
   posture for §1983-type suits against government instrumentalities and
   officials.
2. **PROMESA overlay.** The suit targets a Commonwealth instrumentality (GDB —
   which itself restructured its liabilities through a PROMESA Title VI
   qualified modification consummated in late 2018) and Commonwealth
   officials, while the Commonwealth's Title III case was pending. An action
   *initiated against* the debtor is subject to the automatic stay on appeal
   regardless of who appeals, so the show-cause order materially raises the
   chance this appeal was stayed/held in abeyance and later resolved
   *procedurally* — dismissed pursuant to the confirmed plan of adjustment,
   discharged/channeled claims, voluntary dismissal, or dismissal for want of
   prosecution — rather than decided on the merits.
3. **Corpus base rates** (committed statpack, CA1 resolved cases): **other
   86.3%, dismissed 8.0%, denied 5.0%, granted 0.7%**. Note the label
   mechanics in this pipeline: a free-text appellate disposition of
   "affirmed" *or* "reversed" normalizes to `other`; only text containing
   grant/deny/dismiss/withdraw maps to those labels. So even an appellant
   win on the merits would very likely be recorded as `other`, and
   `granted` (the binary target) is rare for appeal dispositions.

## Weighing

- If the appeal reached the merits, affirmance is far more likely than
  reversal (plaintiff lost below on an early motion; PROMESA discharge and
  Eleventh Amendment / official-immunity defenses loom over claims against
  GDB and its officers). Either merits outcome lands on the `other` label.
- The stay posture shifts real probability mass toward `dismissed`: PROMESA
  stays froze many such appeals for years, and a meaningful fraction ended in
  procedural dismissal after the Commonwealth's plan of adjustment took
  effect (March 2022) rather than in a merits decision.
- My rough distribution: **other ≈ 0.62** (merits decision, overwhelmingly
  affirmance), **dismissed ≈ 0.28**, denied ≈ 0.04, withdrawn ≈ 0.02,
  granted/granted-in-part ≈ 0.02, residual to rounding. On any path, relief
  *recorded as* `granted` is a tail event.

## Prediction

- `predicted_disposition`: **other** (most likely a merits affirmance,
  which this pipeline's normalizer labels `other`).
- `granted`: **0**; `probability` P(granted) = **0.02** — consistent with the
  CA1 granted base rate (0.7%) plus a small allowance for label noise.
- No panel is identified in the snapshot, so no per-judge votes are offered.

## Caveats

- **Stale snapshot in a forward cell.** The snapshot was provisioned
  2026-07-11 but its docket data was last refreshed 2020-03-25 (the docket
  has been blocked from indexing since 2021). An appeal docketed in 2019 has
  almost certainly been disposed of in reality by mid-2026. Honoring the
  "predict as if undecided — never retrieve this case's outcome" rule, I
  deliberately did **not** fetch this docket's current state from
  CourtListener, since any live read would likely reveal the disposition.
  This is flagged in `flags.json`.
- I do not know this case's actual outcome from prior knowledge; the analysis
  above rests solely on the pre-decision record and general legal context.
