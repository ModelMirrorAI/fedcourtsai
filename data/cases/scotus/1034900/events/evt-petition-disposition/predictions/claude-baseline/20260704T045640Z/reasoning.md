# Minor v. Tillotson — evt-petition-disposition

**Prediction: not granted (granted = 0), P(granted) = 0.03, predicted disposition
`other`, confidence 0.65.**

## What the snapshot contains

The 2026-07-04 snapshot is a sparse historical CourtListener docket (bulk-import
source, no PACER lineage): case name *Minor v. Tillotson*, court `scotus`, one
associated opinion cluster, and **no docket entries, no filing/argument/decision
dates, no docket number, and no petition documents**. There are no cert dates
(`date_cert_granted` and `date_cert_denied` are both null) and no
originating-court information. The only case-specific facts available from the
snapshot are the caption, the court, and the existence of a decided opinion
cluster.

## What the case is

The caption and docket shape identify this as the historical litigation *Minor
v. Tillotson* — a land-title dispute out of Louisiana that reached the Supreme
Court more than once in the Marshall/Taney era on **writ of error** (reported at
32 U.S. (7 Pet.) 99 (1833), where the Court addressed the best-evidence rule
governing secondary proof of title documents, and again in the 1840s at 43 U.S.
(2 How.) 392). This identification is background legal knowledge (the kind of
precedent context the contract permits), not a new docket fetch. The snapshot
does not say which of the case's appearances this docket's single opinion
cluster corresponds to, and I have not fetched the cluster to find out, so I
treat the specific merits outcome as uncertain and lean on the structural point
below, which holds for every appearance of the case.

## Legal question and governing standard

Whatever the merits question (the 1833 appearance turned on whether secondary
evidence of title papers was properly admitted; the later appearance on the
sufficiency of the competing Louisiana land titles), the dispositive point for
*this event* is procedural: the case predates the certiorari system created by
the Judiciary Act of 1891 and expanded in 1925. It arrived as of right on writ
of error — there was no petition for certiorari to grant or deny. A
"petition-disposition" event over such a docket can only reconcile to whatever
label the pipeline assigns historical merits dispositions (affirmed/reversed),
none of which is `granted` in the cert sense.

## Mapping to the event's disposition labels

The event asks for a disposition from the enum
granted/denied/granted-in-part/dismissed/withdrawn/other. Corpus base rates
(`fedcourts stats --court scotus`, 296 resolved events) show how the pipeline
actually labels these historical events: **`other` 78.4%, `dismissed` 15.9%,
`denied` 4.4%, `granted` 1.4%**. A writ-of-error merits case resolved by
affirmance or reversal fits none of the grant/deny labels directly and, by the
corpus's realized labeling, most likely reconciles to `other`.

## Calibration

- `granted = 0`, `probability = 0.03`: the corpus-wide grant share for resolved
  SCOTUS events is 1.4%, and the structural analysis (no cert petition existed
  to be granted) pushes the same way; the residual 3% covers the chance that I
  have misidentified the docket or that the reconciler maps a reversal in the
  petitioner's favor to `granted`.
- `predicted_disposition = other` rather than `denied` or `dismissed`: driven
  by the pipeline's realized labeling (78% `other`) plus the fact that nothing
  in the snapshot suggests a jurisdictional dismissal. Because I am unsure
  which appearance of the case this docket represents, and because the label
  choice is mostly a mapping question rather than a legal one, confidence is
  0.65 — slightly below the analogous prior run where the merits outcome was
  known with certainty.
- **No per-judge votes.** The snapshot names no panel, and predicting seriatim
  or per-Justice votes for an 1830s–1840s case from a bare caption would be
  invention.

## Data-quality note

This prediction rests almost entirely on recognizing the caption as a
pre-certiorari historical case plus corpus base rates; a predictor without
background knowledge of the case could only emit the raw base rate. Recorded
durably in `flags.json` (data-quality warning, ambiguous-event info).
