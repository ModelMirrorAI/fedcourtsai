# Prediction reasoning — scotus/1000314 (McCoy v. Nelson), evt-petition-disposition

## The legal question

The event `evt-petition-disposition` (kind `petition`, decision target
`disposition`) asks how the Supreme Court of the United States will dispose of
the petition in *McCoy v. Nelson*. For SCOTUS, a "petition" of this sort is a
petition for a writ of certiorari, and the disposition is overwhelmingly a binary
order: cert **granted** or cert **denied** (with occasional GVRs, dismissals, or
withdrawals). `granted` here means the petition is granted.

## Governing standard

Certiorari is discretionary (Supreme Court Rule 10). The Court grants review only
for "compelling reasons" — typically a genuine circuit split, a conflict with the
Court's own precedent, or an important unsettled federal question. There is no
right to review, and the empirical base rate is stark: the Court grants on the
order of ~1–3% of the several thousand paid and *in forma pauperis* petitions it
receives each Term. The strong prior for any given petition is therefore
**denial**.

## What the snapshot actually tells me

I am required to predict only from the provisioned snapshot
(`record/snapshots/2026-06-28.json`) and not fetch new docket facts. The snapshot
is extremely thin:

- `court_id: scotus`, `case_name: "McCoy v. Nelson"`, `docket_number: "255"`.
- `docket_entries: []` — no merits briefing, no scheduling, no order text.
- `date_argued`, `date_cert_granted`, `date_cert_denied`, `date_terminated`,
  `date_filed` are all `null`.
- One opinion-cluster reference is present:
  `clusters: [".../clusters/91942/"]`.
- `date_created: 2014-10-30`, `date_modified: 2023-08-02`.

There is **no substantive signal about the petition's merits** — no question
presented, no indication of a circuit split, no CVSG, no relisting history, no
amicus activity. None of the Rule 10 factors can be assessed from these fields.

## How I weigh the one real signal

The single decision-relevant structural fact is the presence of an opinion
**cluster** (91942). In CourtListener, a docket linked to an opinion cluster is
more often a case that was actually *decided* (cert granted, argued, opinion
issued) than a routine denial, since plain denials are recorded as order-list
entries rather than as their own opinion clusters. That pushes the probability of
a grant **above** the ~1–3% base rate.

This signal is, however, weak and ambiguous, and I deliberately do not over-read
it:

- I cannot open cluster 91942 — doing so would be fetching a new case fact, which
  the contract forbids. So I cannot confirm whether it is a merits opinion, an
  in-chambers opinion, a memorandum, or a published denial.
- The dates cut the other way: a genuinely granted-and-decided case would
  normally have `date_cert_granted` and `date_argued` populated, and here they
  are all `null`. For older/incompletely-ingested CourtListener records those
  fields are frequently empty even for decided cases, so this is suggestive but
  not dispositive.

## Probability and disposition

Balancing the overwhelming denial base rate against the modest, unverifiable
upward signal from the opinion cluster, I set **P(granted) = 0.30** — well below
0.5 (so `granted = 0`, `predicted_disposition = denied`) but materially above the
raw cert base rate to reflect the cluster signal. Confidence is low (**0.25**):
the snapshot carries almost no merits information, and the result is sensitive to
how much weight the cluster reference deserves.

Per-judge votes are omitted: cert dispositions issue as a Court order without
recorded individual votes, and nothing in the snapshot supports a vote breakdown.

## Notes / blockers

Not blocked — the snapshot and event definition are present and well-formed, so
no issue comment is warranted. The chief limitation is the sparseness of the
snapshot (empty `docket_entries`, all key dates `null`), which caps achievable
confidence; this is recorded here rather than escalated.
