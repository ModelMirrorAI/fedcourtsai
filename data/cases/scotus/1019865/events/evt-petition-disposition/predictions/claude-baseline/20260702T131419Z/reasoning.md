# Hennessy v. Sheldon — petition disposition (scotus/1019865)

## The question

Predict the disposition of the petition event for this Supreme Court case:
whether it will be granted (and if not, which disposition bucket it lands in).

## What the snapshot shows

The 2026-07-02 snapshot is a bare CourtListener docket. The only substantive
facts it carries are:

- Case name **Hennessy v. Sheldon**, court `scotus`.
- **One linked opinion cluster** — a published decision is associated with this
  docket.
- **No docket entries, no docket number, no filed/argued/terminated dates, and
  no cert-granted or cert-denied dates.** The CourtListener record was created
  in 2014 from a bulk import (`source: 0`) and last modified in 2016.

There is no petition text, no lower-court information, no party detail, and no
Term to anchor the case in time. Everything below is therefore driven by
corpus base rates for dockets that look exactly like this one, not by
case-specific merits analysis — the snapshot simply does not support one.

## Corpus context (base rates, not case facts)

`fedcourts stats --court scotus --resolved-only` over 296 resolved SCOTUS
cases in the corpus:

| Disposition | Share |
|-------------|-------|
| other       | 78.4% |
| dismissed   | 15.9% |
| denied      | 4.4%  |
| granted     | 1.4%  |

Grouping by SCOTUS Term shows 267 of the 296 resolved cases have **no
parseable Term** — the same shape as this docket (no docket number). That
bucket runs: other 76.4%, dismissed 17.6%, denied 4.5%, granted 1.5%.

`fedcourts query --court scotus` priors confirm the pattern: dockets of this
vintage in the corpus are opinion-derived records (a docket reconstructed from
a published opinion cluster), and when they resolve, the disposition label is
overwhelmingly `other` (a merits outcome such as affirmed/reversed that maps
to no petition-specific bucket) or occasionally `dismissed` (e.g. for want of
jurisdiction).

## Reasoning

1. **The docket is opinion-derived.** The single linked cluster with no docket
   entries is the signature of a historical SCOTUS record built from a
   published opinion. Cases in the corpus with this shape resolve to `other`
   about three-quarters of the time.
2. **"Granted" is rare in this corpus and unsupported here.** The corpus-wide
   grant share is ~1.4% (and ~1.5% in the no-Term bucket that matches this
   docket). Nothing in the snapshot — no CVSG, no distribution, no
   response-requested signal, indeed no docket entries at all — provides any
   lift over that base rate. A published opinion attached to the docket might
   in a modern cert-era case hint that review was granted, but the corpus's
   labeling of exactly such opinion-derived dockets shows they resolve to
   `other`, not `granted`, so I give that signal only a small upward nudge.
3. **`other` beats `denied` here.** For a modern cert petition, `denied`
   would be the default. But this record's shape (bulk-imported, opinion
   cluster attached, no cert-denied date despite the field existing) matches
   the historical merits-case population, where `other` dominates and `denied`
   is only ~4.5%.

## Prediction

- **predicted_disposition: `other`** — the modal outcome (~76%) for resolved
  SCOTUS dockets of this shape.
- **granted: 0, probability: 0.02** — essentially the corpus base rate
  (~1.4–1.5%) with a small nudge for the attached opinion cluster.
- **confidence: 0.4** — low-moderate: the base rates are well-grounded, but
  the snapshot carries almost no case-specific information, so the prediction
  is a calibrated prior rather than a case analysis.
- **No per-judge votes** — the snapshot names no panel and no Term, so any
  vote breakdown would be invented.

## Data-quality note

The snapshot's sparseness (no entries, no dates, no docket number) is flagged
in `flags.json`: the linked opinion cluster suggests the true disposition may
be recoverable upstream (the cluster-disposition path that
`probe-recoverability` classifies), which would also let this event resolve.
