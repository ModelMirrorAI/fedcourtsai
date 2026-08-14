# Rationale for the numbers

**P(grant) = 0.07.**

**Anchor.** My context freezes `band: elevated` under `sal-v2`, matching the
statpack's segment table version, so the yardstick is the elevated band's
bracketed `reached` rate. Pooling the Term rows the table renders that precede
this case's Term (OT2017–OT2024): weighted grants ≈ 686 over n ≈ 3411, a pooled
**reached rate of ~20.1%** (per-Term range 17.3%–22.0%; OT2025's own row, which
I do not pool, reads 17.6%). That is the rate for a paid petition that has
reached the elevated band, and the baseline my skill is scored against.

**Adjustments down — substantial, to 0.07.**

1. *The frozen trajectory overstates this docket.* `distribution_count: 2`
   counts the May 26 distribution of sealing motion 25M86 (conference
   6/11/2026) alongside the petition's single distribution (June 24, for the
   9/28/2026 long conference, not yet held). The petition has never actually
   been considered at a conference, let alone relisted. A genuine
   twice-distributed petition is a materially stronger animal than this one;
   the elevated band is partly an artifact of the motion practice. (Flagged in
   `flags.json`.)
2. *Waived response, no CFR.* Vizient waived on June 22 and the Court has not
   requested a response. No grant can happen from this state without a CFR and
   redistribution, so the grant probability is bounded by
   P(CFR) × P(grant | CFR-path) ≈ 0.25–0.30 × ~0.2–0.25 ≈ 0.05–0.08.
3. *The asserted split is soft.* The petition's anchor conflict is with the
   D.C. Circuit's Whole Foods — a fractured decision with two separate majority
   opinions and no controlling rationale (with then-Judge Kavanaugh dissenting
   against Brown Shoe's indicia altogether), which the Fifth Circuit here
   "declined to rule on" as "nonbinding even within that Circuit" rather than
   squarely rejected. Newcal is a Ninth Circuit aftermarket case at the
   pleading stage. The rest of the support is district-court decisions and the
   Merger Guidelines. Clerks can — and I expect will — read this as a shallow,
   avoidable conflict.
4. *Fact-bound posture.* A summary-judgment market-definition affirmance turning
   on record percentages (27.7% channel exit, 72%/82% GPO purchase shares) has
   an error-correction flavor the Court resists, and parts of the record are
   sealed/redacted — a modest vehicle wrinkle.
5. *Weak amicus signal.* One brief from a solo practitioner, not an industry or
   scholars' brief.

**Adjustments up — real but smaller.** Published Fifth Circuit opinion
(164 F.4th 405) that expressly declines to follow the D.C. Circuit's approach;
a recurring, outcome-determinative threshold issue across modern antitrust
litigation; the Court's occasional appetite for market-definition questions
(Amex); competent appellate counsel with a disciplined, narrow ask. These keep
me at 0.07 rather than the ~4% no-signal paid rate.

**Claims.** `disposition` 0.07 restates the number above. `relist-increment`
0.32: from the frozen count of 2, a further distribution happens if the Court
CFRs (~0.25–0.30, forcing redistribution) or plain-relists out of the long
conference without one (~0.05–0.08); the statpack's relist cuts (terminal
buckets: ~26% of the paid segment ends with ≥1 relist) frame the population but
this docket's CFR channel is the dominant term. `cvsg-increment` 0.05: the
docket-wide CVSG incidence is ~1.3% (173 of ~13,400 paid petitions), and
antitrust is a CVSG-prone subject, but most of the CVSG mass sits on petitions
that survive early conferences, which this one probably will not.

**Uncertainty / where to discount me.** My main uncertainty is the CFR
probability — it is not a statpack cut and my 0.25–0.30 is judgment, not a
measured rate; if the Court requests a response, my number is too low and the
petition moves toward the band anchor. I also could not verify the Fifth
Circuit panel composition or confirm the absence of a dissent below: the
CourtListener cluster record for the opinion returned mismatched metadata
(a different case's fields), so I rely on the petition's silence — a petition
would certainly cite a dissent if one existed. The provisioned inputs were
complete and current (snapshot dated today, both documents extracted, no
truncation); no BIO text exists because the response was waived, not because
extraction failed.
