# Prediction reasoning — scotus/1001512 / evt-petition-disposition

## The legal question

Will the Supreme Court of the United States grant the petition in *Blackledge v.
Allison* (docket No. 75-1693)? The event's `kind` is `petition` and its
`decision_target` is the **disposition** of that petition. For a SCOTUS filing of
this posture — a petition for a writ of certiorari — "granted" means the Court
agrees to review the case; the overwhelmingly common alternative is denial of
review.

## Governing standard

Certiorari is discretionary. Under Supreme Court Rule 10, review "is not a matter
of right, but of judicial discretion," and is granted "only for compelling
reasons" — typically a genuine split among lower courts or an important unsettled
question of federal law. Four Justices must vote to grant (the "rule of four").
The empirical base rate is the dominant prior for an undistinguished petition: the
Court grants only a low-single-digit percentage of petitions. A prediction should
therefore start near denial and move off that prior only when the record contains
a concrete signal that review was taken.

## Facts from the snapshot that drive the outcome

From `record/snapshots/2026-06-29.json`:

- **Court:** `scotus` — Supreme Court of the United States.
- **Caption:** *Blackledge v. Allison*; `docket_number` `75-1693`.
- **Disposition date fields are null:** `date_cert_granted`, `date_cert_denied`,
  `date_argued`, and `date_terminated` are all `null`; `docket_entries` is empty;
  the event is `resolved: false`. Taken alone these would leave only the base-rate
  prior.
- **A merits opinion cluster is linked:** the `clusters` field contains exactly
  one entry, an opinion cluster on this SCOTUS docket
  (`/api/rest/v4/clusters/109648/`). This is the decisive snapshot fact. The
  Supreme Court issues a published opinion cluster only for cases it has taken up
  and decided on the merits. A docket that proceeds to a SCOTUS merits opinion is
  one in which review was granted; bare denials of certiorari do not generate a
  merits opinion cluster of this kind.

The presence of a linked merits opinion on a SCOTUS docket is strong
snapshot-internal evidence that the threshold petition was granted and the case
moved into the Court's merits docket, notwithstanding the sparse, historical (the
docket dates to the 1975 Term) docket record that leaves the date fields empty.

I reason only from the provisioned snapshot. I did **not** fetch the linked
cluster or any other external docket fact about this case, and I do not rely on
outside recollection of the case's ultimate holding; the inference rests on the
fact, present in the snapshot itself, that an opinion cluster is attached to the
docket.

## Probability and disposition

The base-rate prior (deny) is overridden here by the linked merits opinion
cluster, which signals the Court took the case.

- `predicted_disposition`: **granted**
- `granted`: **1**
- `probability` (P(granted)): **0.85** — well onto the "granted" side, with the
  remaining mass reserving for the chance that the cluster reflects something
  other than a cert grant (e.g., an opinion respecting a denial, or a posture I
  cannot confirm without fetching the cluster, which the contract forbids).
- `confidence`: **0.8** — moderately high; the cluster is a strong but indirect
  signal, and the date fields that would corroborate a grant are null in this
  sparse historical record.

## Votes

SCOTUS orders disposing of certiorari petitions ordinarily issue without recorded
per-Justice votes (a grant requires four, but the action is reported as a Court
action, not an individual tally). I therefore record no per-judge votes; `votes`
is empty rather than speculative.

## Limitations

Predicted strictly from the provisioned snapshot, per the contract. The snapshot's
explicit disposition fields are null, so the prediction turns on the inferential
weight of the linked opinion cluster rather than on a directly recorded grant
date. I did not fetch new docket facts.
