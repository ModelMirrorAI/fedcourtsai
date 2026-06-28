# Prediction reasoning — scotus/1000525, evt-petition-disposition

## The legal question

The event asks for the **disposition of a petition** before the Supreme Court of
the United States in *Smyth v. Strader, Pevine, & Co.* (docket 1000525). The
decision target is the petition's disposition: granted, denied, dismissed, or
otherwise resolved.

## Governing standard

For a discretionary petition to the Supreme Court (a petition for a writ of
certiorari), review is granted only for "compelling reasons" (Sup. Ct. R. 10):
a circuit split, an important unsettled federal question, or a lower-court
departure from this Court's precedent. The empirical base rate is heavily
skewed toward denial — the Court grants only on the order of ~1% of paid
certiorari petitions in the modern era. Petitions can also be **dismissed**
(e.g., for want of jurisdiction or as improvidently granted) rather than decided
on the merits.

## Facts available from the snapshot

This is the binding constraint on the prediction. The latest snapshot
(`record/snapshots/2026-06-28.json`) is almost entirely empty for predictive
purposes:

- `docket_entries`: empty — no motions, briefs, orders, or scheduling.
- No dates: `date_filed`, `date_argued`, `date_cert_granted`,
  `date_cert_denied`, `date_terminated` are all null.
- No `nature_of_suit`, `cause`, `jurisdiction_type`, or
  `appellate_case_type_information`.
- `panel` and `assigned_to` are empty — no judge identities, so no per-judge
  votes can be predicted.
- The one substantive signal is a linked opinion `clusters` reference, which
  indicates a reported decision exists for the underlying matter. The snapshot
  does **not**, however, expose the *content* or *direction* of that
  disposition, and I may not fetch new case facts to resolve it.

In short, the snapshot carries essentially none of the substantive features
(questions presented, the lower-court posture, briefing, a circuit split) that
would move a petition-disposition prediction off the base rate.

## Reasoning behind the probability

With no cert-worthiness signal in the snapshot, the most defensible estimate is
the prior for petition grants, which is strongly tilted toward non-grant. I set
**P(granted) = 0.10** — slightly above the raw modern grant rate to (a) hedge
for the historical/sparse nature of this record and (b) acknowledge the linked
opinion cluster, which weakly suggests the matter was resolved by a reported
decision rather than a routine summary denial. The predicted disposition is
therefore **denied** (`granted = 0`).

**Confidence is deliberately low (0.2).** This reflects model uncertainty about
the *outcome*, driven by the near-total absence of usable facts in the snapshot,
not confidence in the call. A richer snapshot (docket entries, the questions
presented, or the cluster's disposition field) could move this materially.

No per-judge `votes` are predicted because the snapshot exposes no panel or
assigned judges.

## Data limitation note

The snapshot for this case is sparse to the point of being non-predictive for a
merits-style disposition. I made the most conservative reasonable call from the
base rate and the one available signal (the opinion cluster), and recorded the
limitation here. A brief note has been left on the triggering issue (#192) so a
maintainer can confirm whether a fuller snapshot should be provisioned for this
docket.
