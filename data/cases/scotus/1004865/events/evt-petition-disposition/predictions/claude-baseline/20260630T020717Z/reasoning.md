# Prediction reasoning — scotus/1004865, evt-petition-disposition

## The legal question

The event is a `petition`-kind disposition before the Supreme Court of the
United States in *Railroad Comm. v. Eastern Tex. RR* (docket "145 and 146"). The
decision target is the **disposition** of the matter: the binary `granted`
field, P(granted), and the categorical disposition label
(granted / denied / granted-in-part / dismissed / withdrawn / other).

This is **not** a modern discretionary certiorari petition. The low paired
docket numbers ("145 and 146"), the absence of any `date_cert_granted` /
`date_cert_denied` fields, and the case posture place this in the early-20th-
century / pre-1925 era, when the Court's jurisdiction over such matters was
largely **mandatory** (appeals and writs of error), not the discretionary cert
docket. So "grant rate ≈ 1%" reasoning from Supreme Court Rule 10 does not
govern; the question is how a matter the Court actually took up was disposed of.

## Facts from the snapshot

The provisioned snapshot (`record/snapshots/2026-06-30.json`) is thin:

- **Court / posture.** SCOTUS docket 1004865; `court_id` = `scotus`; docket
  number raw "145 and 146" (a consolidated pair). `docket_entries` is empty and
  every date field (`date_filed`, `date_argued`, `date_cert_granted`,
  `date_cert_denied`, `date_terminated`) is `null`.
- **A merits disposition exists.** The snapshot links one opinion **cluster**
  (`clusters: [.../clusters/100348/]`) with `precedential_status` "Published"
  (per the corpus row). A published opinion cluster means the Court did not
  simply turn the matter away on the papers — it **resolved the matter with a
  written opinion**. That rules out the "denied"/"withdrawn" tails and points to
  a substantive disposition (a merits ruling → `other`, or a `dismissed`).
- **Parties / subject.** A state Railroad Commission against a railroad — a
  railroad-regulation controversy (here, the Texas Railroad Commission and the
  Eastern Texas Railroad).

Per the contract I predict **only** from this snapshot; I did not fetch new
docket facts. I used the corpus `query` tool for **priors / legal context**
(base rates over already-decided, comparable historical SCOTUS matters), not for
new facts about this case.

## Governing standard and base rates

For this historical mandatory-jurisdiction corpus, the realized disposition
distribution over 244 decided SCOTUS priors is:

- `other` (a merits ruling — affirmed / reversed / decided on the merits): **75%**
- `dismissed`: **19%**
- `denied`: **4.5%**
- `granted`: **1.6%**

So a categorical `granted` outcome is very rare, and `granted = 0` is strongly
favored: the binary target here is not "did the Court grant discretionary
review" but "was the matter granted as a disposition," which almost never is the
label for these merits-posture cases. Among the railroad / commission / equity
priors specifically, several resolved as `dismissed` (e.g. dockets that became
academic, mootness, or jurisdictional dismissals).

## Reasoning behind the probability and the disposition

- **`granted = 0`, `probability` (P(granted)) = 0.02.** A grant label is the
  rarest outcome (1.6% base) and is a poor fit for a mandatory-jurisdiction
  matter the Court resolved by published opinion. I keep a small non-zero
  probability rather than 0 because the snapshot is thin and I cannot fully rule
  out an unseen feature.

- **`predicted_disposition = dismissed`** (the close runner-up to the modal
  `other`). The case is a railroad-regulation controversy of the kind that, in
  this corpus, frequently became moot or jurisdictionally non-reviewable before
  final disposition — a railroad-abandonment / continued-operation dispute where
  the corporate party's dissolution or the controversy's evaporation leaves
  nothing to decide on the merits, and the Court reverses with directions to
  dismiss. That pattern fits this caption and posture and is the second-most-
  common label (19%) overall and well-represented among the railroad/commission
  priors. The base-rate modal alternative is `other` (a merits affirm/reverse);
  I treat that as the most likely competing outcome.

- **`confidence = 0.5`.** I am highly confident in `granted = 0` and the low
  P(granted), but the categorical label is a genuine `dismissed`-vs-`other` toss
  between the two dominant historical buckets, so I hold confidence at the
  midpoint to reflect that the specific label could land on `other`.

## Votes

These early-Court matters were decided by the full bench, typically through a
single opinion and without a published per-Justice tally of the disposition.
The snapshot lists no `panel`, so I record no per-judge votes.
