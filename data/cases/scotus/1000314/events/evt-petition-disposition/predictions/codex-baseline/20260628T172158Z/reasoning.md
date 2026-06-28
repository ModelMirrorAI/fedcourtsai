# Prediction: petition disposition

## Legal question

The event asks for the Supreme Court petition disposition in `McCoy v. Nelson`.
The prediction target is whether the petition will be granted.

## Snapshot used

I used `data/cases/scotus/1000314/record/snapshots/2026-06-28.json`.

The snapshot identifies a Supreme Court docket, `McCoy v. Nelson`, docket number
`255`, with CourtListener docket id `1000314`. It contains no docket entries, no
lower-court source information, no panel, no assigned judge, and no dates for
certiorari granted or denied. The event definition identifies this as an open
petition-disposition event and provides no additional merits facts.

## Governing standard

Supreme Court petition grants are discretionary. A grant normally requires more
than case-specific error correction, such as an important federal question, a
conflict among lower courts, or another reason making Supreme Court review
institutionally important. In the absence of facts showing that kind of signal,
the appropriate baseline is denial because the Court denies the overwhelming
majority of petitions.

## Reasoning

The snapshot provides no case-specific grant indicators: no lower-court split, no
identified federal question, no emergency posture, no noted government
participation, and no docket activity suggesting the petition has drawn special
attention. Because the available record is sparse, I do not infer facts outside
the snapshot.

The strongest driver is therefore the Supreme Court petition base rate. With no
affirmative reason in the snapshot to move above that base rate, I predict denial.
I assign `P(granted) = 0.02`: low enough to reflect the ordinary certiorari grant
rate, but not zero because the snapshot does not disclose the petition papers or
the legal issue.

No per-justice votes are predicted. The event is a petition disposition, and the
snapshot does not contain judge-specific or vote-specific information.
