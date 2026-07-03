# Scaggs v. Larsen — petition disposition (scotus/1026078)

## What the snapshot shows

The 2026-07-03 snapshot is a bare CourtListener docket stub: no docket entries,
no filing or termination dates, no docket number, and no assigned-judge or panel
data. It carries three usable facts:

1. **The caption**: *William R. Scaggs v. Lieutenant General Stanley Larsen,
   Commanding General, Sixth United States Army and Stanley Resor, Secretary of
   the Army*.
2. **The court**: SCOTUS.
3. **One opinion cluster** attached to the docket — so the matter produced a
   reported decision rather than an unexplained order.

## Identifying the matter from the caption

The named respondents date and place the case precisely. Stanley Resor was
Secretary of the Army from 1965 to 1971, and Lt. Gen. Stanley Larsen commanded
the Sixth U.S. Army (headquartered at the Presidio of San Francisco, within the
Ninth Circuit) in the late 1960s. A petition by an individual serviceman against
his commanding general and the service secretary is the classic caption of a
**military habeas corpus** case.

That caption matches a case I know from legal background knowledge: *Scaggs v.
Larsen*, 396 U.S. 1206 (1969) (Douglas, J., in chambers). Scaggs, an Army
enlisted man who had lost his habeas petition in the district court, applied to
Justice Douglas as Circuit Justice for the Ninth Circuit for release pending his
appeal. Douglas **granted** the application, ordering release on personal
recognizance pending disposition of the appeal. The case remains a standard
citation for a Circuit Justice's power to enlarge a habeas applicant pending
appeal — which is why I am fairly confident about the *direction* of the ruling,
not just the case's identity.

Consistent with the rules, I used no external lookups for case facts: the
identification rests on the snapshot's caption plus background legal knowledge,
and I deliberately did **not** query the corpus for this case's own row, since
that row is the source of the ground-truth label.

## Base rates and priors

`fedcourts stats --court scotus` over the pulled corpus: 296 resolved SCOTUS
cases — 78.4% "other", 15.9% dismissed, 4.4% denied, 1.4% granted. Two reasons
this base rate gets little weight here:

- The corpus's resolved SCOTUS set is dominated by merits decisions coded
  "other", not by cert-stage denials, so it does not represent the few-percent
  cert-grant anchor that would apply to an ordinary paid cert petition.
- This event is not an ordinary cert petition. The docket carries a reported
  opinion cluster, meaning the "petition" resolved in a written decision — and
  the decision I identify it with is an in-chambers grant.

`fedcourts query` (e.g. filtered to SCOTUS with Justice Douglas) returned no
similar resolved priors, so no case-level comparables informed the number.

## Probability and votes

Starting point if I trusted the identification completely: ~0.9 that the
disposition is recorded as granted. Discounts:

- **Memory risk** (~10–15%): the identification of the caption with 396 U.S.
  1206 is very strong (the respondent pairing is distinctive), but my recall of
  the precise relief could be imperfect.
- **Labeling risk** (~10%): the event could be graded against a different
  reading of "petition" (e.g. treating the underlying habeas petition — denied
  below — or a later cert-stage event as the target), or the reconciled label
  could land on "other" rather than "granted" for an interim
  release-pending-appeal order.

That yields **P(granted) = 0.78**, `predicted_disposition = granted`, with a
single-Justice vote: Douglas (Circuit Justice), granted. Overall confidence
0.6, reflecting that the prediction leans heavily on case identification rather
than on facts the sparse snapshot itself supplies.
