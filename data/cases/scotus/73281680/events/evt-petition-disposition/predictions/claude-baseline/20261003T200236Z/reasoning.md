# Why 0.08

**Anchor.** `record/context.json` freezes this cell at band `baseline` under
`sal-v4`, one distribution, no CVSG, `forward` mode, snapshot `2026-10-03.json`
(cutoff null, as-stored). Per the prompt, the yardstick is the baseline band's
bracketed `reached` rate in the statpack's "Segment base rate by salience band
(sal-v4)" table, pooled over Term rows strictly before this case's Term (2025).
Pooling 2017–2024 (reached n = 1643, 1524, 1399, 1739, 1500, 1192, 1312, 1271;
rates 4.7, 4.6, 4.6, 4.5, 5.6, 5.8, 5.9, 5.7%) gives roughly **5.1%**. The
modern-cert whole-docket grant family (granted + gvr) sits near 3%; the ca8
circuit cut is about 2.6% grant family, slightly below the docket average; the
relist-0 bucket is 1.7% but that is a terminal-state figure and not the
forward hazard from a first conference.

**What pushed me up (to ~0.08).**
- The question is real and the Court knows it is open. *Bouarfa v. Mayorkas*,
  604 U.S. 6, 19 (2024) says in terms that the Court "need not resolve whether
  § 1252(a)(2)(B)(ii) strips courts of jurisdiction to review threshold
  determinations that the agency must make before exercising discretion."
  The Eighth Circuit resolved exactly that question (published, Colloton, C.J.,
  joined by Loken and Benton), and it was outcome-determinative: the district
  court had twice granted summary judgment for Fofana, and the reversal rests
  on jurisdiction alone.
- There is at least some conflicting authority: *Hosseini v. Johnson*, 826 F.3d
  354 (6th Cir. 2016), held the § 1159(b) step-one eligibility finding
  reviewable in district court, and the Eighth Circuit's own *Bremer* line
  pointed the other way until this opinion "clarified" it. The Court has
  granted two § 1252(a)(2)(B) scope cases in four Terms (*Patel*, *Bouarfa*),
  so the subject is one it is willing to take.
- The Solicitor General did not waive. On a petition filed by the petitioner
  himself (see below), a waiver is the default; instead the SG took four
  extensions (the fourth letter cites press of business, so this is a weak
  signal) and filed a brief in opposition on September 8, 2026.

**What pulled me back down.**
- *Shaiban v. Jaddou*, No. 24-183, is this petition's near twin: asylee
  adjustment under § 1159(b), a terrorism-related inadmissibility finding, a
  Fourth Circuit holding (97 F.4th 268 (2024)) that clause (ii) bars review of
  the threshold eligibility determination, and an SG memorandum asking the
  Court to hold for *Bouarfa*. After *Bouarfa* the Court **denied** Shaiban
  (order list of January 13, 2025) rather than GVR'ing. Having passed on the
  identical question 21 months ago with the reservation fresh, the Court is
  unlikely to take it now in a weaker vehicle.
- The freshest contrary circuit authority has been pulled. *Mukantagara v.
  Noem* (10th Cir. Jan. 12, 2026) held clause (ii) does not reach
  non-discretionary eligibility determinations and relied on the § 1159(b)
  line, but on the government's rehearing petition the panel vacated that
  judgment in July 2026 and ordered supplemental briefing on whether *Mullin v.
  Doe* (June 25, 2026, 6–3), which treats subsidiary determinations as
  unreviewable where the final action is, undermines it. So the SG's BIO can
  fairly say the split is stale (*Hosseini* predates *Patel*) or dissolving,
  and the Court's own recent direction favours the Eighth Circuit's reading,
  which lowers the Court's appetite to correct it.
- Vehicle and advocacy. The docket lists the petitioner himself as counsel of
  record (with a Minneapolis immigration firm's address), and the Clerk's
  paper-only instruction confirms the filer is not a member of the Supreme
  Court bar. There are no amici. The underlying facts (soliciting funds for a
  Tier III terrorist organization) are unsympathetic, and the Eighth Circuit
  opinion is tightly reasoned from *Patel* and *Kucana*, leaving little for
  the Court to work around.
- Timing: first distribution at the first October conference, with a
  government BIO on file, is the ordinary route to a denial.

Net: roughly 1.5× the band anchor, i.e. **0.08**.

**Claims.** `disposition` 0.08 restates the top-level number. `relist-increment`
0.30: the paid scored segment is relisted at least once about a quarter of the
time by the statpack's relist-count cut, and this petition has a bit more than
average to hold a Justice's attention; a reschedule would also count. `cvsg-
increment` 0.01: the United States is the respondent. `summary-disposition-
route` 0.10 conditional on grant: nothing to GVR in light of; a grant would be
plenary. `dissent-from-denial` 0.10: Shaiban drew none; a Gorsuch or Sotomayor
statement is possible but not the base case.

**Big-case score 0.35.** If decided, the ruling would fix the reviewability of
eligibility findings behind every discretionary immigration benefit outside
clause (i)'s list — real doctrinal stakes, little public salience.

**Where to discount me.**
- No filed documents were provisioned (`record/documents/` does not exist): no
  petition, no questions-presented file, no BIO text. The petition is a paper
  filing with no PDF on the docket, and the BIO entry carries no link, so I
  could not retrieve either. My reading of the petition's QP is inferred from
  the Eighth Circuit opinion, and my account of the SG's likely arguments is
  inferred from the SG's Shaiban memorandum and the intervening case law, not
  from the actual BIO. If the SG acquiesced or confessed error in the BIO
  (I think this unlikely given the government's rehearing petition in
  Mukantagara), the number is far too low.
- The counsel-of-record ambiguity (petitioner's name, a law firm's address)
  means the petition may be more professionally drafted than a pro se filing;
  I weighted the advocacy discount lightly for that reason.
- The Shaiban denial is public information predating the snapshot, used as a
  comparator; it is not this case's outcome. I know nothing about this
  petition's disposition, which has not occurred (conference is October 9).
- The statpack's circuit and relist cuts are terminal-state cuts and the band
  table pools denial-reweighted estimates; I used them as shape, not as the
  answer.
