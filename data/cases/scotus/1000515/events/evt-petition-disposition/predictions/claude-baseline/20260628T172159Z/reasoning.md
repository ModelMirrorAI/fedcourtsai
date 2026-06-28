# Prediction reasoning — scotus/1000515, evt-petition-disposition

## The question

The event (`kind: petition`, `decision_target: disposition`) asks how the
Supreme Court will dispose of the petition in *Thatcher Heating Co. v. Burtis*.
At the Supreme Court the petition stage is a petition for a writ of certiorari,
so the disposition is effectively grant vs. deny of the writ.

## Governing standard

Certiorari is wholly discretionary (Sup. Ct. R. 10): "Review on a writ of
certiorari is not a matter of right, but of judicial discretion. A petition for a
writ of certiorari will be granted only for compelling reasons." Grant typically
requires a genuine circuit split, an unsettled and important federal question, or
a lower-court decision in conflict with this Court's precedents. The empirical
base rate is decisive: the Court receives on the order of 7,000–8,000 petitions a
term and grants roughly 1% of them. Absent affirmative signals of cert-worthiness,
the prior strongly favors denial.

## Facts available in the snapshot

The point-in-time snapshot (`record/snapshots/2026-06-28.json`) is sparse. It is
a historical Supreme Court docket record with:

- `case_name`: "Thatcher Heating Co. v. Burtis"
- `court_id`: `scotus`
- empty `docket_entries`, empty `docket_number`, no `nature_of_suit`,
  no `cause`, and no `panel`.
- All disposition dates are null: `date_cert_granted`, `date_cert_denied`,
  `date_argued`, and `date_terminated` are all `null`, so the snapshot records no
  resolution.
- One opinion `clusters` reference (cluster 91925) is listed.

There are no docket entries describing the petition's contents, no questions
presented, no indication of a circuit conflict, and no procedural posture beyond
the bare caption. Per the contract I predict only from this snapshot and do not
fetch the cluster contents or any other new case facts.

## Reasoning

With essentially no case-specific signal of cert-worthiness in the snapshot, the
dominant evidence is the base rate, which overwhelmingly favors denial. The lone
weak data point pointing the other way is the presence of an opinion cluster on
the docket: a cluster can indicate the case produced a written opinion, which for
SCOTUS petitions correlates somewhat with cert having been granted and the case
decided on the merits. But a cluster is ambiguous — cert denials, per curiam
dispositions, and memorandum orders also appear as clusters — and I cannot inspect
its contents without fetching new facts, which the contract forbids. I therefore
treat it as only a modest upward nudge on the grant probability rather than a
reason to flip the predicted disposition.

Netting the ~1% prior against that weak cluster signal, I set P(granted) ≈ 0.06
and predict the modal, most conservative outcome: **denied**. Confidence is
moderate (0.55) rather than high because the snapshot is too thin to rule out that
this historical record corresponds to a granted-and-decided case.

## Output

- `predicted_disposition`: denied
- `granted`: 0
- `probability` (P granted): 0.06
- `confidence`: 0.55
- `votes`: omitted — the snapshot identifies no panel or per-Justice information,
  so per-judge votes cannot be grounded in the available facts.
