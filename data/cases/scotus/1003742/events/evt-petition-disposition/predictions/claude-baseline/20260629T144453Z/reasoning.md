# Prediction: scotus/1003742 — evt-petition-disposition

## The legal question

Will the Supreme Court grant the petition for a writ of certiorari in *Edward
Esparza v. Doug Dretke, Director, Texas Department of Criminal Justice,
Correctional Institutions Division* (No. 04-7542)?

The event's `decision_target` is `disposition` and its `kind` is `petition`, so
the binary outcome of interest is whether the Court grants review (`granted`) or
denies the petition (`denied`).

## Governing standard

Certiorari is wholly discretionary. Under Supreme Court Rule 10, review "is not a
matter of right, but of judicial discretion," and is granted "only for compelling
reasons" — typically a genuine, entrenched conflict among the courts of appeals
or with the Supreme Court's own precedent, or an important unsettled federal
question. The Court receives roughly 7,000–8,000 petitions per Term and grants on
the order of 60–80, an overall grant rate of about 1%.

The base rate is far lower for the subset this petition belongs to. The docket
number `04-7542` places it in the in forma pauperis (IFP) range (paid petitions
that Term carry numbers below 04-2000; IFP petitions begin around 04-5000). IFP
petitions — overwhelmingly pro se filings, many from state prisoners — are
granted at well under one-half of one percent. This petition is a criminal /
habeas matter: the respondent is the Director of the Texas Department of Criminal
Justice, and the case comes up from the Fifth Circuit (originating district
docket 03-20064, judgment entered 2004-06-24). That profile — an IFP prisoner
petition seeking review of a Fifth Circuit habeas judgment — is among the least
likely categories to be granted.

## Facts from the snapshot

From the latest snapshot (`record/snapshots/2026-06-29.json`):

- SCOTUS docket 1003742, docket number 04-7542, filed 2004-12-06.
- On appeal from the United States Court of Appeals for the Fifth Circuit;
  originating court judgment dated 2004-06-24.
- `date_cert_granted`, `date_cert_denied`, and `date_terminated` are all `null`,
  and `docket_entries` is empty in this snapshot, so the snapshot does not itself
  record a disposition.
- The IFP-range docket number and the criminal/habeas posture against a state
  corrections director are the salient predictive signals.

There is nothing in the snapshot indicating a circuit split, a question the Court
has flagged for review, a call for the views of the Solicitor General, or any
other compelling-reason signal that would lift this petition above the base rate.

## Reasoning behind the probability

Absent any case-specific signal pointing toward a grant, the prediction is
governed by the base rate for the relevant subset. IFP criminal/habeas petitions
out of the Fifth Circuit are denied in the great majority of cases — the grant
rate is a small fraction of one percent. I set P(granted) = 0.015, a touch above
the bare base rate to leave room for the small chance of a summary disposition
(e.g., a GVR in light of an intervening decision) in a criminal matter, while
still reflecting that denial is overwhelmingly the expected outcome.

- `predicted_disposition`: **denied**
- `granted`: 0
- `probability` (P granted): 0.015
- `confidence`: 0.9

No per-judge votes are provided: certiorari denials are typically unsigned orders
with no recorded vote breakdown (the rule of four operates without a public
tally), so a judge-level vote prediction would be unsupported.
