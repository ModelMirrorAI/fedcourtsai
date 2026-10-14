# Rationale — P(disturbed) = 0.84

**Inputs.** Forward cell, `moment: grant` (event opened 2026-10-13, the day the docket shows
"Petition GRANTED"). I read snapshot `2026-10-13.json` and the provisioned petition, QP
section, brief in opposition (CREW), and the cert reply. No merits briefs are on disk,
which is what a grant-moment cell should see, so there is no provisioning anomaly to flag.
This forecast rests on the cert-stage papers and the docket skeleton; I did no CourtListener
or corpus retrieval.

**Anchor.** The statpack's "The merits docket (granted cases)" section publishes an
`excluded` column, so it is quotable. This case's grant Term is OT2026 (granted Oct 13,
2026), so the pool is grant Terms 2016–2025. The table has rows for 2017–2025 (2016 has
no parsed judgment): 377 disturbed / 540 parsed = **69.8%**, which clears the 30-judgment
floor. Coverage caveat: OT2025 is thin (24 parsed of 51 granted), mostly pendency and
skewed toward quick dispositions. Every other Term in the pool has near-full coverage.

**Adjustments up.**
- The Solicitor General is the petitioner. Plenary grants on the SG's petition reverse at
  well above the docket's average rate.
- This Court has already ruled for the government in this same case. In June 2025 it
  stayed discovery, granted cert, vacated the denial of mandamus, and said the
  recommendation requests were not tailored, that FOIA status "cannot turn on [the]
  ability to persuade", and that Cheney's separation-of-powers restraint applies. The
  government's core complaint now is that the D.C. Circuit read that order too narrowly.
  A Court that took a second interlocutory look at a discovery order is very unlikely to
  be granting just to approve it.
- The petition itself suggested summary reversal. The Court chose plenary review instead.
  That signals the Court wants to write, and nothing in the docket suggests it wants to
  write in order to affirm.

**Adjustments down.**
- Mootness or a DIG. The DOGE temporary organization's EO term ended in July 2026, and
  the BIO argues the equities have faded. A DIG or dismissal would leave the judgment
  standing. A Munsingwear vacatur would not, so only part of this risk lowers my number.
- The mandamus standard is demanding, and the BIO argues the separation-of-powers point
  was forfeited in the district court. A majority wanting to avoid a categorical FOIA rule
  could still find the remaining discovery adequately tailored. I think that is unlikely
  given the 2025 order.

**Net.** About 0.85–0.88 before the exit risk. I shade to **0.84** for roughly 5–8% DIG
or mootness, a little of which would still show up as a disturbing vacatur.

**Judgment label.** "Reversed" versus "vacated" is close to a coin flip (Cheney itself
vacated). I chose "reversed" because this is the second trip and the Court may tell the
D.C. Circuit what to do instead of remanding open-endedly. Both labels count as disturbed,
so the choice does not affect the scored number.

**Votes.** 6–3 on ideological lines, matching the stay-stage alignment. Low confidence on
any individual Justice: Kagan, or less likely Barrett, could cross on a narrow ground.

**Stakes (big_case_score 0.6).** The issue is a real separation-of-powers question about
discovery against presidential advisers, and the entity is high-profile. The posture is
narrow, though: interlocutory mandamus over discovery scope.

**Where to discount me.** I have not seen the merits briefs or the argument. My view that
SG petitioners get reversals at an elevated rate comes from general knowledge, not from a
committed cut. I did not verify the current organizational status of USDS beyond what the
briefs say.
