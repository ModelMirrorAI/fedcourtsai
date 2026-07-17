# Gator's Custom Guns, Inc. v. Washington (No. 25-153) — cert disposition

## The question presented

Petitioners challenge Washington's ban on the manufacture, import, distribution,
and sale of ammunition-feeding devices holding more than ten rounds (a
sales-side ban, broader than most states' possession bans). The Washington
Supreme Court upheld the law 7-2 (May 8, 2025), reasoning that such magazines
are "accessories," not "Arms," and therefore outside the Second Amendment's
plain text. The QP is whether magazines over ten rounds are "Arms"
presumptively protected under the Second Amendment — the same threshold
plain-text move used by the Seventh Circuit in *Bevis* and the Ninth Circuit
en banc in *Duncan v. Bonta* to sustain hardware bans.

No filed-document text was provisioned for this cell (`record/documents/` is
absent), so the QP characterization above rests on the docket snapshot plus
public reporting on the petition (SCOTUSblog case page, State Court Report
tracker) retrieved in forward mode.

## What the docket shows (snapshot of 2026-07-17)

- Paid petition, Term 2025, docketed Aug 8, 2025. Counsel of record is Erin
  Murphy (Clement & Murphy) — elite SCOTUS counsel.
- Washington initially **waived** response; the Court **requested a response**
  (Sept 4, 2025) — a screening signal that at least one chamber is engaged.
- Cert-stage amici from ~25 states (Montana et al.), the NRA, NSSF, and NAGR.
- First distributed for the Dec 5, 2025 conference, then **redistributed to
  roughly twenty consecutive conferences** through June 29, 2026 — a serial
  relist far beyond the "3+" bucket, and the case was **not** denied at the
  term-end clean-up conference; it carries over to next Term.
- Supplemental briefing tracked *Benson v. United States*: a D.C. Court of
  Appeals panel struck D.C.'s 10-round magazine limit (Mar 5, 2026), which
  petitioners raised as a split-deepening development; Washington answered
  (Apr 23, 2026) that the panel opinion was vacated when en banc rehearing was
  granted (Apr 22, 2026) — so that split evaporated, which helps explain the
  continued holds rather than a grant.

## The decisive forward signal

In July 2026 (reported the week of this snapshot) the Court **granted
certiorari in *Viramontes v. Cook County* (7th Cir.) consolidated with
*Grant v. Higgins* (2d Cir.)** — the AR-15/"assault weapons" ban cases —
for argument in fall 2026, decision expected by June 2027. Those bans are
defined partly by capacity to accept large-capacity magazines, and the granted
question (whether commonly possessed semiautomatic rifles are protected
"Arms") squarely overlaps the threshold "Arms"/plain-text holding below in
this case. Critically, at the same term-end window the Court **held Gator's
and Duncan v. Bonta over** rather than denying them — the opposite of what it
did in June 2025, when it denied *Snope v. Brown* and *Ocean State Tactical*
outright after ~15 relists with no lead case granted. The natural reading:
the magazine petitions are now being carried for the AWB merits decision.

## How this cashes out

The post-*Bruen* pattern is the template: when the Court decided *Bruen* it
GVR'd the held hardware-ban petitions (*Duncan*, *Bianchi*, *ANJRPC*) en
masse. Conditional paths:

1. **Petitioners prevail in Viramontes/Grant** (the grant itself, after years
   of ducking, plus *Snope*'s three noted dissents and Kavanaugh's "soon"
   statement, make reversal the likelier outcome — I put this at ~0.70-0.75).
   A holding that common-use hardware is presumptively protected "Arms" guts
   the Washington Supreme Court's "accessories, not Arms" rationale, and a
   **GVR of Gator's is near-automatic** (~0.90+ conditional). A plenary grant
   of the magazine question (with *Duncan* the likelier lead vehicle) is the
   main alternative — still a grant on the binary axis.
2. **Government prevails or the Court rules narrowly** (~0.25-0.30): the
   magazine cases most likely go the way of *Snope* — denial with dissents.
   A residual chance (~0.15 conditional) the Court still takes magazines
   separately, since magazines-in-common-use is analytically distinct from
   "M16-like rifles."

Blending: P(any grant, GVR included) ≈ 0.72 × 0.92 + 0.28 × 0.15 ≈ **0.68**.

Base-rate anchors from the committed statpack: modern paid petitions grant at
~5.4% (Term 2025 paid class); the 3+-relist bucket grants at ~21.8%. This
case sits far above both anchors — ~20 relists, requested response, elite
counsel, 25+ state amici, and, decisively, survival past a clean-up
conference at which a companion presenting the shared threshold question was
granted. The 0.68 figure is a large upward adjustment from the relist-bucket
base rate, justified by the hold-for-lead-case posture, and discounted for
the real path where the AWB ruling goes against challengers and this
petition is denied.

**Most likely single disposition: `gvr`** — held for *Viramontes/Grant*, then
granted, vacated, and remanded in light of the decision (expected by June
2027). Plenary grant is possible but the Court more often GVRs the trailing
vehicles and lets the lead case do the work; if it wants the magazine
question itself, *Duncan* (a possession ban, with a takings question) is the
more comprehensive vehicle, with Gator's again GVR'd. Hence `granted=1`,
`probability=0.68`, `predicted_disposition=gvr`.

No per-justice votes predicted: a GVR issues per curiam and a denial records
no votes; individual noted dissents are not meaningfully predictable here.

## Big-case score

0.75. Stakes are high independent of the odds: magazine-capacity limits exist
in roughly 14 states, the case is tracked by SCOTUSblog, state AGs (25+ as
amici), and every major gun-rights organization, and it travels with the
highest-profile Second Amendment grant since *Bruen*. It is scored below the
lead AWB cases themselves only because its likeliest disposition is a
companion GVR rather than a landmark merits opinion of its own.

## Leakage note

This is a **forward** cell and the petition is genuinely undecided as of the
snapshot (held over to next Term; confirmed undisposed by public reporting
contemporaneous with the snapshot). The *Viramontes/Grant* cert grant and the
*Benson* en banc vacatur are companion-case developments predating/
contemporaneous with the snapshot — legitimate forward signal under the
leakage doctrine, noted in `flags.json` because they are decisive to the
forecast. No information about this petition's own disposition exists or was
used.
