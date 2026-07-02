# United States v. Fremont (scotus/1016970) — evt-petition-disposition

## What the event asks

`evt-petition-disposition` (kind `petition`, target `disposition`): predict the
disposition of the petition in this Supreme Court docket, as a binary
granted/not-granted plus a disposition label.

## What the snapshot shows

The 2026-07-02 snapshot is extremely thin. It contains:

- Case name **"United States v. Fremont"**, court `scotus`.
- **One opinion cluster** attached to the docket (CourtListener cluster 86967),
  meaning the Court issued at least one opinion in this case.
- **No docket entries, no docket number, no filing/argument/termination dates,
  no cert-granted or cert-denied dates, no panel, no parties beyond the
  caption.** The record was created in CourtListener in 2014 from a bulk
  import (`source: 16`).

There are no case facts to reason from beyond the caption and the existence of
a decided opinion.

## Characterizing the case

Two snapshot signals place this docket in the historical (pre–certiorari-era)
part of the SCOTUS corpus rather than the modern cert docket:

1. The very low opinion-cluster id (86967) sits in CourtListener's historical
   SCOTUS reporter import range.
2. The docket has none of the modern cert-lifecycle fields populated
   (`date_cert_granted` / `date_cert_denied` are null and there are no docket
   entries at all), yet an opinion exists — the shape of a 19th-century merits
   appeal, not a modern petition.

The caption is consistent with the well-known Taney-era land-grant litigation
over John C. Frémont's California (Las Mariposas) claim, decided in the 1850s,
in which the Court upheld the confirmation of the claim against the United
States. I note this identification as legal-context background only and with
explicit uncertainty — the snapshot itself gives no date or citation — so I do
not lean on the specific historical outcome; but every reading of the snapshot
points the same direction: this is a decided historical merits appeal, not a
petition that will be "granted" in the modern cert sense.

## Base rates from the corpus

`fedcourts stats --court scotus`: 296 resolved SCOTUS events in the corpus —
**other 78.4%, dismissed 15.9%, denied 4.4%, granted 1.4%**. Grouped by Term
year, virtually all resolved SCOTUS events have no Term (undated historical
cases), matching this docket's shape. Sampled priors labeled `other`
(`fedcourts query --court scotus --disposition other`) are exactly this kind of
record: historical appeals and writs of error resolved on the merits
(affirmances/reversals), for which none of the granted/denied labels fit.

## Prediction and calibration

- **granted = 0, probability = 0.03.** The corpus-wide granted share for
  resolved SCOTUS events is ~1.4%; nothing in this snapshot pulls upward from
  that anchor, and the historical-merits shape pulls the "granted" reading
  further down. I set 0.03 rather than the raw 1.4% to reflect the small
  resolved sample (n=296) and my uncertainty about how the label was assigned
  for this docket.
- **predicted_disposition = "other".** A historical merits appeal resolved by
  opinion is overwhelmingly labeled `other` in this corpus (78% of resolved
  SCOTUS events), since an affirmance/reversal maps to none of
  granted/denied/dismissed. `dismissed` is the runner-up (~16%) but there is no
  jurisdictional-defect signal in the snapshot.
- **confidence = 0.35**, low, because the snapshot carries almost no
  information: the prediction rests on corpus base rates and on structural
  inferences about the docket's era, not on case facts.
- **No per-judge votes**: the snapshot has no panel information, and guessing a
  19th-century bench composition would be speculation.

Data-quality and event-scope concerns are recorded in `flags.json` alongside
this file.
