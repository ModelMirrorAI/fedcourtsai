# Queen v. Hepburn (scotus/1018480) — evt-petition-disposition

## What the snapshot supports

The 2026-07-02 snapshot is nearly empty: no docket entries, no docket number,
no filed/argued/terminated dates, no cert-grant or cert-denied dates, no
assigned judges or parties beyond the caption. The only substantive signals
are:

- Caption: **Queen v. Hepburn**, court `scotus`.
- One linked opinion cluster (CourtListener cluster 85002) — the docket is
  associated with a published opinion, which indicates the case reached a
  merits decision rather than dying at a screening stage.
- The docket is a bulk-ingested historical SCOTUS record (source 16, no PACER
  linkage), consistent with the pre-1925 era in which the Supreme Court's
  appellate docket was overwhelmingly **mandatory jurisdiction** (writ of
  error / appeal), not discretionary certiorari.

## The legal question and the governing frame

The event asks for the disposition of the "petition" for this case. For a
mandatory-jurisdiction-era SCOTUS case that produced a published opinion, the
realistic disposition space is a merits outcome (affirm/reverse — mapped to
`other` in this project's taxonomy) or a dismissal (e.g. for want of
jurisdiction), not the modern grant/deny-cert dichotomy. "Granted" in the
schema's binary sense is therefore very unlikely a priori.

## Base rates (corpus)

`fedcourts stats --court scotus --resolved-only --group-by disposition` over
the 296 resolved SCOTUS cases in the corpus:

| disposition | share |
|---|---|
| other | 78.4% |
| dismissed | 15.9% |
| denied | 4.4% |
| granted | 1.4% |

A sample of resolved priors from `fedcourts query --court scotus` confirms the
pattern: historical SCOTUS dockets with a linked published opinion
overwhelmingly carry disposition `other` (merits affirm/reverse), with
`dismissed` the main alternative.

## Prediction

- **predicted_disposition: `other`** — the modal outcome for a historical
  SCOTUS docket with a published merits opinion, and the linked cluster makes
  a screening-stage dismissal less likely than the unconditional base rate.
- **granted: 0, probability: 0.02** — anchored on the corpus grant base rate
  (1.4%), rounded up slightly for taxonomy noise.
- **confidence: 0.55** — moderate: the disposition-class call (`other` vs
  `dismissed`) rides almost entirely on base rates plus the single
  opinion-cluster signal, because the snapshot carries no case-specific facts.
- **No per-judge votes** — the snapshot names no panel, so any vote breakdown
  would be fabricated.

## Candor notes

1. **Sparse snapshot.** This prediction is essentially a calibrated base-rate
   call; the snapshot contains no petition text, no docket entries, and no
   procedural history to reason over. Flagged as `data-quality` in
   `flags.json`.
2. **Training-data awareness.** Queen v. Hepburn is a well-known historical
   Supreme Court case (an 1813 freedom suit decided on a writ of error, with
   the lower-court judgment affirmed). Its outcome is in this model's training
   data, so for backtest purposes this cell cannot be treated as a blind
   prediction. I have grounded the numbers above in the snapshot and corpus
   base rates — which independently point the same way (a merits affirmance
   maps to `other`, not `granted`) — but the leakage caveat is flagged so
   evaluators can weight this cell accordingly.
3. **Scope.** An 1813 mandatory-jurisdiction case appears to fall within the
   predict scope's pre-1925 exclusion policy, yet it was fanned out to this
   run. Flagged as `scope` for maintainer triage.
