# Prediction Reasoning

## Event

The event asks for the disposition of a petition in `scotus/103746`, titled `Hopt v. Territory of Utah`.

## Snapshot Facts Used

I used `data/cases/scotus/103746/record/snapshots/2026-07-04.json`.

The snapshot is sparse. It identifies the court as SCOTUS, docket id `103746`, slug `hopt-v-territory-of-utah`, case name `Hopt v. Territory of Utah`, and one linked opinion cluster. It contains no docket entries, docket number, filed date, last filing date, termination date, cert grant date, cert denial date, panel, parties, originating court, or tags.

## Governing Standard

For a petition-disposition event, the ordinary grant question is whether the Supreme Court grants discretionary review. The Court grants only a small fraction of petitions, generally where the matter presents a sufficiently important recurring federal question, a conflict, or another strong reason for review. Sparse historical records are different: the absence of cert-specific fields and docket entries makes it hard to classify the proceeding as a modern cert petition at all.

## Corpus Calibration

I checked corpus priors for SCOTUS resolved events. In the matched resolved SCOTUS set, dispositions were mostly `other` (232 of 296, 78.4%), with `dismissed` at 15.9%, `denied` at 4.4%, and `granted` at 1.4%. A quick SCOTUS prior query also showed many historical rows with sparse metadata and `other` dispositions.

## Assessment

The linked opinion cluster makes it plausible that this historical matter reached a merits or appellate disposition, but the event record and snapshot do not show a petition, a cert grant, a cert denial, or any docket-entry-level disposition. For this kind of sparse historical SCOTUS record, the corpus base rate strongly favors `other` over a clean grant/deny petition outcome.

I therefore predict `other`, with a low probability that the petition will be classified as granted. I set `P(granted) = 0.03`: above the raw 1.4% SCOTUS resolved grant base rate because the snapshot has a linked opinion cluster, but still low because there is no grant-specific metadata and the dominant historical-disposition bucket is `other`.

No votes are predicted. The snapshot provides no panel, and petition-stage votes are not disclosed in the ordinary way.
