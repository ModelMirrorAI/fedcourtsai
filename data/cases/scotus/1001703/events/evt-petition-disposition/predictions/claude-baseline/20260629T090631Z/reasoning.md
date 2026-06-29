# Prediction reasoning — scotus/1001703 (Carlos Sanders v. Ohio), evt-petition-disposition

## The legal question

The event `evt-petition-disposition` (kind `petition`, decision target
`disposition`) asks how the Supreme Court of the United States will dispose of
the petition in *Carlos Sanders v. Ohio*. For SCOTUS, a "petition" of this kind
is a petition for a writ of certiorari, and the disposition is almost always a
binary order: cert **granted** or cert **denied** (with occasional GVRs,
dismissals, or withdrawals). `granted` here means the petition is granted.

## Governing standard

Certiorari is wholly discretionary (Supreme Court Rule 10). The Court grants
review only for "compelling reasons" — typically a genuine circuit split, a
conflict with the Court's own precedent, or an important unsettled federal
question. There is no right to review, and the empirical base rate is stark: the
Court grants on the order of ~1–3% of the several thousand petitions filed each
Term, and the rate is far lower still on the *in forma pauperis* docket.

## What the snapshot actually tells me

I predict only from the provisioned snapshot
(`record/snapshots/2026-06-29.json`) and do not fetch new docket facts. The
snapshot is thin but carries two structurally meaningful fields:

- `court_id: scotus`, `case_name: "Carlos Sanders v. Ohio"`,
  `docket_number: "01-8551"`, `date_filed: 2002-02-25`.
- `appeal_from_str: "Supreme Court of Ohio"`; the originating-court record points
  to Ohio docket `98-1209`. This is a state-court criminal/post-conviction
  posture (an individual petitioner against a State).
- `docket_entries: []` — no question presented, no merits briefing, no order
  text.
- `date_argued`, `date_cert_granted`, `date_cert_denied`, `date_terminated` are
  all `null`.
- One opinion-cluster reference is present:
  `clusters: [".../clusters/120126/"]`.

None of the Rule 10 factors (circuit split, CVSG, relisting, amicus activity) can
be assessed from these fields.

## How I weigh the signals

Two structural signals point in opposite directions:

1. **Downward — the IFP docket number.** A 2001-Term docket number of `01-8551`
   is an *in forma pauperis* number (paid petitions that Term were numbered well
   below ~1500; numbers in the 5000–9000 range are the pauper docket). Combined
   with the individual-vs-State criminal posture and appeal from a state supreme
   court, this is a textbook IFP petition, whose grant rate is a small fraction
   of one percent — materially below even the overall ~1–3% base rate.

2. **Upward — the opinion cluster.** A docket linked to an opinion cluster
   (120126) is somewhat more often a case that was actually decided than a routine
   order-list denial, since plain denials are usually recorded as order-list
   entries rather than their own cluster. That nudges the probability of a grant
   above the IFP base rate.

I deliberately do not over-read the cluster: I cannot open it (that would be
fetching a new case fact, which the contract forbids), so I cannot tell whether
it is a merits opinion, an in-chambers opinion, a memorandum, or a published
denial — and for older, incompletely-ingested CourtListener records the
key dates are frequently `null` even for decided cases, so their emptiness here
is uninformative either way.

## Probability and disposition

Balancing the strong IFP/criminal downward signal against the modest,
unverifiable upward signal from the opinion cluster, I set **P(granted) = 0.12** —
well below 0.5 (so `granted = 0`, `predicted_disposition = denied`), below the
~0.30 I would assign a paid-docket petition with a comparable cluster reference,
but above the raw IFP base rate to reflect the cluster. Confidence is low
(**0.30**): the snapshot carries no merits information, and the result is
sensitive to how much weight the cluster reference deserves.

Per-judge votes are omitted: cert dispositions issue as an unsigned Court order
without recorded individual votes, and nothing in the snapshot supports a vote
breakdown.

## Notes / blockers

Not blocked — the snapshot and event definition are present and well-formed, so
no issue comment is warranted. The chief limitation is the sparseness of the
snapshot (empty `docket_entries`, all key dates `null`), which caps achievable
confidence; this is recorded here rather than escalated.
