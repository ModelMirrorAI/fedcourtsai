# Prediction reasoning — scotus/1004147, evt-petition-disposition

## The legal question

The event asks for the **disposition** of a petition (`kind: petition`,
`decision_target: disposition`) in *Chemical Manufacturers Assn. v. NRDC*, a
Supreme Court of the United States matter. The outcome space is the standard
disposition enum (granted / denied / granted-in-part / dismissed / withdrawn /
other), with `granted` as the binary target and `probability` as P(granted).
For a SCOTUS matter at this posture the petition is a petition for a writ of
certiorari, so "granted" means cert granted.

## What the snapshot tells me

I predict only from the provisioned snapshot
(`data/cases/scotus/1004147/record/snapshots/2026-06-29.json`). I did not fetch
new docket facts or look up the historical merits outcome. The snapshot is a
thin metadata record:

- `docket_entries: []` — no filings, petition text, or order text.
- `date_argued`, `date_filed`, `date_cert_granted`, `date_cert_denied`,
  `date_terminated` are all `null` — no disposition date recorded *in this
  snapshot*.
- No `nature_of_suit`, `cause`, question presented, or merits briefing.

Despite the thin record, two **structural** identifiers on the face of the
snapshot carry real signal — these are properties of the snapshot itself, not
externally fetched facts:

- **An opinion cluster is attached.** `clusters` is non-empty
  (`.../clusters/111358/`). On CourtListener a docket gains an opinion cluster
  when the Court issued an opinion in the matter. For a certiorari posture, an
  attached merits opinion cluster is strong evidence the Court took the case —
  i.e., the cert petition was *granted* and the case was decided on the merits.
  Petitions that are simply denied do not normally acquire a merits opinion
  cluster.
- **Paid docket number `83-1013`.** SCOTUS docket numbers above ~5000 within a
  Term are the in forma pauperis ("pauper") docket; numbers below that are the
  paid docket. `1013` places this on the **paid** docket for October Term 1983.
  Paid petitions are granted at a materially higher rate than IFP petitions
  (which dominate the denial-heavy base rate), and the party caption — an
  industry association versus NRDC — fits the profile of a counseled,
  merits-bearing dispute rather than a pro se filing.

## How I reach a probability

The unconditional base rate for cert grants is very low (a few percent), and a
bare metadata stub alone would push me toward a confident *denied* call, as for
the IFP stubs in this corpus. But here the dominant signal cuts the other way:
the snapshot already carries an attached opinion cluster. That is the single
most informative structural fact available, and it is most consistent with a
matter the Court accepted and decided — i.e., cert granted.

I therefore predict **granted**, with `probability = 0.90`. I hold back from a
near-certain value because (a) the snapshot records no explicit
`date_cert_granted`, and (b) an opinion cluster can in rare cases attach to a
summary disposition or a related opinion rather than a clean grant-and-decide,
so a small mass of residual uncertainty is appropriate. `confidence = 0.7`
reflects that the call rests on a structural inference from a thin record rather
than on an explicit disposition field.

This event is a single-petition disposition, so no per-judge votes are recorded.
