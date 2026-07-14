# Trump v. Barbara, No. 25-365 — petition disposition (cert before judgment)

## Bottom line

**Predicted disposition: granted. P(granted) = 0.99.**

## The outcome is present in the provisioned baseline — read this first

This cell is marked `forward` in `record/context.json`, but the provisioned
snapshot (`record/snapshots/2026-07-14.json`) already contains the event's
resolution, and far more:

- **Dec 05 2025** — "Petition for a writ of certiorari before judgment
  GRANTED."
- **Jan 30 2026** — set for argument April 1, 2026.
- **Apr 01 2026** — argued (SG D. John Sauer for petitioners; Cecillia Wang
  for respondents).
- **Jun 30 2026** — merits decision: "Adjudged to be AFFIRMED," Roberts,
  C.J., for the Court, joined by Sotomayor, Kagan, Barrett, and Jackson, JJ.

I did not retrieve any of this; it is the guaranteed-common input every
predictor in this fan-out reads. The event (`evt-petition-disposition`,
`resolved: false` in `event.yaml`) was in fact resolved on December 5, 2025,
roughly seven months before this run. Provisioning is supposed to refuse a
forward cell whose snapshot reads terminal; this one slipped through, so the
cell measures nothing about forecasting skill. I have flagged it in
`flags.json` (data-quality, warning) so the evaluation can discount it.
Given that the sanctioned baseline states the disposition outright, the honest
prediction is `granted` at near-certainty; pretending to uncertainty the input
does not contain would only corrupt calibration measurement in the other
direction.

## Counterfactual pre-decision analysis (as of the 12/5/2025 conference)

For whatever signal the cell retains, here is how the call looks from the
pre-decision record alone — everything below draws only on docket entries
that precede December 5, 2025, plus the provisioned brief-in-opposition text
and the committed statpack.

**The legal question.** Executive Order 14160 ("Protecting the Meaning and
Value of American Citizenship") denies birthright citizenship to U.S.-born
children of parents unlawfully or temporarily present. Respondents (a
certified nationwide class of affected children, represented by the ACLU and
NAACP LDF) obtained a classwide preliminary injunction in the District of New
Hampshire; the Solicitor General petitioned for **certiorari before judgment**
(filed Sept. 26, 2025), bypassing the pending First Circuit appeal
(No. 25-1861), with Trump v. Washington, No. 25-364, as a companion.

**The governing standard.** Sup. Ct. R. 11 reserves cert before judgment for
cases of "such imperative public importance as to justify deviation from
normal appellate practice." The base rate for modern discretionary cert
petitions overall is very low — the statpack's modern-cert section puts grants
at ~273 of ~8,270 resolved petitions, roughly **3.3%** — but this petition sat
about as far from the median petition as one can get:

- **The petitioner is the Solicitor General.** SG petitions are granted at
  dramatically higher rates than the population; the SG sought review of a
  ruling enjoining a flagship executive order.
- **Imperative public importance is conceded on all sides.** The scope of the
  Fourteenth Amendment's Citizenship Clause, the citizenship status of tens of
  thousands of newborns, and a nationwide classwide injunction against the
  President — the questions do not get bigger.
- **The Court had already engaged with this controversy** in Trump v. CASA
  (2025), which addressed universal-injunction remedies in these same EO
  challenges while leaving the merits unresolved — a strong signal the merits
  question was coming back.
- **The BIO does not really resist review.** The provisioned
  `brief-in-opposition.txt` (filed Oct. 29, 2025) argues the EO is flatly
  unconstitutional under United States v. Wong Kim Ark and the plain text of
  the Citizenship Clause, and primarily disputes the *vehicle* (cert before
  judgment rather than awaiting the First Circuit) — while acknowledging the
  importance of prompt, definitive resolution. When both sides effectively
  want the question settled, denial is improbable.
- **Docket mechanics signaled speed.** Petitioners waived the Rule 15.5
  14-day distribution wait (Nov. 4); the petition was distributed for the
  11/21/2025 conference, redistributed for 12/5/2025 — a single relist, the
  classic pre-grant pattern consistent with opinion-drafting or vote
  confirmation rather than trouble.
- **Extraordinary amicus attention at the petition stage** (dozens of briefs
  from states on both sides, members of Congress, bar associations, and
  scholars) — noisy but correlated with grants.

A pre-decision estimate on this record would be P(granted) ≈ 0.93–0.96, with
the residual mass mostly on "deny/hold in favor of the companion Washington
petition (25-364) as the lead vehicle" — which for this docket would read as
denial or hold, not on any view that the Court would leave the question
unreviewed. The realized grant (both petitions were granted and argued
together) confirms the direction.

**Why 0.99 and not 1.0 or 0.95:** the disposition is stated verbatim in the
provisioned snapshot, so the only residual uncertainty is snapshot corruption
or my misreading — small but not zero.

## Inputs used

- `record/snapshots/2026-07-14.json` (provisioned baseline; contains the
  disposition and full docket through June 30, 2026).
- `record/documents/brief-in-opposition.txt` (provisioned; 49 pp., not
  truncated) — vehicle-focused opposition, merits-forward.
- `record/context.json` (mode: forward), `events/evt-petition-disposition/event.yaml`.
- `metrics/statpack.md` — modern discretionary-cert base rates (committed
  roll-up; no corpus reads).

No votes are predicted: cert-stage vote tallies are not disclosed, and the
event's decision target is the disposition.
