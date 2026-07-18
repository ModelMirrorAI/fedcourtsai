# Karsjens v. Gandhi, No. 25-1321 — cert petition disposition

**Prediction: denied. P(grant, GVR included) = 0.015.**

## The case

Paid cert petition (docketed May 28, 2026, Term 2025) from the Eighth Circuit's
decision in *Karsjens v. Gandhi*, 164 F.4th 662 (8th Cir. 2026), the costs
endgame of the long-running Minnesota Sex Offender Program (MSOP) class action
filed in 2011. After the state defendants prevailed on all claims, the district
court (Frank, J.) denied their ~$838k bill of costs entirely, resting chiefly on
the plaintiffs' indigence (they are indefinitely civilly committed) and the
"potential chilling effect" of taxing costs against civil-rights plaintiffs. A
unanimous Eighth Circuit panel (Colloton, C.J., joined by Loken and Benton)
reversed, holding the district court abused its discretion by ignoring the
plaintiffs' own 2013 offer to split the Rule 706 court-appointed-expert fees
50/50, rejected the chilling-effect rationale under *Poe v. John Deere Co.*, and
— rather than remanding for further findings — directed entry of a cost award of
$366,461.96 against the named plaintiffs jointly and severally. Rehearing en
banc was denied February 25, 2026, with no noted dissent.

## Questions presented

1. Whether a court awarding costs under Fed. R. Civ. P. 54(d)(1) may consider
   the potential chilling effect on civil-rights litigants to reduce or deny
   costs to a prevailing party (petition alleges a 9th Cir. vs. 6th/8th Cir.
   split — *Stanley v. USC*, 178 F.3d 1069 (9th Cir. 1999) and *AMAE v.
   California*, 231 F.3d 572 (9th Cir. 2000) (en banc) vs. *Weever v. Toombs*
   (6th Cir. 1991) and *Poe* (8th Cir. 1982)).
2. Whether the Eighth Circuit exceeded its authority by finding disputed facts
   (ability to pay) itself and directing a specific award instead of remanding.

## Why denial is the strong call

**Base rates.** The committed statpack's modern discretionary-cert slice runs
~3% granted overall; paid petitions in Term 2025 grant at ~5.4% (IFP ~1.1%).
The relist-count cut shows the zero-relist bucket granting at only 0.8% — and
this petition sits pre-conference with zero relists. Eighth Circuit
originating-court petitions grant at ~3.3%.

**Case-specific negatives, each pushing well below the paid base rate:**

- **Respondent waived the right to respond** (June 26, 2026), and as of the
  snapshot the Court has not called for a response. The Court essentially never
  grants without at least a CFR; a grant here requires the compound path
  CFR → relist(s) → grant, each step low-probability from this posture.
- **Distributed July 1 for the September 28, 2026 long conference**, the
  highest-denial-density conference of the year.
- **Fourth cert petition from the same litigation; the prior three were all
  denied** (*Karsjens v. Piper*, 138 S. Ct. 106 (2017); *Karsjens v. Lourey*,
  142 S. Ct. 232 (2021); *Karsjens v. Harpstead*, 144 S. Ct. 814 (2024)) — the
  petition's own appendix and statement of related proceedings document this.
- **The split is real but old, shallow, and soft.** *Stanley* (1999) and *AMAE*
  (2000) vs. *Weever* (1991) and *Poe* (1982) have coexisted for a quarter
  century without the Court's intervention; the disagreement is over which
  factors a district court *may* weigh within Rule 54(d) discretion, reviewed
  for abuse of discretion — a discretionary-standard split the Court routinely
  leaves alone. And even the Eighth Circuit concedes indigence itself can
  justify denying costs (*Poe*), so the practical daylight between circuits is
  narrower than the QP frames it.
- **The decision below is heavily record-bound.** The panel turned on the
  plaintiffs' specific 2013 offer to split expert costs — an idiosyncratic fact
  that makes this a poor vehicle for the chilling-effect question, since the
  Eighth Circuit had an independent, case-specific ground.
- **QP2 is error correction.** "The court of appeals found facts instead of
  remanding" is a classic fact-bound misapplication claim (*Zenith*, *Anderson*,
  *June Medical*); the Court does not grant plenary review to police remand
  scope in a costs dispute. The Excessive Fines argument was never passed on
  below and is raised only inside a parenthetical.
- **No dissent below, no cert-stage amici on the docket, unanimous panel,
  rehearing denied without noted dissent** — no institutional signal of
  certworthiness. (The substantial 8th Circuit amicus support — ACLU, Impact
  Fund, etc. — shows the civil-rights bar's interest and leaves some room for
  cert-stage amici before conference, which is a modest upside tail.)

**Modest positives:** paid petition, experienced counsel of record, a genuinely
articulated split with a sympathetic-facts narrative ($366k joint-and-several
against indigent, indefinitely committed plaintiffs earning ~$5/hr after state
withholding), and a recurring issue the plaintiffs' bar cares about. That is
enough to put this above the generic zero-relist floor but not near the paid
average.

**No GVR path.** No intervening decision of this Court bears on Rule 54(d)
chilling-effect analysis; a GVR is not a realistic disposition here.

## Probability

Start from the paid-petition rate (~5%), discount hard for the respondent
waiver with no CFR yet, the long-conference distribution, the vehicle problems,
the softness of the split, and the litigation's 0-for-3 cert history; credit a
small tail for a possible CFR driven by cert-stage amici. **P(grant) ≈ 0.015;
predicted disposition: denied.** A denial with a statement or dissent from
denial (e.g., a justice writing on cost-shifting against indigent civil-rights
plaintiffs) is conceivable but still scores as denied.

## Inputs and caveats

Anchored on the provisioned snapshot
(`record/snapshots/2026-07-18.json`), the provisioned petition text and
questions-presented extract (no brief in opposition exists — respondent
waived), and the committed `metrics/statpack.md` / `metrics/statpack.json`
(paid vs. IFP grant rates, relist and circuit cuts). The statpack in this
checkout carries no salience-band table, so I anchored on the modern-cert,
fee-class, and relist cuts instead. The corpus query sidecar was unreachable
(`fedcourts query` / `open-events` timed out), so no corpus priors could be
pulled — a degraded but non-blocking input; see `retrieval.md`. Mode is
`forward`; the conference date (September 28, 2026) post-dates this run, so no
disposition exists to leak.
