# Prediction — scotus/1004191 · evt-petition-disposition

**Case:** Gregory Hunt v. Alabama · **Event:** petition disposition
**Predicted disposition:** denied · **P(granted): 0.02** · granted = 0

## The legal question

The event `evt-petition-disposition` asks for the disposition of the petition
before the U.S. Supreme Court in *Gregory Hunt v. Alabama* (docket no. 01-8924).
The case is an appeal from the Supreme Court of Alabama (originating court docket
`(1001358)`), a state criminal/capital matter. "Granted" means the Court grants
review (grants certiorari); "denied" means it declines review.

## Governing standard

Review on certiorari is wholly discretionary (Supreme Court Rule 10): "A petition
for a writ of certiorari will be granted only for compelling reasons." Cert is
reserved for cases presenting circuit splits, important unsettled federal
questions, or decisions in conflict with the Court's precedent — not for
error-correction. The petitioner bears a heavy burden, and the overwhelming
default disposition is denial.

## Facts from the snapshot

The point-in-time snapshot (`2026-06-29.json`) is sparse:

- `case_name`: "Gregory Hunt v. Alabama"; `court_id`: `scotus`.
- `docket_number`: **01-8924**; `date_filed`: 2002-03-13.
- `appeal_from_str`: "Supreme Court of Alabama"; originating court docket
  `(1001358)`.
- `date_cert_granted`: null and `date_cert_denied`: null; `date_terminated`:
  null; `docket_entries`: empty. The snapshot records no disposition, so the
  event is treated as unresolved and predicted prospectively.

Two structural signals drive the prediction:

1. **It is a discretionary cert petition to SCOTUS.** The unconditional base rate
   for a grant of certiorari is very low — on the order of ~1% of all paid
   petitions in a modern Term, and far lower across the full docket.
2. **The docket number 01-8924 places this on the *in forma pauperis* docket.**
   SCOTUS numbers paid petitions in a low block within each Term and assigns IFP
   petitions high numbers (here, 8924). IFP petitions — predominantly pro se
   criminal and post-conviction filings, consistent with this being a state
   capital appeal from the Alabama Supreme Court — are granted at a rate well
   under 0.2%, an order of magnitude below the already-low overall rate.

Nothing in the snapshot (no flagged circuit split, no CVSG, no relisting signal,
no cert grant date) cuts against the strong structural prior toward denial.

## Probability and disposition

Combining the very low cert base rate with the IFP-docket signal and the absence
of any countervailing facts, I set **P(granted) = 0.02**, slightly above the raw
IFP base rate only to hold back tail uncertainty given how thin the snapshot is.
This rounds to a binary `granted = 0` and `predicted_disposition = "denied"`,
with moderate-to-high confidence (0.85).

No per-judge votes are reported: a cert grant requires four Justices, but the
Court does not publish individual votes on the typical certiorari denial, and the
snapshot lists no panel, so a vote breakdown would be invented rather than
supported.

## Notes on inputs

I predicted only from the provisioned snapshot. I consulted the corpus via
`fedcourts query` for SCOTUS priors, but the available corpus rows are a small,
historical sample of published opinions whose disposition labels track merits
outcomes rather than cert grant/deny, so they are not a representative base-rate
sample for modern certiorari petitions; I relied instead on the well-established
discretionary-review base rate as legal context. I did not fetch any new docket
facts about this case.
