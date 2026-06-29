# Prediction reasoning — scotus/1003917, evt-petition-disposition

## The legal question

The event asks for the **disposition** of a petition (`kind: petition`,
`decision_target: disposition`) in *Michigan Pub. Util. Comm'n v. Duke*, a
Supreme Court of the United States matter. The outcome space is the standard
disposition enum (granted / denied / granted-in-part / dismissed / withdrawn /
other), with `granted` as the binary target and `probability` as P(granted). At
this posture "granted" means the Court took the case up for decision (review
granted / jurisdiction noted) rather than turning it away.

## What the snapshot tells me

I predict only from the provisioned snapshot
(`data/cases/scotus/1003917/record/snapshots/2026-06-29.json`). I did not fetch
new docket facts or look up the historical outcome — that outcome is exactly the
quantity under evaluation. The docket record itself is a thin metadata stub:

- `docket_entries: []` — no filings, no petition text, no order text.
- `date_argued`, `date_filed`, `date_cert_granted`, `date_cert_denied`,
  `date_terminated` are all `null`.
- No `nature_of_suit`, no `cause`, no question presented.

But two **structural** identifiers on the face of the snapshot carry real signal
and are not "new facts":

- **An opinion cluster is linked.** `clusters` contains
  `.../clusters/100552/`. A linked opinion cluster indicates the docket resolved
  into a **published, written opinion** — i.e., the Court reached and decided the
  matter, rather than disposing of it by a bare order. Bare cert/appeal refusals
  do not normally generate a substantive opinion cluster.
- **Old-style docket number `283`.** The docket number (`docket_number` and
  `docket_number_raw` are both `"283"`) is a short, pre-modern SCOTUS number, not
  the modern `YY-NNNNN` certiorari format. That places the case in the era of the
  Court's **mandatory appellate jurisdiction** (appeals / writs of error), when
  properly presented cases were far more likely to be decided on the merits than
  modern discretionary cert petitions.

## How I reach a probability

The modern base rate for a SCOTUS petition (a discretionary cert petition) is a
grant in roughly **1%** of cases. That prior does **not** govern here, because
the snapshot's own structural facts point the other way:

- A published opinion cluster strongly implies the Court **decided the case on
  the merits**, which means review was effectively granted / jurisdiction noted.
- The pre-modern docket number is consistent with the mandatory-appeal regime,
  where the Court disposed of properly presented cases on the merits.

I therefore depart from the cert base rate and predict **granted**
(`predicted_disposition = granted`, `granted = 1`), with `probability = 0.7`.

I hold the probability at 0.7 rather than higher because the chain has a genuine
weak link: a published opinion is also consistent with dispositions that are
**not** "granted" — most relevantly a **dismissal** (e.g., an appeal dismissed
for want of a substantial federal question) or a per curiam disposition that
still produces a citable cluster. The snapshot gives no merits facts to
distinguish these, so the precise probability rests on the structural inference
that an opinion cluster + pre-modern posture most often reflects a case the
Court took up and decided.

`confidence = 0.3` reflects that the directional call (the Court engaged and
decided this matter rather than summarily refusing it) is reasonably secure, but
the mapping of an old mandatory-appeal disposition onto the granted/denied/
dismissed enum carries interpretive uncertainty, and the snapshot supplies no
case-specific merits signal. I report no per-judge `votes`: the snapshot
identifies no panel, and historical dispositions of this kind are not recorded
as individual Justice votes in this record.
