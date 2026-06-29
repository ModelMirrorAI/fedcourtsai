# Prediction reasoning — scotus/1001361, evt-petition-disposition

## The legal question

What is the disposition of the petition in *King County v. Seattle School
District No. 1* (Sup. Ct. Docket No. 30)? The event's `decision_target` is the
petition's **disposition**; "granted" means the Court took up the petition for
review (as opposed to denying review).

## Governing standard

Supreme Court review is discretionary: certiorari is "not a matter of right, but
of judicial discretion" (Sup. Ct. R. 10), and the Court grants only on
"compelling reasons" such as a circuit split or an important unsettled federal
question. Across modern petitions the grant rate is roughly 1%, so the default
prior for a bare "petition disposition" event is overwhelmingly **denied**. That
prior, however, is calibrated to the modern, Term-sequenced cert docket; it must
be displaced when the snapshot itself carries a feature that distinguishes the
case from a routine denial.

## Facts from the snapshot that drive the outcome

Reasoning is based solely on the provisioned snapshot
(`data/cases/scotus/1001361/record/snapshots/2026-06-29.json`). The snapshot is a
sparse docket stub, but three features matter:

- **An opinion cluster is attached.** The docket links one opinion cluster
  (`clusters: [".../clusters/1443879/"]`). On the Supreme Court docket, a linked
  opinion cluster indicates the Court produced an opinion — i.e., the case was
  taken up and decided on the merits. Petitions that are simply *denied* do not
  generate a standalone opinion cluster (they appear only in order lists). This
  is the single strongest signal in the record and it points toward review having
  been granted, not denied. (Per the data contract I did **not** fetch the
  cluster itself, which would be retrieving new case facts; I rely only on the
  fact, present in the snapshot, that a cluster exists.)
- **A very low, non-Term-sequenced docket number.** `docket_number` is `30` — a
  single- /double-digit number characteristic of an old merits docket, not the
  four-/five-digit Term-sequenced numbering of modern cert (and IFP) petitions
  that drive the ~1% grant base rate. This reinforces that the base rate for
  routine modern cert denials is the wrong reference class here.
- **All case-specific dates are null; `date_created` is an import artifact.** No
  `date_argued`, `date_filed`, `date_cert_granted`, `date_cert_denied`, or
  `date_terminated`, and `docket_entries` is empty. The `date_created`
  (2014) and `date_modified` (2016) are CourtListener ingestion timestamps, not
  case events. So there are no procedural facts that would let me confirm the
  merits posture beyond the cluster link itself — hence real residual
  uncertainty.

## Probability and disposition

The bare-petition prior favors denial, but the attached opinion cluster is a
specific, on-snapshot signal that this petition led to a merits decision —
meaning review was effectively **granted**. Weighing that signal (strong but not
conclusive, given how little else the stub records) against the residual chance
that the cluster reflects something other than a grant, I assign
**P(granted) = 0.68** and predict **disposition = granted** (`granted = 1`).
Confidence is moderate (0.5): the direction is driven by one robust structural
signal, but the snapshot is otherwise almost empty, so I avoid a high-confidence
call.

## Votes

The Court does not publish individual Justices' votes on whether to grant review,
and the snapshot records no panel or judge assignment (`panel` is empty,
`assigned_to` is null). No per-judge votes are recorded.
