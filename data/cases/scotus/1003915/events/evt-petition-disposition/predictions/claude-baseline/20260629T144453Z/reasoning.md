# Prediction reasoning — scotus/1003915, evt-petition-disposition

## The event

`evt-petition-disposition` is a `petition` event whose `decision_target` is
`disposition`: how the Supreme Court disposed of the petition by which *College
Point Boat Corp. v. United States* (docket no. 121) came before it — i.e.,
whether the Court took the case up and resolved it (granted) or turned it away
(denied/dismissed).

## What the snapshot tells me

I predict only from the provisioned snapshot
(`data/cases/scotus/1003915/record/snapshots/2026-06-29.json`). It is sparse —
a historical SCOTUS docket imported into CourtListener (`source: 16`,
`date_created` 2014) with no docket entries, no panel, and none of the
`date_cert_granted` / `date_cert_denied` / `date_argued` fields populated. For
dockets of this vintage those date fields are routinely empty regardless of
outcome, so their absence carries little signal.

The one materially informative field is `clusters`: the docket is linked to
exactly one opinion cluster (`.../clusters/100556/`). On the Supreme Court, a
linked opinion cluster means a written opinion issued in the matter. The Court
does not author a full opinion cluster for a petition it merely denies — a
denial is a one-line order, not a clustered opinion. The presence of a merits
opinion is therefore strong, case-specific evidence that the Court took the
case up and decided it: the petition/application for review was effectively
granted and the case resolved on the merits.

## Standard / base-rate considerations

The unconditional base rate for discretionary review is overwhelmingly denial
(~99% of modern cert petitions are denied). That prior, however, is
conditioned away by the opinion-cluster signal: this docket is in the small
slice that produced a written opinion. Additionally, a docket numbered 121 of
this era predates (or sits at the threshold of) the modern certiorari regime
established by the Judiciary Act of 1925; many cases then reached the Court by
appeal, writ of error, or certificate — routes the Court decides on the merits
as of right. Both readings point the same way: a clustered opinion implies the
matter was heard and disposed of, not turned away at the threshold.

## Call

- `predicted_disposition`: **granted** (`granted = 1`).
- `probability` (P(granted)): **0.75**. The opinion-cluster signal dominates the
  denial base rate, but I temper the estimate because the snapshot is thin, the
  precise semantics of "petition disposition" for a pre-1925 docket are
  ambiguous (grant of review vs. outcome on the merits), and a single derived
  field carries the weight.
- `confidence`: **0.55**, reflecting that thinness and ambiguity.
- `votes`: omitted. The snapshot carries no panel or judge data, so I cannot
  attribute per-justice votes without inventing facts.

I did not consult external sources for case facts (the contract is to predict
from the snapshot alone), and no new facts were fetched.
