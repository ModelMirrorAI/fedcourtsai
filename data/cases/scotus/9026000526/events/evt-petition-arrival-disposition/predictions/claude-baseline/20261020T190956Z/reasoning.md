# Reasoning — P(grant) 0.035

**Inputs read.** Snapshot `record/snapshots/2026-10-21.json` (docketed Oct 20,
2026; paid; petition filed Oct 13 after a 26A324 extension; response due
Nov 19; no distributions); `record/context.json` (forward mode, band
`baseline` under sal-v4, distribution_count 0, no CVSG, Term 2026);
`record/documents/questions-presented.txt` and `petition.txt` (93 pp., not
truncated). No brief in opposition exists yet.

**Anchor.** This is an arrival-moment cert cell. The frozen band is
`baseline`, and the caption class is private (an individual criminal
defendant petitioning against a State — the State is the respondent, not the
petitioner), so `baseline`'s floor is the right anchor either way. From
`metrics/statpack.md`, *Segment base rate by salience band (sal-v4)*, pooling
the bracketed `reached` figure for `baseline` over Terms 2017–2025 (strictly
before OT2026; the table renders 10 of 10 Terms) gives ≈ **5.0%**
(n ≈ 12,900 weighted). OT2026's own row (n=146) is excluded as not strictly prior.

**Adjustments.**
- *Down:* The merits look weak for petitioner. On the petition's own account
  the trial court removed the case from the jury because the complainant's
  refusal to appear violated petitioner's compulsory-process / due-process
  rights — a ground the State court characterized as a dismissal unrelated to
  factual guilt. Evans v. Michigan and Scott draw exactly that line
  (procedural dismissals are not acquittals), so the decision below looks like
  a routine application rather than a conflict with this Court's cases.
- *Down:* The asserted split is a set of older state-court decisions
  described as differing "approaches" to mixed rulings, not a crisp,
  acknowledged conflict on the QP. Counsel is a small Mississippi firm, not
  the Supreme Court bar. The Mississippi Supreme Court granted and then
  dismissed its own writ, which leaves a fact-bound record.
- *Down (minor):* Interlocutory posture (retrial set for March 2027). Double
  Jeopardy claims are reviewable before retrial, so this is not a
  jurisdictional bar, but it does not help the vehicle.
- *Up (minor):* The Court of Appeals was closely divided en banc (four
  dissents, four votes to rehear). The Court takes Double Jeopardy acquittal
  cases from state courts now and then (Evans, McElrath, Smith v.
  Massachusetts), and the "a label doesn't control" framing has some appeal.

Net: a bit below the floor, **0.035**.

**Other claims.**
- `relist-increment` 0.96: at zero distributions, the question is whether it is
  ever distributed. Nearly every paid petition reaches conference; the
  residual is withdrawal or a very long delay past the resolution clock.
- `cvsg-increment` 0.005: a state criminal case with no federal interest.
- `summary-disposition-route` 0.20 (conditional on a grant): a grant here
  would plausibly be a summary reversal applying Evans if the Court read the
  ruling as an acquittal; plenary review is still likelier.
- `dissent-from-denial` 0.04: separate writings on paid-docket denials are
  rare; nothing here strongly attracts one.

**Uncertainty.** I read the Court of Appeals opinion only through the
petition's characterization. If the trial court's ruling actually rested on
evidentiary insufficiency (the complainant's absence made proof of intent
impossible), petitioner's Evans argument is stronger than I credit. I did no
live retrieval, so I have not checked whether Mississippi will respond or
whether amici are lining up.
