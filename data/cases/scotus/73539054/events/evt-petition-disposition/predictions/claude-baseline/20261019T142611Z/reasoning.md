# Rationale — P(grant) = 0.04

**Inputs read:** the snapshot `2026-10-19.json`, `context.json` (forward mode, band `baseline` under sal-v4,
distribution_count 1, no CVSG, Term 2025), the questions presented, the full government brief in opposition, and
part of the cert reply (searched for the AT&T dissent and Justices' remarks). I did not read the petition body or
the appendix beyond the QPs. The QPs and the BIO's summary of the petition's arguments captured the contested
issues, but a reader should discount my read of the petitioners' best case accordingly.

**Anchor.** For band `baseline`, I used the bracketed `reached` rate in the statpack's "Segment base rate by salience
band (sal-v4)" table, pooled over the Terms shown before 2025 (OT2017–OT2024). That rate runs 4.5–5.9% per Term,
about **5%** pooled. The table's salience version matches my context. The petitioner is private, so `baseline` is
also its caption-class floor.

**Adjustments up:** elite Supreme Court counsel (Gibson Dunn), two amicus briefs at the cert stage (CTIA and the U.S.
Chamber), a $92M penalty, and a GVR request tied to a fresh decision of this Court (FCC v. AT&T, 2026). A GVR is a
low-cost disposition that the Court sometimes uses for petitions held behind a lead case.

**Adjustments down, which outweigh the above:**
1. The Solicitor General opposes even the GVR. The government points out that the Court declined a remand in AT&T
   and denied Verizon's rehearing petition asking for the same remand on a "misled" theory (Aug. 17, 2026). Granting
   one to T-Mobile/Sprint would treat like cases unlike, and the Court usually avoids that.
2. The "misled into paying" theory was apparently not raised in the D.C. Circuit. AT&T expressly reserved it
   (n.5). That makes a Lawrence v. Chater GVR weak.
3. There is no circuit split on CPNI: the Second Circuit agrees, and that judgment was affirmed in AT&T on other
   grounds. The D.C. Circuit held the § 503 statutory argument forfeited, which makes QP 3 a poor vehicle.
4. The industry has ended its location-based-service programs, so the questions have limited prospective
   importance.

Net: a little below the anchor, at 0.04.

**Other claims.**
- relist-increment 0.15: a first-conference paid petition with amici sits a bit above the low unconditional relist
  hazard. Thomas's AT&T dissent makes a relist for a separate writing plausible.
- cvsg-increment 0.005: the federal government is the respondent, so a CVSG is essentially impossible.
- summary-disposition-route 0.5 (conditional on a grant): QP 1 is itself a GVR request.
- dissent-from-denial 0.1: raised above a generic rate because of the AT&T dissent.

**Uncertainty and discounts.** I have not read the AT&T opinion itself. I know it only from how the briefs
characterize it, and it postdates my training. If the AT&T majority is narrower than the SG says, or if other
held cases were GVR'd after AT&T, the GVR odds would rise. I could not check either point because I did no
external retrieval. The relist count is the signal to watch.
