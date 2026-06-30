# Prediction: Sanders v. Pennsylvania

## Event

The event is the Supreme Court petition disposition for `scotus/1005659`, docket number `93-7173`, titled *Sanders v. Pennsylvania*. The target is whether the petition is granted or denied.

## Snapshot Used

I used `data/cases/scotus/1005659/record/snapshots/2026-06-30.json`. I did not fetch new docket facts. The snapshot identifies a Supreme Court docket created in CourtListener's data in 2014, with no docket entries, no cert-grant date, no cert-denial date, no argument date, no termination date, and one linked CourtListener cluster.

## Governing Standard

For a Supreme Court petition, `granted` means the Court accepts review. Certiorari is discretionary and denials are the ordinary outcome, especially for case captions and high docket-number ranges that look like routine state-criminal or prisoner petitions. A grant usually leaves stronger snapshot signals, such as a cert-grant date, an argument date, merits-stage docket entries, or fuller lower-court metadata.

## Case-Specific Signals

The strongest signals point to denial. The snapshot has no affirmative grant marker, no argument marker, no docket activity, no originating-court details, and no termination information. The docket number `93-7173` is also in a high-number range that is more consistent with the large volume of ordinary petitions than with granted merits cases.

The linked cluster is the main countervailing signal. A Supreme Court cluster can indicate a merits opinion, but it can also reflect an order, denial-related entry, or other non-merits disposition. Because the snapshot does not classify the cluster or expose opinion text, I treat it as raising the grant probability slightly above a bare denial prior, but not enough to overcome the absence of grant, argument, or merits-stage indicators.

## Probability and Disposition

I predict `denied`, with `P(granted) = 0.06`. Confidence is moderate rather than high because the snapshot is sparse and the linked cluster is not classified. I do not provide per-Justice votes because this is a petition-disposition event and the snapshot contains no vote information.
