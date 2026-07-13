# Allen v. Milligan (No. 25-274) — disposition of the jurisdictional statement

## Disclosure first: the outcome is visible in the provisioned baseline

This cell is provisioned in `forward` mode with `resolved: false`, but the
guaranteed-common input — the 2026-07-13 snapshot — already records the
disposition on its face. The May 11, 2026 proceedings entries read:

> "Judgment VACATED and case REMANDED for further consideration in light of
> *Louisiana v. Callais*, 608 U.S. ___ (2026). The judgment will be issued
> forthwith pursuant to Rule 45.3. Justice Sotomayor, with whom Justice Kagan
> and Justice Jackson join, dissenting."

followed by "Judgment Issued" the same day. I did not retrieve this; it was in
the baseline every predictor in this fan-out reads. Per the contract I disclose
it here and in `flags.json` (so the evaluation can discount the cell), and the
analysis below reasons from the **pre-decision record only** — everything on
the docket strictly before the May 11, 2026 disposition entries.

## The case and the question

This is not an ordinary cert petition. It is a **direct appeal under
28 U.S.C. § 1253** from a final judgment of a three-judge district court
(N.D. Ala., 2:21-cv-01530 — the *Milligan* congressional-redistricting
litigation), decided below on May 8, 2025. Alabama's Secretary of State and
co-appellants filed a jurisdictional statement (docketed September 10, 2025)
challenging the three-judge court's judgment imposing a remedial congressional
map under Section 2 of the Voting Rights Act. The event asks how the Court
disposes of that jurisdictional statement.

Because § 1253 jurisdiction is mandatory, "deny" is not on the menu the way it
is for certiorari: the realistic dispositions are (a) note probable
jurisdiction and set for plenary review, (b) summarily affirm, (c) dismiss for
want of a substantial federal question, or (d) vacate and remand in light of an
intervening decision (the appeal analog of a GVR).

## What the pre-decision record shows

- **The case was being held for *Louisiana v. Callais*.** The jurisdictional
  statement was fully briefed by November 4, 2025 (motion to affirm filed by
  the Milligan appellees October 20; appellants' reply November 4) and
  distributed for the November 21, 2025 conference — after which the docket
  goes silent for over five months. A fully briefed, high-profile appeal
  sitting undecided through the winter and spring is the classic signature of
  a hold for a pending merits case. *Callais* — the Louisiana congressional
  redistricting case presenting whether intentionally race-based remedial
  districting under § 2 is constitutional — was pending on the merits over
  exactly that period, and this docket's amicus lineup (Louisiana itself, North
  Dakota, RITE, Project on Fair Representation) confirms the two cases travel
  together. The docket is linked with No. 25-273 (*Singleton*, the companion
  Alabama appeal), and the stay application 25A110/25A1231 chain runs through
  Justice Thomas as circuit justice.
- **The endgame accelerated in spring 2026.** Alabama moved on April 30, 2026
  to expedite consideration of the jurisdictional statement (election-calendar
  pressure: the docket shows Alabama enacted a new map, Act 2026-612, and the
  three-judge court denied a stay), filed an emergency stay application on
  May 8, 2026 (25A1231), and the case was distributed for the May 14, 2026
  conference. The Court granted the motion to expedite on May 11.

## Prediction

For a case held pending a lead merits case, the Court's near-uniform practice
once the lead case comes down is to **vacate and remand for further
consideration in light of** the new decision rather than resolve the held case
itself — especially where, as here, the held case arrives on mandatory appeal
from a fact-bound three-judge-court judgment and the intervening decision
reworks the governing framework. The expedite grant and the election-clock
posture make summary disposition (rather than plenary review in OT2026) the
most likely vehicle, and a *Callais*-keyed vacate-and-remand the most likely
form.

In this repo's disposition vocabulary, a GVR/vacate-and-remand lands on the
**granted** side (see `src/fedcourtsai/pipeline/cert_signals.py` — the GVR
patterns map to `Disposition.granted`; `historical.py` counts "grants and
GVRs" together). Noting probable jurisdiction — the main alternative — would
also land on the granted side. The residual mass is summary affirmance or a
dismissal-style disposition, which would map to `other`/`dismissed`.

- **P(granted-side disposition) = 0.85** (≈0.65 GVR-in-light-of-*Callais*,
  ≈0.20 note probable jurisdiction / plenary grant), predicted_disposition
  **granted**, granted = 1.
- Remaining ≈0.15: summary affirmance (~0.10, plausible only if *Callais*
  left the § 2 framework intact) or dismissal/other (~0.05).
- **Confidence 0.6**: the legal-posture analysis is strong, but the cell is
  contaminated (outcome visible in the baseline) and there is genuine label
  ambiguity in how the pipeline will latch a vacate-and-remand order that,
  unlike a cert GVR, contains no "grant" language.

The statpack's modern-cert base rate (grants a few percent, denials ~93%) is
the wrong prior for this cell and I discount it almost entirely: this is a
mandatory-jurisdiction appeal, already fully briefed, held for a decided lead
case, with an expedite motion granted — each of which moves the case far from
the discretionary-cert population the statpack describes.

No per-justice votes are predicted: the only vote information I have comes
from the outcome-revealing docket entry itself, and a "prediction" copied from
it would not be a prediction.

## Inputs used

- Provisioned snapshot `record/snapshots/2026-07-13.json` (the baseline; no
  `record/documents/` were provisioned for this cell).
- Event definition `events/evt-petition-disposition/event.yaml`.
- `metrics/statpack.md` (base rates — considered and discounted, see above).
- `fedcourts query` corpus priors (see `retrieval.md`) — recent SCOTUS grants
  for context; none were on-point for a held three-judge-court appeal.
