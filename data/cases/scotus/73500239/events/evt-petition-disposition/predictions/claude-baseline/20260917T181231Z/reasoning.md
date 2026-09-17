# Rationale for the numbers

**P(grant) = 0.02; predicted disposition: denied.**

## What I read

- `record/snapshots/2026-09-17.json` (the provisioned baseline): paid petition, No. 25-1337, docketed June 1, 2026, from the Sixth Circuit (No. 24-3947; decision November 4, 2025; rehearing en banc denied December 29, 2025). Three docket entries: the petition (March 30, 2026), a **waiver of the right to respond** by the respondents (June 25, 2026), and a single distribution on July 1, 2026 for the **Conference of September 28, 2026**. No relist, no CVSG, no amicus.
- `record/context.json`: forward cell, `band: baseline` under `sal-v4`, `distribution_count: 1`, `cvsg_date: null`, Term 2025.
- `record/documents/petition.txt` (25 pages, full text extracted) and `questions-presented.txt`. No brief in opposition exists; the respondents waived.

## Anchor

The context's band is `baseline`, and the statpack's "Segment base rate by salience band" table is computed under `sal-v4`, matching the context's `salience_version`. Pooling the bracketed `reached` figures for `baseline` over the rendered Terms strictly before OT2025 (OT2017 through OT2024) gives a weighted rate of about **5.1%** over roughly 11,600 weighted petitions (the last four Terms alone pool to about 5.7%). The petitioner is a private individual, so `baseline` is also the right caption class. The relist-count cut shows the paid scored segment's terminal shape: about 74% of petitions never draw a second distribution; those that do grant at 8% (one relist) rising to 22–28% (two or more).

## Adjustments

Down, and substantially, from 5.1% to 2%:

1. **Waiver of response.** The respondents declined to file a brief in opposition. The Court almost never grants without a response; a grant here would require a call for a response first, which itself happens only for a small fraction of waived petitions. This is the single largest factor.
2. **Vehicle.** The Sixth Circuit's opinion is unpublished (the petition cites it only to Westlaw and describes the lower-court decisions as "a series of unpublished opinions"), and it affirmed on **causation**: the professor was terminated for research misconduct, not for the content of his paper. The court of appeals did not reach the district court's alternative *Garcetti* holding. So neither the *Sullivan*-malice question (QP 1) nor the *Garcetti* academic-freedom question (QP 2) was the ground of decision below, and QP 3 asks for fact-bound error correction.
3. **No clean split.** The petition's asserted disagreement rests on a 1995 Ninth Circuit observation (*Johnson v. Multnomah County*) about how malice figures in *Pickering* balancing, and the petition itself concedes that split "is not quite posed as it is here." The *Sullivan*-threshold rule it proposes has not been adopted by any circuit it cites.
4. **Presentation.** The petition is from a solo practitioner, spends much of its length re-arguing the record, and asks the Court to grant "whether the Court affirms or reverses," which is not how the Court reads a cert petition.

Up, modestly:

- The *Garcetti* reservation for academic speech is a genuinely open question that Justices have signaled interest in (the petition cites Justice Thomas's statement respecting denial in *MacRae v. Matthews*), and the underlying subject (a professor disciplined after publishing race-and-intelligence research, with record evidence the petition characterizes as committee members condemning the research as "harmful") is the kind of viewpoint-discrimination narrative that can draw a call for a response from an interested chambers. This keeps me at 2% rather than 1%.

## The other claims

- **relist-increment 0.12.** From one distribution. The terminal shape says roughly a quarter of paid scored-segment petitions see a second distribution, but that population includes petitions with a filed opposition, which draw far more scrutiny. On a waived petition the main paths are a call for a response (I put that at roughly 7–8%) and a short relist for a statement (a few percent), plus a small allowance for a reschedule.
- **cvsg-increment 0.01.** No federal party; the federal interest is peripheral.
- **summary-disposition-route 0.35 (conditional on a grant).** The statpack's modern-cert grant family is roughly 47% GVR, but I identify no intervening decision of this Court that would drive a GVR here, so I sit below that share while still well above zero, because a grant on this record is more plausible as a GVR than as plenary review.
- **dissent-from-denial 0.05 (conditional on a denial).** Justice Thomas's prior writing on the *Pickering*/*Garcetti* framework and the academic-freedom subject make a statement conceivable; the causation ground and unpublished status make it unlikely.
- **big_case_score 0.3.** Stakes are moderate: a real doctrinal question and a newsworthy subject, but a posture that would confine any decision to its facts.

## Retrieval and its limits

Forward cell, so retrieval was unrestricted. I ran one corpus query for recent granted SCOTUS priors (which returned mostly high-profile applications and government-side grants, not comparable to this petition, and served only to confirm the shape of the granted population) and four CourtListener searches. CourtListener does not index the Sixth Circuit's unpublished opinion in *Pesta v. Cleveland State University* and shows no SCOTUS docket for the case; it does show the N.D. Ohio docket (1:23-cv-00546, terminated October 7, 2024), which confirms the procedural history the petition recites. My read of the decision below therefore rests on the petition's own account of it, which is an advocate's account, and a reader should discount my vehicle analysis accordingly: the petition's characterization of the Sixth Circuit's causation holding is consistent across its jurisdiction, procedural-history and argument sections, and the waiver of response is consistent with a respondent who reads that holding as fact-bound, but I did not read the opinion itself. Nothing I retrieved disclosed this petition's disposition.

## Where to discount me

The number is dominated by two docket facts (waiver, one distribution for the long conference) and a base rate; the case-specific reading adds little beyond confirming the petition is weaker than the band average. If the Court calls for a response after the September 28 conference, this forecast should be treated as superseded: the conditional grant probability would move to the high single digits.
