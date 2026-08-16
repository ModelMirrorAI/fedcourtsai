# Rationale for the numbers

**P(disturbed) = 0.88, judgment = reversed, 6–3.**

## Anchor

The committed statpack's "The merits docket (granted cases)" section publishes
an `excluded` count (67 pool-guard exclusions), so its per-Term disturbed
rates are quotable and are the registered baseline feed. This case's grant
Term is OT2025 (cert granted 2026-06-29, from the event's `opened_at`), so the
pool is grant Terms 2015–2024, strictly before mine; the table holds parsed
judgments for 2017–2024. Pooled: 515 parsed, 359 disturbed — **69.7%**,
comfortably over the 30-parsed floor. That is the baseline my Brier skill is
scored against.

## Adjustments up from 0.70

- **The Court has already granted emergency relief on both questions
  presented, in the petitioner's direction.** In this very case, the August
  2024 partial stay (No. 24A164, recited in the petition and its appendix)
  reinstated the state-form proof-of-citizenship requirement pending appeal —
  a stay that under Hollingsworth requires a fair prospect of reversal. And
  the October 2024 Beals stay lifted the injunction against Virginia's
  90-day-window noncitizen removals, the same QP2 issue on the same NVRA
  provision. A grant following the Court's own prior emergency intervention
  against the judgment below is among the strongest reversal signals
  available.
- **The United States filed as respondent in support of the petitioner**
  (docketed May 26, 2026) — SG-side alignment with the petitioner correlates
  strongly with reversal.
- **The petition was granted fast**: two distributions, with petitioner
  waiving the Rule 15.5 waiting period — a clean, wanted grant, not a
  relist-scarred compromise.
- **The court below is the Ninth Circuit**, historically the most-reversed
  circuit, and the petition frames concrete splits (Eighth Circuit's Carson v.
  Simon on the consent decree; Eleventh/Fourth vs. Ninth on the 90-day
  provision).
- **P(disturbed) needs only one of the two QPs to go the petitioner's way** —
  an affirmed-in-part-reversed-in-part outcome counts as disturbed on this
  axis.

## Adjustments down

- **A live standing challenge.** The AAANHPI respondents' BIO leads with an
  Article III attack on the RNC (the State and Attorney General did not
  appeal). I discount it — the Court granted anyway, the RNC was a full
  intervenor-defendant below, and the legislative-leader companion petition
  (25-1019, per the joint BIO caption) offers a Berger-style backstop — but a
  dismissal on standing or a DIG would leave the judgment standing, and both
  count as undisturbed. I put roughly 5% on that family.
- **QP2 is textually closer than QP1.** "Ineligible voters" in §20507(c)(2)
  can plausibly cover noncitizens (the Eleventh Circuit's Arcia read it that
  way for the removal bar), and the DNC BIO presses that the removal scheme
  has never been enforced, weakening the record. A split decision is possible,
  but it still disturbs.

Net: 0.70 baseline, strong upward pull from the stay history and SG
alignment, small reserve for the procedural exits → **0.88**.

## Label and votes

"Reversed" over "vacated": the Ninth Circuit affirmed the district court's
injunction of the state statutes; a ruling for the RNC on the questions
presented rejects the holdings themselves rather than remanding for
reapplication of a corrected standard, so a reversal entry is the modal
parse. The 6–3 lineup follows the two stay orders' apparent alignments;
Barrett on QP2 is my main vote uncertainty (a 5–4 or a concur-in-part
variant), and no recusal is on the record, so an equally divided affirmance
gets negligible weight. No vote source is populated today, so the block is
banked, not scored — it is still my honest lineup.

## What I worked from, and where to discount me

- This is a **forward** cell (mode `forward`, no cutoff): the judgment does
  not exist yet — merits briefs are not yet filed (petitioner's due
  2026-08-28), so there was nothing case-specific to retrieve beyond the
  provisioned record. I worked from the **docket skeleton plus the cert-stage
  documents** (petition, three BIOs' text, QP section) and general knowledge
  of this litigation predating the snapshot (the 2024 stay orders, the Ninth
  Circuit's February 2025 decision) — legitimate forward signal. No merits
  advocacy is on my desk; the briefed-moment cell will re-measure with it.
- The context's `band: elevated` (sal-v3) is a cert construct; per the stage
  rule I did not anchor on it — the petition's grant is settled history.
- One `fedcourts query` citation lookup returned nothing (citation coverage
  is sparse: 161 of 590k SCOTUS rows). I did not retry sparse filters; the
  statpack is the anchor. The CourtListener MCP surface was not needed and
  was not used.
- Main uncertainty: the standing question's bite and Barrett's QP2 vote. If
  the Court limits the grant's effective scope at the merits (e.g., resolving
  QP1 on the consent decree only), the disturbed binary is unaffected but the
  ground-breadth proposition would grade poorly.
