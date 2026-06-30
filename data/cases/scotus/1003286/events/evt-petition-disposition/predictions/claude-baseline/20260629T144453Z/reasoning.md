# Prediction reasoning — scotus/1003286, evt-petition-disposition

## The legal question

The event (`kind: petition`, `decision_target: disposition`) asks how the
Supreme Court disposed of the petition for a writ of certiorari in *Alejandra
Tapia v. United States* (docket 10-5400), an appeal from the Ninth Circuit.
At the cert stage the disposition is binary: the petition is either **granted**
(the Court agrees to hear the case) or **denied**.

## Governing standard

Certiorari is discretionary (Supreme Court Rule 10). The overwhelming base rate
is denial — the Court grants only a small fraction of paid and IFP petitions.
But that base rate is not the relevant evidence here, because the snapshot
itself records the downstream procedural history of the case, which resolves the
question directly rather than probabilistically.

## Facts from the snapshot that drive the outcome

Predicting only from `record/snapshots/2026-06-29.json`:

- **`date_argued`: `2011-04-18`.** The case was set for and held oral argument.
- **`audio_files`** contains an oral-argument audio recording
  (`/api/rest/v4/audio/89535/`).
- **`clusters`** contains an opinion cluster (`/api/rest/v4/clusters/218921/`),
  indicating a merits opinion issued in the case.
- `appeal_from_str`: "United States Court of Appeals for the Ninth Circuit"
  and `original_court_info` confirm the posture as a petition seeking review of
  a Ninth Circuit judgment.

The Supreme Court calendars oral argument and issues signed merits opinions
**only in cases where certiorari has already been granted.** A petition that is
denied never reaches argument and produces no opinion cluster. The presence of
both an argument date and an opinion cluster in the snapshot is therefore
conclusive that the cert petition was **granted**.

## Note on the empty cert-date fields

`date_cert_granted` and `date_cert_denied` are both `null`. These CourtListener
fields are frequently unpopulated even for cases that plainly went to argument,
so their absence is not probative. The argument date and opinion cluster are the
controlling evidence and both point unambiguously to a grant.

## Probability and disposition

- **`predicted_disposition`: granted**, **`granted`: 1**.
- **`probability` (P(granted)): 0.97.** The snapshot evidence is essentially
  dispositive; the small residual reflects only the possibility of data-entry
  artifacts in the upstream record (e.g., an argument/cluster mis-association).
- **`confidence`: 0.95**, for the same reason.

No per-judge votes are predicted: the event targets the petition disposition (a
court-level grant of certiorari), not a merits vote split, so `votes` is empty.
