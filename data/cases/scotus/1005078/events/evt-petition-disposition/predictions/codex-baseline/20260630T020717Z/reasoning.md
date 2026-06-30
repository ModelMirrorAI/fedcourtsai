# Prediction: Myers v. Ohio

## Event

The event is the SCOTUS petition disposition for `scotus/1005078`, docket number `02-9866`, titled *Myers v. Ohio*. The target is whether the petition is granted, denied, or otherwise disposed.

## Snapshot Used

I used `data/cases/scotus/1005078/record/snapshots/2026-06-30.json`. I did not fetch new docket facts. The snapshot identifies a petition filed on 2003-04-01 from the Supreme Court of Ohio, original lower-court docket `(99-395)`, and a linked CourtListener cluster at `https://www.courtlistener.com/api/rest/v4/clusters/130224/`. It has no docket entries, no cert-grant date, no cert-denial date, no argument date, no termination date, and no merits description.

## Governing Standard

For this event, `granted` means the Supreme Court takes up the petition rather than denying it or disposing of it without a grant. In the modern discretionary certiorari system, grants are rare. A petition with sparse record information and no affirmative grant or argument signal should usually be predicted denied unless the snapshot contains a strong contrary marker.

## Case-Specific Signals

The strongest denial signals are the modern docket number `02-9866`, the absence of any `date_cert_granted` or `date_argued`, and the lack of docket entries showing briefing, argument, or merits activity. Docket numbers in this range are commonly ordinary certiorari petitions, often from prisoners or other high-volume petition categories, and the baseline grant rate for such petitions is very low.

The linked opinion cluster is the main countervailing signal. A cluster can indicate that the Supreme Court generated some publishable order or opinion-related record. But the snapshot does not show what the cluster contains, and SCOTUS clusters can be associated with denials, summary orders, or other non-grant dispositions. Because the event must be predicted from the snapshot alone, I treat the cluster as raising the grant probability above a bare-petition baseline, but not enough to overcome the missing grant and argument markers.

## Probability and Disposition

I predict `denied`, with `P(granted) = 0.08`. The probability is above a minimal cert-denial prior because of the linked cluster, but it remains low because the snapshot lacks the features I would expect in a granted modern SCOTUS case. I do not provide per-Justice votes because the snapshot contains no vote information, and certiorari votes are not ordinarily visible in this data.

