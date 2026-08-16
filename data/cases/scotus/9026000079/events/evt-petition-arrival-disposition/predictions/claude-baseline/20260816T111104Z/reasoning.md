# Rationale for the numbers

**P(grant family) = 0.025.**

**Anchor.** This is a cert-stage `arrival` cell with a frozen band of `baseline`
under `sal-v3` (matching the statpack table's version), Term 2026,
`distribution_count` 0. The scored yardstick is the baseline band's bracketed
`reached` rate — for the weakest band that is the whole paid scored segment's
grant rate, unconditional on trajectory, which is exactly the arrival
population's rate. Pooling every rendered Term strictly before 2026
(OT2017–OT2025) from the "Segment base rate by salience band (sal-v3)" table:
Σ(rate x n) / Σn = 862 / 13163 ≈ **6.6%**.

**Adjustments down from 6.6% to 2.5%, all from pre-decision material:**

1. **Unpublished memorandum disposition below.** The CA9 resolved the case
   (docket 25-2460, Acosta-Tapia v. Bondi) in an unpublished memorandum,
   submitted on the briefs without oral argument, with no noted dissent. The
   Court rarely grants from unpublished, non-precedential dispositions; they
   signal the panel saw settled law.
2. **The disposition below was a dismissal** of the petition for review —
   apparently threshold/jurisdictional — in a removal case, a very high-volume,
   very high-denial class of petitions.
3. **The SG waived the right to respond** (Aug 14, 2026). The modal path from a
   waiver is denial without a response ever being filed; a grant would require
   the extra step of a call for a response first.
4. **Counsel profile.** Petitioner's counsel is a solo immigration practitioner
   in Tucson, not a repeat Supreme Court advocate; no cert-stage amici have
   appeared.
5. **Circuit cut is neutral.** The statpack's modern-cert CA9 cut (granted 2.2%,
   gvr 1.1% of resolved) sits at the docket average — no adjustment either way.

**What pushes mildly the other way, keeping me off the floor:** the petition is
paid and counseled (already in the anchor's population); an immigration
advocacy group (National Immigration Litigation Alliance) tried to file an
amicus brief supporting the petitioner below, suggesting the legal issue has
some currency with the immigration bar; and if the dismissal below turned on
the scope of review under 8 U.S.C. § 1252, that is a question family the Court
has repeatedly taken in recent Terms — and one that also supports GVR potential
if a related merits case decides this Term (hence the relatively high 0.45 on
`summary-disposition-route`, conditional on any grant).

**Main uncertainty — I could not read the petition.** No documents were
provisioned, and the docket shows why: the Court directed filings in paper form
only (Rule 34.6 note), so no QP text exists on the electronic docket. The CA9
memorandum and the rehearing petition are also unavailable in RECAP
(`is_available: false`), so my read of the ground of dismissal is inference
from the docket entries, not from any opinion or brief text. If the QP is a
clean, well-preserved circuit-split question on § 1252 review, 0.025 is too
low; nothing visible suggests that, but a reader should weight this cell as a
docket-skeleton forecast.

**Other claim numbers.** `relist-increment` 0.96 is P(ever distributed) from a
zero-distribution state — near-certain post-waiver, discounted slightly for
pre-conference dismissal/withdrawal (the petitioner is under a removal order;
the case could exit the docket before conference). `cvsg-increment` 0.005 is
structural: the United States is the respondent, so a CVSG is effectively
unavailable. `dissent-from-denial` 0.02 reflects the rarity of separate
writings on denials of low-salience petitions, nudged up slightly for the
immigration-removal subject matter.

**Mode and hygiene.** Forward cell; retrieval was unrestricted and nothing I
retrieved disclosed any disposition of this petition (the SCOTUS docket shows
it pending, response due Aug 17, 2026). I did not query for this case's
outcome. The corpus `query` I ran (recent resolved SCOTUS priors) returned
mostly unrelated denials and did not move the number.
