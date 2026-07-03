# Montgomery v. Hernandez (scotus/1029326) — evt-petition-disposition

## What the snapshot gives us

The 2026-07-03 snapshot is nearly bare: a SCOTUS docket captioned **"Montgomery
v. Hernandez"** with no docket entries, no docket number, no filed / argued /
terminated dates, no parties or counsel, and no cert-grant/denial dates. The
substantive signals are the case name, the court (`scotus`), the CourtListener
source (a bulk historical import, docket row created in 2014), and a single
linked opinion cluster — meaning the Court produced at least one opinion in
this matter. The corpus row for the case is equally bare (no dates, topic,
disposition, or originating court).

## Case identification and era

The SCOTUS reports contain a case under this exact caption: *Montgomery v.
Hernandez*, 25 U.S. (12 Wheat.) 129 (1827), a writ of error from a Louisiana
court raising review under § 25 of the Judiciary Act of 1789. The snapshot's
shape (historical bulk import, low-numbered opinion cluster attached, no modern
docket metadata) is fully consistent with a case of that era, and I treat the
identification as the working hypothesis — while noting my recall of this
case's specifics is weaker than for better-known captions. This is background
legal-historical knowledge, not a new fact fetched about this docket; no
external lookups about this case were made.

## The legal question and governing standard

This is **not** a certiorari-era petition. In the 1820s the Supreme Court's
appellate docket was mandatory (writs of error and appeals of right); the
discretionary cert regime dates to 1891/1925. So the "petition disposition"
frame maps poorly onto the event. Under § 25 of the Judiciary Act of 1789, the
Court could re-examine a state-court judgment only where the decision below was
*against* the title, right, or privilege claimed under federal law; where the
party claiming under the United States prevailed below, the Court had no
jurisdiction and the writ of error was dismissed. My recollection of
*Montgomery v. Hernandez* is that it turned on exactly this § 25 limit (it sits
in the reports alongside *Williams v. Norris*, 12 Wheat. 117 (1827), the
same Term's leading § 25 want-of-jurisdiction dismissal), with the writ of
error dismissed for want of jurisdiction — but I hold that outcome recollection
at moderate, not high, confidence.

## Base rates from the corpus

`fedcourts stats --court scotus --resolved-only` over the corpus's resolved
SCOTUS cases (n=296): `other` 78.4%, `dismissed` 15.9%, `denied` 4.4%,
`granted` 1.4%. The resolved historical SCOTUS cases are labeled from their
opinion-stage outcomes, so merits affirm/reverse outcomes land in `other` while
jurisdictional and procedural terminations land in `dismissed`. No Term-year or
originating-circuit cut is possible — the snapshot has no dates or docket
number to anchor one.

## Prediction

- **`granted` = 0, P(granted) = 0.01.** Nothing here is "granted" under any
  reading: the corpus base rate for `granted` among resolved SCOTUS cases is
  ~1.4%, and the cert frame doesn't apply to an 1820s mandatory-jurisdiction
  writ of error.
- **`predicted_disposition` = `dismissed`.** Driven by the working
  identification of the case as the 1827 § 25 writ-of-error matter dismissed
  for want of jurisdiction, which also aligns with the second-most-common
  resolved label in the corpus (15.9%).
- **Alternative considered:** if my outcome recollection is wrong — e.g. the
  Court took jurisdiction in part and affirmed, or the outcome labeler
  classifies the opinion as a generic merits/historical outcome — the label
  would be `other` (the corpus modal class at 78%). I weigh the case-specific
  recollection at roughly 55–60% against that base rate, which is why
  `confidence` is 0.4: the *direction* (not granted) is near-certain; the exact
  label bucket is genuinely uncertain between `dismissed` and `other`.
- **Votes:** omitted. The snapshot carries no panel, and predicting named
  seats of the 1827 Marshall Court from a bare docket would be manufactured
  precision.
