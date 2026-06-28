# Prediction reasoning — scotus/1000513, evt-petition-disposition

## The legal question

The event is a `petition`-kind event with `decision_target: disposition` for
*Mercantile Bank v. New York* (CourtListener docket 1000513, docket number
"1258"). I am asked to predict the disposition of the petition for review —
i.e. whether the Supreme Court grants review / decides the case on the merits
(`granted`) or declines it (`denied`).

## Governing standard

For modern Supreme Court certiorari practice the operative standard is Supreme
Court Rule 10: review is discretionary and granted only for compelling reasons
(a genuine circuit split, an important unsettled federal question, or a decision
in conflict with the Court's precedent). The unconditioned base rate is heavily
toward denial: the Court grants only on the order of 1–2% of paid cert
petitions. Absent case-specific signals (a noted circuit conflict, a CVSG, an
amicus pile-up), the base-rate prior alone points to `denied`.

## What the snapshot actually contains

I predicted **only** from the provisioned snapshot
(`data/cases/scotus/1000513/record/snapshots/2026-06-28.json`). That snapshot is
unusually thin: `docket_entries` is empty, and every dispositive date field
(`date_argued`, `date_cert_granted`, `date_cert_denied`, `date_terminated`,
`date_filed`) is null. There is no question presented, no lower-court posture, no
briefing, and no party/amicus information. On the face of it there is almost no
case-specific merits signal to override the base-rate prior.

The one materially informative fact in the snapshot is that the docket is linked
to an opinion **cluster** (`clusters: [".../clusters/91904/"]`). I did not and
must not follow that link to fetch the opinion's contents (that would be pulling
a new case fact), but the mere existence of a linked opinion cluster is itself a
snapshot fact and is informative: in CourtListener, a SCOTUS docket carries an
opinion cluster when the Court issued a published opinion. Bare orders-list cert
denials generally do **not** produce an opinion cluster, whereas cases decided on
the merits do. The docket also has the hallmarks of an old, fully-adjudicated
case rather than a live petition awaiting action: a low sequential docket number
("1258"), a bulk-import provenance (`source: 16`, `date_created` 2014 from
historical data), and no modern docket activity. For a case of this vintage,
review was typically had on the merits (much of the 19th-century docket reached
the Court by writ of error/appeal as of right, before discretionary certiorari
was generalized by the Judiciary Act of 1925), so a linked merits opinion is a
strong indicator that the petition/appeal was entertained rather than refused.

## Reconciling the signals → probability

Two forces pull in opposite directions:

- The generic cert base rate pulls hard toward `denied` (probability of grant
  ~0.02).
- The linked opinion cluster plus the old, decided-case posture pull toward the
  case having been decided on the merits (`granted`).

The cluster signal is specific to this docket and, for a case of this kind,
substantially outweighs the generic denial prior — a published merits opinion is
much more consistent with review having been granted/had than with a bare
denial. I therefore predict **granted**, with `probability` (P(granted)) = 0.60.
I keep this well short of certainty because (a) the snapshot gives me no merits
detail, (b) some denials with separate statements also generate clusters, and
(c) I cannot inspect the cluster's contents. `confidence` is set low (0.35) to
reflect that the prediction rests on a single inferential snapshot fact rather
than a full record.

## Votes

I omit per-judge `votes`: the snapshot identifies no panel/justices and gives no
basis for individual vote predictions, so reporting votes would be fabrication.

## Data-quality note

This snapshot is degenerate for prediction purposes — zero docket entries and no
dispositive dates — so the prediction leans almost entirely on the base rate and
the single cluster-existence signal. I have left a brief note on the triggering
issue (#190) flagging the thin input. I was not blocked (the event is
well-formed and a snapshot exists), so I proceeded to the most defensible call
rather than stalling.
