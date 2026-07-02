# The Alicia (scotus/1013618) — evt-petition-disposition

## What the snapshot gives us

The 2026-07-01 snapshot is nearly bare: a SCOTUS docket titled **"The Alicia"**
with no docket entries, no docket number, no filed/argued/terminated dates, no
parties or counsel, and no cert-grant/denial dates. The only substantive signals
are the case name, the court (`scotus`), the CourtListener source (a bulk
historical import), and a single linked opinion cluster — meaning the Court
produced at least one opinion in this matter.

## Case identification and era

A one-word admiralty-style caption ("The <vessel name>") is the classic form of
a 19th-century prize or admiralty case, and the SCOTUS reports contain exactly
one such case under this caption: *The Alicia*, 74 U.S. (7 Wall.) 571 (1869), a
Civil War blockade-running prize cause. The snapshot's shape (historical bulk
import, opinion cluster attached, no modern docket metadata) is fully consistent
with that identification, and I treat it as the working hypothesis. This is
background legal-historical knowledge, not a new fact fetched about this docket;
no external lookups about this case were made.

## The legal question and governing standard

This is **not** a certiorari-era petition. In 1869 the Supreme Court's appellate
docket was overwhelmingly mandatory (writs of error and appeals of right); the
discretionary cert regime dates to 1891/1925. So the "petition disposition"
frame maps poorly onto the event: the operative question the Court actually
faced in *The Alicia* was jurisdictional — whether an Act of Congress could
transfer a prize cause still *pending and undecided* in the circuit court
directly onto the Supreme Court's appellate docket. Under Article III appellate
jurisdiction doctrine (already settled by cases like *Marbury*'s
original/appellate line and applied throughout the era), appellate review
requires a judgment or decree below to act upon. The Chase Court held the
transfer ineffective and refused to entertain the cause, disposing of it by
dismissal/striking it from the docket for want of jurisdiction.

## Base rates from the corpus

`fedcourts stats --court scotus --group-by disposition` over the resolved SCOTUS
cases in the corpus (n=296): `other` 78.4%, `dismissed` 15.9%, `denied` 4.4%,
`granted` 1.4%. The corpus's resolved historical SCOTUS cases are labeled from
their opinion-stage outcomes, so merits affirm/reverse outcomes land in `other`
while jurisdictional and procedural terminations land in `dismissed`. A
`fedcourts query --court scotus` sample of resolved priors confirms this
pattern (e.g. a writ-of-error case ending in a want-of-jurisdiction dismissal is
labeled `dismissed`; ordinary merits opinions are labeled `other`). No term-year
cut is possible — the snapshot has no dates or docket number to anchor a Term.

## Prediction

- **`granted` = 0, P(granted) = 0.01.** Nothing here is "granted" under any
  reading: the corpus base rate for `granted` among resolved SCOTUS cases is
  ~1.4%, the cert frame doesn't apply to an 1869 mandatory-jurisdiction cause,
  and the specific historical outcome was a refusal to exercise jurisdiction.
- **`predicted_disposition` = `dismissed`.** Driven by the identification of
  the case as *The Alicia* (1869), whose outcome was a dismissal for want of
  jurisdiction. This also aligns with the second-most-common resolved label in
  the corpus.
- **Alternative considered:** if the outcome labeler instead classifies the
  opinion as a generic merits/historical outcome, the label would be `other`
  (the corpus modal class at 78%). That residual-label risk, plus the small
  chance the docket is a different vessel's case, is why `confidence` is 0.5
  rather than higher — the *direction* (not granted) is near-certain, the exact
  label bucket is the uncertain part.
- **Votes:** omitted. The snapshot carries no panel, and while the 1869 decision
  was unanimous, predicting nine named seats from a bare docket would be
  manufactured precision.
