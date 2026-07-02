# Prediction reasoning — scotus/1016450, evt-petition-disposition

## The legal question

The event asks for the **disposition** of a petition (`kind: petition`,
`decision_target: disposition`) in *Brooks v. South Carolina*, a Supreme Court
of the United States matter. The outcome space is the standard disposition enum
(granted / denied / granted-in-part / dismissed / withdrawn / other), with
`granted` as the binary target and `probability` as P(granted).

## What the snapshot tells me

I predict only from the provisioned snapshot
(`data/cases/scotus/1016450/record/snapshots/2026-07-02.json`). I did not fetch
new docket facts and did not resolve the linked opinion cluster, because the
realized disposition is exactly the quantity under evaluation. The snapshot is a
bare metadata stub:

- `docket_entries: []` — no filings, no petition text, no order text.
- `date_filed`, `date_argued`, `date_cert_granted`, `date_cert_denied`,
  `date_terminated` are all `null` — no recorded disposition in this snapshot.
- No `nature_of_suit`, no `cause`, no question presented, no merits facts.
- `clusters` lists one opinion cluster, indicating some printed entry exists;
  I do not open it (that would be reading the outcome).

Three **structural** identifiers on the face of the snapshot carry the only
real signal:

- **Docket number `610, Misc`.** Before October Term 1970 the Court kept a
  separate **Miscellaneous Docket** for *in forma pauperis* petitions — mostly
  pro se state and federal prisoners. This is therefore an IFP matter from
  roughly the 1930s–1970 era, and IFP petitions were granted at a markedly
  lower rate than the paid (Appellate) docket.
- **Caption `Brooks v. South Carolina`.** An individual petitioner against the
  State as respondent — characteristically a state criminal conviction or
  state post-conviction matter reaching the Court on certiorari.
- **The linked cluster.** Something about this case was printed in U.S.
  Reports. That is weak evidence either way: the digitized historical corpus
  includes both per curiam merits dispositions *and* one-line
  certiorari-denied / appeal-dismissed order entries, so a cluster does not
  imply the petition succeeded.

## The governing standard

Certiorari is discretionary. Under the considerations now codified in Supreme
Court Rule 10 (conflict among circuits or state courts of last resort, an
important unsettled federal question, or a decision in conflict with this
Court's precedent), the writ is denied in the overwhelming majority of cases;
the historical grant rate on the Miscellaneous Docket ran on the order of a
few percent, below the paid docket's.

## Base rates from the corpus

`fedcourts stats --court scotus --resolved-only` over the 296 resolved SCOTUS
cases in the corpus: **granted 1.4%, denied 4.4%, dismissed 15.9%, other
78.4%** (the "other" mass is unparsed disposition text on old opinion-derived
rows). Restricting to the machine-readable labels, granted is 4 of 64 (~6%) —
an upper anchor that already reflects this corpus's selection toward cases
with printed entries. Grouping by originating circuit adds nothing here (the
originating court is unknown for the historical rows, including this one).

## How I reach a probability

With no merits facts, the defensible estimate blends:

- the ~1–3% unconditional IFP grant rate for the era (floor);
- the ~6% granted share among the corpus's machine-readable historical
  dispositions, which conditions on a printed U.S. Reports entry existing —
  the situation this docket is in (mid anchor);
- one modest case-specific upweight: during the early 1960s the Court
  repeatedly took and **summarily reversed** South Carolina breach-of-the-peace
  and civil-rights-era convictions (the *Edwards v. South Carolina*, 372 U.S.
  229 (1963) line, e.g. *Fields v. South Carolina*, 372 U.S. 522 (1963) (per
  curiam)). A Miscellaneous Docket case captioned against South Carolina with
  a printed entry has a non-trivial chance of belonging to that line, which
  raises the grant tail above the generic IFP floor. I hold this to a modest
  adjustment because the snapshot does not date the case and I will not fetch
  facts to confirm the era.

I set `predicted_disposition = denied`, `granted = 0`, and
`probability = 0.10`. Denied is the modal realized outcome for an IFP
certiorari petition against a state respondent; dismissed is the main
alternative non-grant label (an appeal posture — "dismissed for want of a
substantial federal question" — cannot be excluded from the docket number
alone), but certiorari was the dominant IFP vehicle for state criminal cases,
so denied remains the single most likely label.

`confidence = 0.2` reflects that the directional call is well anchored in the
docket structure and base rates, but the snapshot carries no dates, parties
detail, or merits facts, so the precise probability rests on era inference and
corpus-selection reasoning rather than case-specific evidence.

No per-judge `votes` are predicted: the snapshot identifies no panel or Term,
so naming Justices would be guesswork.
