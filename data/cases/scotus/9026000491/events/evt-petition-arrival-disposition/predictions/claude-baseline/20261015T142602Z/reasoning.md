# Reasoning — P(grant) = 0.72

**Inputs read:** snapshot `2026-10-14.json` (petition docketed; the only entry so
far); `documents/questions-presented.txt`; `documents/petition.txt` (168 pages,
truncated at the text cap; the body of the petition and the start of the en banc
opinion were readable); `context.json` (forward mode, band `federal`, sal-v4,
distribution_count 0, no CVSG, Term 2026). No BIO exists yet.

**Anchor.** This is an arrival cell with band `federal`, so the anchor is the
statpack's sal-v4 `federal` bracketed `reached` rate. I pooled every Term row
shown before 2026 (OT2017–OT2025; the OT2026 row contains this case and has n=2).
That gives about 143 weighted grants out of n≈203, or **≈70%**. Individual Terms
range from 44% to 90%, so the pooled figure is the steadier anchor.

**Adjustments (net roughly flat to slightly up):**
- *Up:* The question is a recognized national issue that the Court left open in
  *CASA*. It has been publicly flagged by Justices on both sides (Gorsuch in
  *Texas*, and Alito's comment at argument about thin briefing; Kavanaugh's
  *Corner Post* concurrence on the other side). The SG presents a single clean QP
  and does not ask the Court to review the merits, so a merits ruling cannot
  displace the remedial question. The en banc court refused to revisit its
  precedent, which supports the SG's argument that only this Court can resolve
  it. Judge Ho's concurrence invites review.
- *Down:* The SG concedes there is no circuit split. Respondents will argue
  vehicle problems: the Court of Appeals said the agencies could use enforcement
  discretion to avoid disruption; new rulemaking or the parallel D.D.C. and M.D.
  Fla. litigation might change the practical stakes; and some Justices may
  prefer a vehicle where non-party relief clearly makes a difference. The Court
  could also hold this petition for, or prefer, a different vehicle raising the
  same question. That is the main way this ends as a non-grant.

**Increments.** `relist-increment` 0.97: at zero distributions, P(at least one
distribution) is close to certain unless the petition is withdrawn or rendered
moot first. `cvsg-increment` 0.01: the SG is the petitioner. `summary-disposition-route`
0.04 given a grant: no intervening decision exists to GVR on. `dissent-from-denial`
0.3 given a denial: this is a salient question with known individual Justice
interest, but a denial here would more likely be a quiet vehicle-based denial
or a hold.

**Uncertainty / discount me where:** I have not seen the BIO. The petition text
was truncated past the en banc opinion's opening, so I relied on the petition's
own description of the remedy holding. I did no live retrieval for competing
petitions on the same question. A pending rival vehicle would lower this number.
