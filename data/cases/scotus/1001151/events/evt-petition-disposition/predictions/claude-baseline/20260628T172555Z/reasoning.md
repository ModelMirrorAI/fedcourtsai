# Prediction reasoning — scotus/1001151, evt-petition-disposition

## The legal question

Will the Supreme Court grant the petition for a writ of certiorari in
*Timothy Dashun White v. United States* (No. 01-7700)? The event's
`decision_target` is the petition's **disposition**; "granted" means certiorari
is granted.

## Governing standard

Review on certiorari is "not a matter of right, but of judicial discretion"
(Sup. Ct. R. 10). The Court grants a petition only when there are "compelling
reasons" — typically a genuine conflict among the courts of appeals, a conflict
with the Court's own precedent, or an important unsettled federal question.
Rule 10 expressly cautions that a petition asserting only the misapplication of
a properly stated rule of law, or an erroneous factual finding, is rarely
granted. Across all petitions the Court grants roughly 1%; for *in forma
pauperis* petitions the rate is far lower (well under 0.2%).

## Facts from the snapshot that drive the outcome

Reasoning is based solely on the provisioned snapshot
(`data/cases/scotus/1001151/record/snapshots/2026-06-28.json`):

- **Posture is a routine criminal cert petition.** The case is captioned
  *White v. United States*, an individual petitioner against the federal
  government, on review from the U.S. Court of Appeals for the Fifth Circuit
  (originating district docket 01-20053). This is the most common — and most
  routinely denied — category of certiorari petition.
- **Docket number indicates an IFP petition.** The Supreme Court docket number
  `01-7700` falls in the range reserved for *in forma pauperis* filings (numbers
  at and above ~5000 within a Term). IFP petitions are granted at a rate
  dramatically below the already-low overall grant rate.
- **No signal of any feature that draws a grant.** The snapshot records no
  argument date (`date_argued` is null), no cert-granted or cert-denied date
  (both null), no termination date, and an empty `docket_entries` list. Nothing
  in the record indicates a circuit split, a call for the views of the Solicitor
  General, a relisting, or any other marker that distinguishes the small set of
  granted petitions. There are no facts suggesting a "compelling reason" under
  Rule 10.

## Probability and disposition

The base rate for this category (an IFP criminal cert petition with no
distinguishing feature) is overwhelmingly denial. I assign **P(granted) = 0.01**,
predicting **disposition = denied** (`granted = 0`). The slightly non-zero
probability reflects irreducible uncertainty rather than any affirmative
grant signal in the record. Confidence is high (0.95) because the prediction
rests on a well-established base rate and a posture with no countervailing facts.

## Votes

Certiorari is granted under the "rule of four," and the Court does not publish
individual Justices' votes on the cert pool. No panel or judge assignment is
present in the snapshot, so no per-judge votes are recorded.
