# Why P(grant) = 0.07

**Anchor.** `record/context.json` freezes `band: baseline` under `sal-v4`, with `distribution_count` 1 and no CVSG. The statpack's *Segment base rate by salience band (sal-v4)* table gives the bracketed `reached` rate for `baseline` in the Terms before this case's Term (OT2025). Pooled over OT2017–OT2024 it is about 5.2% (4.5%–5.9% per Term, each n ≈ 1,200–1,750). The OT2025 row contains this case, so I left it out.

**What I adjusted for. No committed table conditions on a called-for response, so this part is judgement.**
- *Upward:*
  - The Court called for a response after the Solicitor General waived. This means at least one Justice wanted the petition answered.
  - Two amicus briefs supported the petition: a coalition led by the Washington Legal Foundation with NACDL, and former federal judges. In the statpack's amicus cut, the `2+` bucket grants 18.4% against 2.0% for `0` (n=1,449 resolved). That is a marginal split heavily confounded with relists and CVSGs, so I give it only modest weight.
  - Recent doctrine leans the petitioner's way. *Erlinger* (2024) listed the pre-*Apprendi* decisions the Court has overruled. *Ellingburg* (2026), which the petition cites, treated restitution as criminal punishment. Gorsuch has written in dissent on the restitution jury right.
  - Experienced counsel filed the petition (Winston & Strawn).
- *Downward, and stronger:*
  - The question has been denied over and over. The brief in opposition lists twelve prior denials, most recently *Esformes* (No. 23-95, denied Dec. 2023 after one distribution, per `fedcourts query`) and *Cline* (cert denied 2026).
  - There is no circuit split. Every circuit follows *Libretti*, and the only conflict the petitioner can cite is with this Court's own later cases.
  - Granting means a vote to consider overruling precedent.
  - The decision below is a nonprecedential summary order, and the petitioner conceded below that circuit law foreclosed the claim. That concession is normal for an overruling request but leaves a thin record.
  - The SG's opposition, read from the live docket in forward mode, is short and goes to the merits. It argues that forfeiture has no statutory maximum, so *Apprendi* does not apply, and cites *Booker*'s remark that the forfeiture statute is "perfectly valid". It raises no new vehicle defect, so it does not weaken the petition either.

Calls for response carry a low bar, and most such petitions are still denied. Combining all this, I move from about 5% to 7%, short of a doubling. The call for response plus amici is real attention, but this question has drawn that kind of attention before and been denied every time.

**The other claims.**
- *relist-increment* = 0.97. The petition is already distributed for November 13, and the harness masks this claim.
- *cvsg-increment* ≈ 0. The United States is a party.
- *summary-disposition-route* = 0.04 given a grant. An overruling request goes to plenary review.
- *dissent-from-denial* = 0.25 given a denial. A response called for after a waiver on a recurring question that a Justice has written about is the classic setup for a separate writing, but most calls for response end in plain denials. The order-writers distribution puts most of this on Gorsuch (0.20), with smaller amounts on Thomas, Jackson and Sotomayor. Those per-Justice numbers overlap, so they do not add up to the existence claim.

**Inputs and where to discount me.**
- I read the snapshot `2026-06-16.json`, `questions-presented.txt`, and `petition.txt`. The petition is truncated in its appendix; I read the body through the Reasons section.
- In forward mode I also read the live supremecourt.gov docket, which still shows the petition pending, and the government's brief in opposition (October 13, 2026). Both postdate my provisioned cutoff, which forward mode allows. I did not open the petitioner's reply.
- My main uncertainty is who called for the response and why. If it signals four Justices' interest rather than one Justice preparing a dissent, 7% is too low.
- My knowledge of the earlier separate writings (*Hester*, *Rimlawi*) comes from training and the petition's citations, not from retrieved texts.
