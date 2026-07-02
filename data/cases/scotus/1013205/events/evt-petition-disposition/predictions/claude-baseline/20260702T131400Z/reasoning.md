# Walden v. The Heirs of Gratz — evt-petition-disposition

## The event and what the snapshot actually contains

The event asks for the disposition of a SCOTUS "petition". The snapshot
(`data/cases/scotus/1013205/record/snapshots/2026-07-01.json`) is extremely
sparse: no docket entries, no docket number, no filed/argued/terminated dates,
no cert-granted/cert-denied dates, no parties or attorneys. The load-bearing
facts it does contain are:

- **Caption:** *Walden v. The Heirs of Gratz* — an archaic party caption in the
  style of the early-1800s Marshall Court reporters, not a modern cert-stage
  caption.
- **A linked opinion cluster** (`clusters` contains one entry, cluster id
  85157). A very low CourtListener cluster id together with the archaic caption
  marks this as a historical merits decision that was scraped from the old
  reporter volumes, not a pending petition.
- No `date_cert_granted` / `date_cert_denied`, consistent with a case that
  predates the certiorari system entirely.

## The legal frame

This case comes from the era of **mandatory appellate jurisdiction**. Before
the Judiciary Act of 1891 (and fully until the Judiciary Act of 1925), cases in
this posture reached the Supreme Court by writ of error or appeal as of right —
there was no discretionary "grant/deny" gate to predict. A case with a merits
opinion cluster attached was necessarily heard and decided on the merits:
the realistic outcome space is *affirmed / reversed / dismissed (e.g. for want
of jurisdiction)*, not *granted / denied*.

In this pipeline's `Disposition` enum, a merits affirmance or reversal has no
dedicated label; the ingestion normalizer maps such free-text dispositions to
**`other`** (and `granted` is reserved for actual grants of the predicted
relief). So the question "how will this event resolve?" is really "what label
will the resolved outcome carry?", and for a decided historical merits case
that label is almost always `other`.

## Base rates (corpus)

`fedcourts stats --court scotus --resolved-only --group-by disposition` over
the pulled corpus (296 resolved SCOTUS cases, dominated by exactly this kind of
historical docket):

| disposition | share |
|---|---|
| other | 78.4% |
| dismissed | 15.9% |
| denied | 4.4% |
| granted | 1.4% |

`fedcourts query --court scotus` confirms the nearest priors are the same
species — sparse historical dockets with an opinion cluster, resolved as
`other`.

## Prediction

- **predicted_disposition: `other`** — the case was heard under mandatory
  jurisdiction and decided on the merits; affirm/reverse outcomes normalize to
  `other`.
- **probability (P(granted)): 0.03** — anchored on the ~1.4% corpus base rate
  for `granted`, nudged up slightly for the residual chance that a reconciler
  labels a heard-and-decided writ of error as "review granted".
- **granted: 0**.
- **confidence: 0.6** — the direction (not granted, merits-era case) is high
  confidence; the residual mass sits mostly on `dismissed` (~15% base rate,
  e.g. dismissal for want of jurisdiction), which keeps confidence in the
  disposition label itself moderate.
- **votes:** none predicted. The snapshot names no panel, and per-seat votes
  for an early-1800s bench would be pure invention.

## Caveats

This event is arguably out of predict scope (pre-1925 mandatory jurisdiction);
it likely reached the predict matrix because the snapshot carries no dates and
no docket number for the scope predicates to match on. Flagged in `flags.json`
(categories `scope` and `data-quality`) so it reaches the run PR roll-up.
