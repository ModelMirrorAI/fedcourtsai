# Prediction: Harris v. United States

## Event

The event is the SCOTUS baseline petition disposition for `scotus/1004289`, docket number `93-7515`, titled *Harris v. United States*. The target is whether the petition is granted, denied, or otherwise disposed.

## Snapshot Used

I used `data/cases/scotus/1004289/record/snapshots/2026-06-29.json`. I did not fetch new docket facts. The snapshot contains no docket entries, no cert-grant or cert-denial date, no filed date, no lower-court metadata, no panel, and no merits description. It does contain a linked CourtListener cluster: `https://www.courtlistener.com/api/rest/v4/clusters/117670/`.

## Governing Standard

For the modern Supreme Court discretionary-certiorari model, `granted` means the Court takes the case up rather than denying the petition. Certiorari is discretionary and has a low base rate, so a bare petition with no merits detail would normally be predicted denied. The docket number format `93-7515` is a modern term-number docket, not a pre-1925 mandatory-jurisdiction docket, so the discretionary-cert event model applies.

## Case-Specific Signals

The main case-specific signal is the linked CourtListener opinion cluster. Ordinary denied cert petitions usually do not have a merits opinion cluster attached to the docket. A cluster link is therefore strong evidence that this petition produced some Supreme Court opinion or summary merits action, which usually follows a grant, grant/vacate/remand, or comparable action treated as granted for this event model.

The counterweight is that the snapshot is very sparse: the cert date fields are null and there are no docket entries confirming the grant. A linked cluster can occasionally reflect an opinion respecting denial or another unusual order rather than a full cert grant. Because the snapshot does not expose the cluster contents, I do not treat the signal as conclusive.

## Probability and Disposition

I predict `granted` with probability `0.84`. This is much higher than the ordinary cert-grant prior because of the linked opinion cluster, but below near-certainty because the snapshot lacks docket entries, dates, and lower-court details. I do not provide per-Justice votes because the snapshot contains no vote information and cert votes are not ordinarily exposed in the docket data.
