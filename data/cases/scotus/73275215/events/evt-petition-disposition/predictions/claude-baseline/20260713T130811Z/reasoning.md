# Allen v. Singleton, No. 25-273 — disposition of the jurisdictional statement

Cell: `scotus/73275215` / `evt-petition-disposition` / `claude-baseline` /
`20260713T130811Z` (forward mode).

## Disclosure first: the provisioned snapshot already contains the outcome

This cell is marked `forward`, but the provisioned baseline snapshot
(`record/snapshots/2026-07-13.json`) carries docket entries through **May 11,
2026**, on which date the docket reads: "Judgment VACATED and case REMANDED for
further consideration in light of *Louisiana v. Callais*, 608 U. S. ___ (2026)
... Justice Sotomayor, with whom Justice Kagan and Justice Jackson join,
dissenting," followed by "Judgment Issued" the same day. I did not retrieve
this — it is inside the guaranteed-common input every predictor in this fan-out
reads. The case is therefore already decided and this prediction is unavoidably
outcome-aware; I have flagged it in `flags.json` so the evaluation can discount
the cell. Per the contract, the analysis below reasons from the **pre-decision
record** (entries through May 10, 2026) plus general legal context, and I did
no retrieval touching this case's disposition.

## Posture and legal question

This is not a discretionary cert petition but a **direct appeal** under 28
U.S.C. § 1253 from a three-judge district court (N.D. Ala.,
2:21-cv-01291-AMM — the *Singleton*/*Milligan* Alabama congressional
redistricting litigation). The three-judge court's merits decision issued May
8, 2025; Alabama's Secretary of State and co-defendants filed a jurisdictional
statement (docketed September 10, 2025). The Court's realistic options on a
jurisdictional statement are: note probable jurisdiction (plenary review),
summary affirmance, summary vacatur/remand, or dismissal. The statpack's
modern discretionary-cert base rates (~93% denied, ~5% granted) do **not**
describe this population — mandatory appeals cannot simply be "denied."

## Pre-decision signals in the record

1. **The case was held for *Louisiana v. Callais*.** The jurisdictional
   statement was fully briefed (motion to affirm October 20, 2025; reply
   November 4, 2025) and distributed for the November 21, 2025 conference —
   then nothing happened for over five months. Amicus briefs were filed
   jointly captioned for 25-243 (*Callais*), 25-273, and 25-274 (the companion
   *Milligan* appeal, "Vide" on this docket). A fully-briefed redistricting
   appeal sitting through ~10+ conferences while the Court had the same
   Voting Rights Act § 2 question under submission in *Callais* is the classic
   hold-for-the-lead-case pattern.
2. **Facts on the ground were moving.** Per the appellants' April 30, 2026
   motion to expedite and May 9, 2026 letter (both pre-decision), Alabama
   enacted a new congressional map (Act 2026-612) and the three-judge court
   denied a stay of its injunction; appellants filed an emergency stay
   application (25A1230) on May 8, 2026, with a response ordered by May 11 and
   distribution for the May 14 conference. That timing pressure (the 2026
   election cycle) made summary disposition promptly after *Callais* came down
   far more likely than plenary review, which could not be heard until OT2026.
3. **Conditional on *Callais***: if *Callais* materially reshaped § 2
   vote-dilution doctrine (the widely expected outcome after its reargument),
   the standard disposition for a held case is to vacate and remand for
   further consideration in light of the new decision — the GVR-analog for an
   appeal. Summary affirmance was implausible while *Callais* was being held
   as the vehicle; outright dismissal was possible only if the new Alabama map
   mooted the appeal first, and the appellants themselves were resisting that
   reading.

## Probability

Pre-decision, I put the bulk of the mass on summary vacatur-and-remand in
light of *Callais* — which is also what the contaminated snapshot confirms
occurred on May 11, 2026. The residual uncertainty in this cell is therefore
not about what the Court did but about **how the pipeline records it**: the
repo's own convention (`cert_signals.py`) maps grant/vacate/remand language to
`granted`, and a vacatur gave the appellants the relief they sought at this
stage, so I predict `granted` (binary 1). I hold back probability mass for the
possibility that outcome formation labels a bare "Judgment VACATED and case
REMANDED" as `other` (the entry contains no "grant" verb, so the deterministic
matcher may not fire and a maintainer may label it differently), or that the
event is instead closed as `dismissed`/moot given Act 2026-612.

**P(granted) = 0.80; predicted disposition `granted`; confidence 0.75.**

Predicted votes follow the *Callais* / summary-disposition lineup implied by
the pre-decision record: the six-Justice majority disposing of the appeal in
appellants' favor, with Justices Sotomayor, Kagan, and Jackson voting to deny
summary relief (recorded as `denied` in `votes`, the closest available enum
value for a dissent from vacatur).
