# No. 90-1397 — evt-petition-disposition

**Prediction: not granted (granted = 0), P(granted) = 0.03, predicted disposition
`other`, confidence 0.55.**

## What the snapshot contains

The 2026-07-04 snapshot is one of CourtListener's sparse historical SCOTUS
dockets, created in 2014 from opinion data rather than from a live docket feed.
It carries almost nothing: the caption is just the docket number ("No.
90-1397"), and there are **no parties, no docket entries, no filing / argument /
decision / cert dates, and no docket-number field** (the number appears only in
the case name and slug). The one substantive fact is a link to a single
associated opinion cluster — the docket exists in CourtListener *because* a
decided opinion exists for it.

## What can be inferred

The "90-" prefix identifies this as an October Term 1990 petition, i.e. a
certiorari-era filing (post-1988 Judiciary Act, essentially fully discretionary
docket). I cannot identify the underlying case from the number alone, and the
snapshot offers no caption or parties to anchor an identification, so — unlike
sparse dockets with a recognizable caption — no background legal knowledge can
be brought to bear. This prediction is therefore driven by the corpus's realized
labeling of structurally identical cases, plus one structural fact: the linked
opinion cluster means the matter produced a published decision rather than
sitting unresolved.

## The legal question and the base rates

For a petition-disposition event the notional question is whether the Court
granted review. In the abstract, the OT-1990 cert grant rate was a few percent.
But the prediction target here is the disposition label the pipeline's
reconciler will assign, and the corpus shows how it labels exactly this shape of
case:

- Across all 296 resolved SCOTUS petition events: **`other` 78.4%, `dismissed`
  15.9%, `denied` 4.4%, `granted` 1.4%** (`fedcourts stats --court scotus
  --resolved-only`).
- Restricted to cases with a parseable modern Term year (1976–2003, all likewise
  cluster-backed CourtListener dockets): **25 of 26 resolved to `other`, 1 to
  `denied`, 0 to `granted`**.

Cluster-backed dockets like this one resolve on a published decision whose
disposition text (affirmed / reversed / vacated, or a memorandum disposition),
and the reconciler maps those overwhelmingly to `other` — even where certiorari
was in fact granted along the way. So `other` is the modal and clearly best
call, and `granted` as a *label* is rare even conditional on a merits opinion
existing.

## Calibration

- `probability = 0.03`: the corpus-wide grant share is 1.4% and the
  modern-Term slice shows 0/26 granted; I set the probability slightly above
  the raw base rate because the presence of a published cluster for a
  discretionary-docket case is weak evidence that review was actually granted,
  and there is residual uncertainty in how the reconciler will map this
  particular cluster's disposition.
- `predicted_disposition = other`: the pipeline's empirical labeling of
  cluster-backed historical SCOTUS dockets, not legal doubt, drives this.
- `confidence = 0.55`: lower than for sparse dockets with an identifiable
  caption — here the case itself is unidentified, so the prediction rests
  entirely on structural base rates.
- **No per-judge votes**: with the underlying case unidentified, any vote
  lineup would be a guess; I omit `votes`.

## Data-quality note

The snapshot supports no case-specific reasoning at all — no caption, parties,
dates, or entries. Without the corpus base rates this cell could produce nothing
better than an uninformed prior. See `flags.json`.
