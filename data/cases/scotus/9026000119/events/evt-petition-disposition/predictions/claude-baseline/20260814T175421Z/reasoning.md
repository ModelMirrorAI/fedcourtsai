# Reasoning — Guam v. Ybanez, No. 26-119 (claude-baseline, 20260814T175421Z)

**P(grant family) = 0.07; predicted disposition: denied.**

## Anchor

`record/context.json` freezes my conditioning: `forward` mode, band `state`
under `sal-v2`, `distribution_count` 0, no CVSG, Term 2026. Per the contract I
anchor on the **state band's bracketed `reached` rate** from the statpack's
"Segment base rate by salience band (sal-v2)" table, pooled over the rendered
Terms strictly before this case's (2017–2025): roughly **36%**
(≈507/1,410 weighted). That is the rate among paid petitions that ever reached
the state band, which is this cell's population and the yardstick my skill is
scored against.

## Adjustments — all downward, and large

The state band's ~36% is dominated by government petitioners with the classic
grant profile: a real split, strong counsel, a clean vehicle. This petition
has none of those:

1. **No split — the petition concedes it.** Its own theory is that federal law
   on office-wide prosecutor disqualification is "uniformly settled" in the
   circuits and should be *extended* to state and territorial courts. A
   request to extend, not to resolve a conflict, is the weakest cert posture,
   and the cited authority (*U.S. v. Bolden*, CA10) is supervisory
   circuit law, not a holding of the Court that the Guam Supreme Court defied.
2. **Doctrinally hostile core theory.** The due-process claim is asserted on
   behalf of "the People of Guam" — a government entity. The Court's
   long-standing position is that a government is not a "person" entitled to
   due process against itself (cf. *South Carolina v. Katzenbach*); the
   petition's *Heller*-based reading of "the People" does not engage that
   problem.
3. **Vehicle problems.** The orders below are unreported; the underlying
   disqualification rests on a *found* GRPC 1.7 conflict of interest that the
   petition never really confronts; and the dismissal below was for violating
   the defendants' statutory speedy-trial rights — unsympathetic
   error-correction material.
4. **Execution.** The petition is weak as advocacy (it cites the Court's own
   FAQ page for the grant rate, styles the office "Attorney Generals," and
   raises the "People" definitional point as a freestanding reason to grant).
5. **Track record of the court below.** Petitions from the Supreme Court of
   Guam are almost never granted — CourtListener shows a string of denials
   (*Moylan v. Guam* (2011), *Quinata*, *Ilagan*, *Enriquez* (×2)) against one
   modern grant, *Limtiaco v. Camacho* (2007).
6. **The "evades review" premise is overstated.** The AG's own collateral
   attack is already pending in the District Court of Guam (*Moylan v. Supreme
   Court of Guam* / *AG of Guam v. Supreme Court of Guam*, 1:26-cv-00007/-08/-09,
   filed March 24–25, 2026 — public filings predating my snapshot). A live
   alternative federal forum further reduces the pressure to grant.

## Why not lower

Two considerations keep me at 7% rather than the 1–2% a generic weak paid
petition would get. First, the structural claim is genuinely striking: a
territorial supreme court extinguished a public-corruption prosecution by
disqualifying the *only* constitutionally and statutorily authorized
prosecutor, with no substitute mechanism, and has already applied the ruling
to a second case (CRA24-023). The Court is the only appellate reviewer of the
Guam Supreme Court, so the no-split logic carries less force than usual — that
is exactly the posture in which *Limtiaco* was granted on an Organic Act
question. Second, the petitioner is a government, and government petitioners
in the corpus (the state band) run far above baseline even when I discount
this one's specifics.

## Claims

- `disposition` 0.07 — restates the number above.
- `relist-increment` 0.97 — the docket shows **zero distributions**; this
  resolves true if the petition is ever distributed at all, which happens to
  essentially every paid petition that is not withdrawn or dismissed
  pre-conference. Response due August 26, 2026; first distribution expected
  for the late-September 2026 long conference.
- `cvsg-increment` 0.02 — slightly above the ~1.3% unconditional paid-segment
  rate for the federal-structure angle, held down by the petition's weakness.

## Uncertainties and discounts

- I read the petition and QP text; **no brief in opposition exists yet**
  (response due August 26, 2026), so I cannot see the waiver-vs-oppose choice
  or the respondents' framing. My read of the conflict-of-interest merits is
  from the petition's own appendices (the orders below are attached), which
  soften the petitioner's telling but are still a one-sided record.
- The statpack's state-band `reached` denominators are modest (n≈1,410 pooled)
  and the band pools true states with territories; if territorial petitioners
  systematically underperform the band, my 7% is generous.
- I know from training data that the Guam AG's office and this dispute have
  had public visibility; I do not know this petition's outcome (it does not
  exist yet — forward cell) and retrieved nothing postdating the snapshot
  about this case's disposition.
