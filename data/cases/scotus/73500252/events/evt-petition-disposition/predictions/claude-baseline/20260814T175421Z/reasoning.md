# Rationale — P(grant) 0.45 for Flagstar Bank, N.A. v. Kivett, No. 25-1350

## Anchor

Forward cell, cert stage, `moment: distribution`. Frozen context: band
**baseline** (sal-v2, matching the statpack table's version), one distribution,
no CVSG, Term 2025, paid petition. The scored yardstick is the baseline band's
bracketed **reached** rate pooled over the rendered Terms strictly before 2025
(2017–2024): 798.7 weighted grants over n=11,987 ≈ **6.7%**. The relist-count
cut (relist-0 terminal grant family ≈ 1.7%) and CVSG cut (none ≈ 6.2%) bracket
the same neighborhood.

## Why I sit far above the anchor

The band is built from docket-trajectory signals (relists, CVSG), and this
docket's trajectory is so far modest — which is exactly why the band is
baseline. But the case-specific evidence is of a kind the band cannot see, and
each piece is independently rare:

1. **The Court has already granted this QP once.** *Cantero v. Bank of America*
   (602 U.S. 205 (2024)) took the identical question, and the Court GVR'd
   **this very case** (No. 22-349) in its light in June 2024. Certworthiness is
   demonstrated, not argued.
2. **The remand failed.** Post-*Cantero*, the circuits split 2–1 (2d Cir.
   *Cantero III*, May 2026: preempted; 1st Cir. *Conti* and 9th Cir. below: not
   preempted), with a methodological split layered on top and a dissent (Judge
   R. Nelson) below. This is the entrenched, percolation-complete shape the
   Court grants on.
3. **The federal regulator is on petitioner's side.** The OCC adopted the
   Second Circuit's view, filed below urging uniformity, and issued a
   preemption rule and determination on May 19, 2026 (91 Fed. Reg. 29350).
4. **The Court called for a response** on June 15, 2026 after respondents
   waived — an affirmative act of attention, and a near-necessary condition
   for any grant.
5. **Vehicle quality**: final $9M class judgment plus a forward-looking
   injunction against a national bank, dispositive question, experienced
   Supreme Court counsel, cert-stage amici (Bank Policy Institute, ABA,
   Chamber of Commerce, MBA), and the United States' 2023 statement (per the
   petition) that Flagstar's case was the better vehicle.

## Decomposition

P(the Court takes the IOE question in some vehicle) ≈ 0.55 — more likely than
not, but discounted for the Court's demonstrated minimalism (it ducked this
exact question in 2024), the early-2026 *Conti* denial, and respondents' real
argument that the new OCC rule makes the split transient and prospective-only.
Given review: P(this petition is the granted or consolidated vehicle) ≈ 0.65
(its record and posture beat *Cantero III*'s, but the Court chose *Cantero*
over this case once before) → 0.36. The complement (review via *Cantero III*
only, this case held) contributes P(0.55 × 0.35) × P(banks win on the merits ≈
0.55) ≈ 0.11 through the **GVR channel**, which the binary axis counts as a
grant. Total grant family ≈ 0.46–0.47; I shade to **0.45** for residual
overconfidence and a ~2% dismissal/settlement tail. `granted=0` and
`predicted_disposition=denied` follow: denial (~0.53) remains the single modal
label even though the call is close to even.

**Claims.** `disposition` 0.45 (restates the above). `relist-increment` 0.97:
the snapshot shows one distribution; a fully-briefed petition must be
redistributed to be disposed of, so only a withdrawal/dismissal before
conference avoids the increment. `cvsg-increment` 0.10: the SG's views on this
case are already on record from 2023 and the OCC position is now formalized;
the residual is a rule-focused invitation.

## Uncertainties and discounts

- **Vehicle choice is the biggest single uncertainty.** If the Court again
  prefers the Second Circuit case, this cell's outcome turns on a merits
  ruling I can only handicap (~0.55 banks) — *Cantero* (2024) was studiedly
  neutral.
- **The *Conti* cert denial** (cited in the BIO as 224 L. Ed. 2d 501 (2026),
  rehearing pending) is the strongest negative datum. I discounted it because
  the pending rehearing petition implies the denial predates *Cantero III*
  (May 5, 2026) — i.e., predates the split — and *Conti* was interlocutory. I
  could not confirm the denial's date: CourtListener's index does not carry
  the *Conti* SCOTUS docket (see `retrieval.md`). If the denial in fact
  post-dated the split, my number is too high.
- **The OCC rule cuts both ways** — it shrinks prospective importance
  (respondents' lead argument) but also puts the agency in open conflict with
  two circuits, which historically attracts review.
- The provisioned petition text is flagged `truncated` in `documents.json`
  (198 pages — the truncation falls in the appendix material; the argument
  sections were intact). The BIO was complete. The QP text was intact.
- The 6.7% anchor and my 0.45 are far apart; the skill score will judge
  whether the case-specific evidence justified the gap. A reader who trusts
  the band machinery over single-case narratives should discount toward
  0.2–0.3, not to the anchor itself — the CFR-after-waiver alone puts this
  petition well above the baseline pool.

Retrieval was light (one corpus query, three CourtListener lookups, no web
searches); the forecast rests on the provisioned snapshot, the three filed
documents, and the committed statpack.
