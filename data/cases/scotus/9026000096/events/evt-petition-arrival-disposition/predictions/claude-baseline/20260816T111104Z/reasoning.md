# Rationale — P(grant) 0.78

**Cell.** Arrival-moment cert cell, forward mode. `record/context.json` freezes
`band: federal` under `sal-v3`, `distribution_count: 0`, no CVSG, Term 2026.
Per the arrival-moment rule I anchored on the frozen band's bracketed `reached`
rate, not on any distributed-population figure.

**Anchor.** The statpack's "Segment base rate by salience band (sal-v3)" table
carries a `federal` column. Pooling the bracketed `reached` figures over the
rendered Terms strictly before 2026 (OT2017–OT2025, n=201 weighted resolved)
gives ≈71% — consistent with the pack's terminal federal-band row (48.8%
granted + 22.4% gvr ≈ 71% grant family, n=201). That is the yardstick this
cell is scored against, and my starting point.

**Adjustments up (net +0.07).**
- The petitioner is the Solicitor General personally (D. John Sauer, counsel
  of record), with a Deputy SG and an Assistant to the SG on the brief — the
  strongest single cert predictor the record can show, and stronger than the
  band's average member, which includes routine federal-agency petitions.
- The Ninth Circuit was divided at both stages: a panel dissent (Bumatay, J.)
  and two dissents from denial of rehearing en banc (Collins, J.; Tung, J.),
  which the petition quotes extensively.
- The government quantifies systemic consequences: 35+ similar statutes, 4M+
  acres (72,000 acres of the ceded Fort Hall lands alone), and argues the
  decision leaves it no viable disposal method for any of it. The petition's
  grant theory — public-lands cases are geographically confined so the Court
  grants without a split (Cowpasture, Babbitt, Andrus) — matches the Court's
  actual practice.
- A companion petition (No. 26-109, marked "Vide" on the docket — J.R. Simplot
  Company, the intervenor whose land exchange was invalidated) and a
  petition-stage industry appearance (NAM and the Fertilizer Institute, Baker
  Botts) both signal real stakes.

**Adjustments down.**
- No circuit split is claimed; the QP construes one 1900 statute, and the
  Court could see it as a splitless, statute-specific error-correction ask.
- The case reached CA9 on a certified interlocutory appeal (Ninth Circuit
  Nos. 23-80058/59 granting permission to appeal), a posture the Court
  sometimes treats as a vehicle defect.
- Respondents retained elite Supreme Court counsel (Neal Katyal, Milbank) who
  will contest the vehicle hard in the BIO, which I have not seen — the BIO is
  not yet filed (extended to September 21, 2026), so the opposition's best
  arguments are unknown to me.

Net: 0.78. Within the grant family I put nearly all mass on a plenary grant —
no intervening decision exists to GVR against, hence `predicted_disposition:
granted` and `summary-disposition-route` at 0.03.

**Other claims.**
- `relist-increment` 0.97: from a zero-distribution state, essentially every
  petition that is not withdrawn or dismissed before conference is distributed
  at least once; nothing here suggests withdrawal or settlement before the
  first conference.
- `cvsg-increment` 0.01: the SG is the petitioner; a CVSG invites the views of
  a non-party United States and cannot sensibly issue here. Near-zero rather
  than zero only for resolver edge cases.
- `dissent-from-denial` 0.15: conditional on a denial. Most denials — even of
  SG petitions — pass silently; the public-lands stakes make a statement
  respecting denial plausible but not likely.

**Uncertainty and discounts.** The biggest gap is the unfiled BIO: I am
pricing the opposition from the docket posture, not its text. Second, the
statpack's `federal` band pools all federal-petitioner filings, and I adjusted
upward on SG-specific and division signals whose incremental value over the
band is judgment, not a published cut. Third, the interlocutory posture is the
one visible vehicle risk, and I may be underweighting it — the Ninth Circuit
took the appeal by permission, which cuts both ways (someone thought the
question controlling and important). A corpus `query` on the petition's cited
public-lands precedents returned no rows (the citation column is sparse — a
coverage gap, not evidence of no precedent), so the quantitative anchor rests
on the statpack alone.
