# Prediction reasoning — scotus/1002339, evt-petition-disposition

## The legal question

Will the Supreme Court grant the petition for a writ of certiorari in
*Grant Investment Funds v. Internal Revenue Service*? The event's
`decision_target` is the petition's **disposition**; "granted" means certiorari
is granted (`granted = 1`).

## Governing standard

Review on certiorari is "not a matter of right, but of judicial discretion"
(Sup. Ct. R. 10). The Court grants a petition only for "compelling reasons" —
typically a genuine conflict among the courts of appeals, a conflict with the
Court's own precedent, or an important and unsettled question of federal law.
Rule 10 expressly cautions that a petition resting only on the misapplication of
a properly stated rule of law, or on an erroneous factual finding, is rarely
granted. Across all petitions the Court grants on the order of 1% of paid
petitions, and a far smaller fraction of *in forma pauperis* petitions.

## Facts from the snapshot that drive the outcome

Reasoning is based solely on the provisioned snapshot
(`data/cases/scotus/1002339/record/snapshots/2026-06-29.json`):

- **Posture is a routine civil cert petition.** The case is captioned
  *Grant Investment Funds v. Internal Revenue Service* — a private party against
  a federal agency in a tax matter. This is an ordinary category of petition with
  no inherent feature that draws a grant.
- **No distinguishing signal in the record.** The snapshot records no argument
  date (`date_argued` is null), no cert-granted or cert-denied date (both null),
  no termination date, and an empty `docket_entries` list. There is no docket
  number, no panel or judge assignment, and nothing indicating a circuit split, a
  call for the views of the Solicitor General, a relisting, or any other marker
  that characterizes the small set of granted petitions. There are no facts
  suggesting a "compelling reason" under Rule 10.
- **Sparse record overall.** The docket entry is thin (a single linked opinion
  cluster, no docket text), so the prediction necessarily leans on the
  category's base rate rather than case-specific grant signals.

## Probability and disposition

The base rate for this category — an ordinary civil cert petition with no
distinguishing feature — is overwhelmingly denial. I assign
**P(granted) = 0.02**, predicting **disposition = denied** (`granted = 0`). The
small non-zero probability reflects irreducible uncertainty rather than any
affirmative grant signal in the record. Confidence is moderate (0.7): the base
rate is well established and points firmly to denial, but the snapshot is sparse
enough that no case-specific facts either reinforce or cut against it.

## Votes

Certiorari is granted under the "rule of four," and the Court does not publish
individual Justices' votes on the cert pool. No panel or judge assignment is
present in the snapshot, so no per-judge votes are recorded.
