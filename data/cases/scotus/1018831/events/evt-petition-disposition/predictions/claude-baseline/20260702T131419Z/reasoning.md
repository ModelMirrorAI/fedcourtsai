# Dollar Savings Bank v. United States — petition disposition

**Prediction: disposition `other`, P(granted) = 0.02, confidence 0.6.**

## What the snapshot shows

The snapshot (`data/cases/scotus/1018831/record/snapshots/2026-07-02.json`) is a
bare historical docket stub:

- Case name: *Dollar Savings Bank v. United States*, court `scotus`.
- **No docket entries, no docket number, no filed/argued/terminated dates**, and
  the cert fields (`date_cert_granted`, `date_cert_denied`) are null.
- One linked opinion cluster (`clusters/88877`), and `source: 16` with a 2014
  `date_created` — the signature of a docket stub generated from a bulk-loaded
  opinion rather than a live docket being tracked toward a cert decision.

The single most informative fact in the snapshot is the linked opinion cluster:
CourtListener holds a decision document for this docket, which means the case
almost certainly resolved on the merits long ago rather than sitting as a
pending petition awaiting a grant/deny call.

## Legal context (not case facts)

The case name matches the reported decision *Dollar Savings Bank v. United
States*, 86 U.S. (19 Wall.) 227 (1874) — a pre-1925 case that reached the Court
on **mandatory jurisdiction** (writ of error), not on a discretionary
certiorari petition. Before the Judiciary Act of 1925 there was no cert-style
"granted/denied" gate for such cases: the Court took the case as of right and
disposed of it on the merits (affirm/reverse). A merits disposition does not map
to `granted` or `denied` in this event's disposition vocabulary; it maps to
`other`.

## Corpus priors and base rates

- `fedcourts stats --court scotus --group-by disposition`: among the 296
  resolved SCOTUS cases in the corpus, dispositions are **`other` 78.4%**,
  `dismissed` 15.9%, `denied` 4.4%, **`granted` 1.4%**. The resolved subset is
  dominated by exactly this kind of bulk-seeded historical case, so it is the
  most relevant base rate available.
- `fedcourts query --court scotus`: the nearest resolved priors are other
  19th-century appeal/writ-of-error dockets with linked opinions, and they
  reconcile to disposition `other` (e.g. `scotus/1004844`, an appeal resolved on
  a motion to affirm, disposition `other` and marked `predict_excluded`).

## Why these numbers

- **`predicted_disposition: other`** — the linked opinion cluster plus the
  mandatory-jurisdiction era mean the realistic resolution is a merits
  disposition, which this pipeline's reconciliation maps to `other` (as the
  resolved priors show). The 78% base rate for `other` among resolved SCOTUS
  corpus cases points the same way; the case-specific evidence pushes it higher.
- **`probability` (P(granted)) = 0.02** — a `granted` disposition here would
  require the reconciler to read the historical record as a cert-style grant.
  Nothing in the snapshot supports that (no cert dates), and the base rate for
  `granted` among resolved corpus cases is 1.4%. I set it slightly above base
  to allow for reconciliation-mapping uncertainty on a bare record.
- **`granted: 0`** follows directly.
- **`confidence: 0.6`** — moderate: the snapshot is nearly empty, so the call
  rests on the cluster link, era, and base rates rather than record facts; but
  those three all point the same direction.
- **No per-justice votes** — the snapshot names no panel, and predicting a
  named 1874 bench from an empty record would be invention.

## Flags

See `flags.json`: this looks like a pre-1925 mandatory-jurisdiction case that
the predict-scope exclusion did not catch — most likely because the docket row
has an empty docket number, so no Term/era could be parsed — plus a
data-quality note on the bare snapshot.
