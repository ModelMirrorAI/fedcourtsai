# Aldridge v. Regions Bank (No. 25-590) — cert disposition prediction

**Prediction: deny is likelier than grant, but this is a genuinely live petition.
P(grant, GVR included) = 0.25; predicted disposition: denied.**

## The case

Former Ruby Tuesday executives (participants in two "top-hat" deferred-compensation
plans backed by a rabbi trust administered by Regions Bank) lost millions when Ruby
Tuesday went bankrupt in 2020. They sued Regions under ERISA § 502(a)(3),
29 U.S.C. § 1132(a)(3), seeking equitable **surcharge**, plus Alabama-law
trust/contract claims. The Sixth Circuit (Judge Murphy, 144 F.4th 828, July 17,
2025) affirmed dismissal on both fronts: surcharge is not "appropriate equitable
relief" under Mertens/Great-West/Montanile (siding with the Fourth Circuit's *Rose
v. PSA Airlines*, 80 F.4th 488), and the state-law claims are expressly preempted
under § 1144(a) even though top-hat plans are exempt from ERISA's fiduciary duties.

The questions presented: (1) whether a § 502(a)(3) plaintiff may seek surcharge, the
remedy *CIGNA Corp. v. Amara*, 563 U.S. 421, 441–42 (2011), described as
"exclusively equitable"; and (2) if not, whether state-law claims on a separate,
non-plan-required contract are nonetheless preempted, leaving no remedy at all.

## Grant-side signals (strong)

- **CVSG.** On April 6, 2026, the Court invited the Solicitor General's views. This
  is the dominant docket signal: in the corpus statpack's CVSG cut, CVSG'd petitions
  grant at **27.1%** (vs. 3.0% for non-CVSG'd), and a CVSG means the Court has
  already looked past the BIO once without denying.
- **A real, acknowledged split.** Six circuits (2d, 5th, 7th, 8th, 9th, 11th) read
  Amara to authorize surcharge; the Fourth (*Rose*, 2023) and now the Sixth (this
  case) reject it as Amara dicta inconsistent with Mertens and Montanile. The Fifth
  Circuit's *Aramark Servs. v. Aetna*, 162 F.4th 532 (5th Cir. 2025), reaffirmed the
  surcharge side *post-Montanile* — undercutting the BIO's core "every pro-surcharge
  case predates or ignores Montanile" argument and making the conflict fresh, not
  stale. The split has deepened since the Court denied *Rose* (144 S. Ct. 1346
  (2024)).
- **Docket trajectory.** Respondent waived; the Court **requested a response**
  (Dec. 29, 2025) — meaning at least one chamber flagged the petition — then CVSG'd
  after the first conference. Petition is paid, counseled by the UVA Supreme Court
  Litigation Clinic against Gregory Garre for respondent, with a cert-stage amicus
  from Prof. Samuel Bray, the leading remedies scholar the petition itself relies on.
- **Importance.** The scope of § 502(a)(3) relief recurs constantly; the
  no-federal-remedy-plus-preemption squeeze the petition highlights is exactly the
  kind of remedial-gap problem the Court has repeatedly been urged to fix since
  Amara.

## Deny-side signals (also strong — the vehicle problem)

The BIO's vehicle attack is unusually substantive, not boilerplate:

1. **Regions is an ERISA non-fiduciary.** Top-hat plans are statutorily exempt from
   ERISA's fiduciary duties, 29 U.S.C. § 1101(a)(1). Every circuit on the
   pro-surcharge side of the split allows surcharge only **against fiduciaries** —
   *Aramark* expressly drew the fiduciary/non-fiduciary line, and even Judge
   Heytens's *Rose* dissent rested on fiduciary status. So arguably *no* circuit
   would rule for these petitioners on QP1, meaning the split may not be outcome-
   dispositive here.
2. **Antecedent liability hole.** The Sixth Circuit said it was "far from clear"
   petitioners even alleged a violation of ERISA or plan terms (their claims sound
   in the rabbi-trust agreement, not the plans). The Court would risk an advisory
   answer on remedies in a case that may fail on liability.
3. **Rose was denied in 2024** on materially the same QP1, in a sympathetic,
   cleaner (fiduciary-adjacent) posture.
4. ***Aramark* itself is a cleaner vehicle** (an undisputed fiduciary defendant),
   and its en banc petition was still pending in the Fifth Circuit as of the last
   docketed entries (Feb. 2026). The SG can — and I expect will — say "the split is
   real but this top-hat/non-fiduciary case is the wrong car," possibly flagging
   Aramark or a successor.

QP2 (preemption) has no alleged circuit conflict and is unlikely to drive a grant
standing alone, though the "no remedy anywhere" squeeze gives it equitable force.

## Weighing

The CVSG bucket's 27.1% grant rate is the right anchor: it already conditions on
the Court's demonstrated interest, and this petition's quality signals (paid,
requested response, expert counsel, scholarly amicus, deepened split) are typical
of that bucket rather than above it. I adjust modestly **down** from the anchor
because the vehicle defects here are worse than the CVSG-case average — the
non-fiduciary/top-hat posture gives the SG and the Court an easy off-ramp that
preserves the question for *Aramark* or a successor, and the Court passed on this
exact QP in *Rose* two years ago. I adjust slightly back **up** for the reality
that the remedial-gap framing (QP1 + QP2 together: no federal remedy *and* no state
remedy) is more arresting than Rose's posture, and DOL has historically defended
surcharge's availability, so a grant-recommending SG brief is far from impossible.

Net: **P(grant) ≈ 0.25**, so the single likeliest disposition is **denied**
(≈ 0.72, with ~0.03 residual for dismissal/other). A GVR is implausible — there is
no intervening decision to GVR against (if the Fifth Circuit's en banc process or a
grant in another surcharge case intervened, the calculus would change, which is
part of why the grant tail is fat). Timing note: with the SG's brief unlikely
before late 2026, the disposition will probably not land until OT2026
(winter/spring 2027).

## Sources used

Provisioned snapshot (`record/snapshots/2026-07-16.json`), the petition's QP
section and full petition text, and the 40-page BIO (all provisioned under
`record/documents/`); the committed corpus statpack (`metrics/statpack.md`) for
the modern-cert, CVSG, relist, circuit, and fee-class base rates; CourtListener
MCP for the docket's live status (still pending, not terminated — confirming the
forward cell is correctly provisioned) and the Fifth Circuit *Aramark* en banc
docket status. Details in `retrieval.md`. No outcome-revealing material was
encountered — the petition remains pending.
