# Rationale for the numbers

## Cell and mode

Cert-stage cell, `moment: cvsg`, `mode: forward`. Snapshot `2026-04-07.json` (truncated at the cutoff the CVSG moment fixes), `band: high` under `sal-v4`, `distribution_count: 2`, `cvsg_date: 2026-04-06`, `term: 2025`. Because the cell is forward, retrieval was unrestricted and I used post-snapshot public material about this docket (below); nothing I found discloses a disposition, and the CourtListener docket record shows no termination date.

## Anchors

- **Salience band.** The statpack's per-Term "Segment base rate by salience band (sal-v4)" matches the context's version and carries a `high` column. Pooling the bracketed `reached` figures over Terms strictly before OT2025 (OT2017 through OT2024, every row the table renders) gives 35.0% (n=898). That is the yardstick the evaluator scores this cell against.
- **CVSG cut.** "Cert petitions by CVSG status (paid scored segment)": with a CVSG, granted 29.4%, gvr 5.5%, denied 62.0%, dismissed 3.1% (n=163 resolved). Grant family ~35%, agreeing with the band anchor.
- **Relist cut.** At two distributions the terminal-bucket grant family is ~41%; but this is a terminal cut and this petition will accrue at least one more distribution by construction, so I read it for shape only.

## Adjustments from ~0.35 to 0.16

1. **The Solicitor General recommended denial (August 31, 2026).** This is the single largest update. The brief says the Sixth Circuit erred in reading 502(a)(3) to exclude surcharge categorically, but that (a) top-hat plans are exempt from ERISA's fiduciary rules, (b) whether Regions is a fiduciary "in the relevant sense" under CIGNA is disputed and unaddressed below, so the Court would face a threshold issue before reaching the QP, (c) no circuit would clearly decide a top-hat/rabbi-trust case differently, (d) the preemption holding is correct and unconflicted, and (e) the Fifth Circuit's Aramark panel decision has been vacated for en banc rehearing. The Court follows a CVSG denial recommendation most of the time; from general knowledge of CVSG outcomes, grants over an SG denial recommendation run in the range of roughly one in five or fewer. The statpack carries no cut conditioned on the SG's recommendation, so this figure is mine, not a committed base rate.
2. **The vehicle problems are real, not respondent spin.** The petition itself concedes top-hat plans are exempt from fiduciary duties; the Sixth Circuit said it was "far from clear" petitioners alleged an ERISA violation at all; petitioners' reply had to argue Regions is a trustee-type fiduciary, a point the panel never reached. Both the BIO (Garre, Latham) and the United States press the same points.
3. **A better vehicle is on the horizon.** Aramark v. Aetna is pending en banc in the Fifth Circuit with an undisputed fiduciary defendant and Labor Department amicus participation. The Court has every reason to wait.
4. **Question 2 adds nothing.** No conflict alleged; both opposing filings say settled law was applied.

Pulling the other way, and why I do not go lower than ~0.15: the Court requested a response after Regions waived (a Justice-driven signal) and then CVSG'd, so at least some chambers were interested; the Solicitor General concedes error and an acknowledged split; petitioners have credible Supreme Court counsel (UVA Supreme Court Litigation Clinic) and a Bray amicus; and the Court has occasionally granted over an SG denial recommendation where it thought the issue ripe. Those factors keep me above the ~0.10 I would assign a petition with vehicle defects this pronounced and no CVSG interest.

## The other claims

- `relist-increment` 0.96: the snapshot shows two distributions; the public docket already shows a third (September 16, 2026, for the October 9 conference), so the increment is essentially realized. The residual accounts for parse conventions in how the harness counts distribution entries.
- `cvsg-increment` 0.01: a CVSG is already on the docket, so the claim is vacuous for this cell and will be masked; I state a near-zero number because no further CVSG can issue.
- `summary-disposition-route` 0.08 (conditional on grant): no intervening decision to GVR against; the CVSG cut's GVR share of grants is ~16%, and I adjust down because the SG's vehicle objections make a summary merits ruling especially unlikely here.
- `dissent-from-denial` 0.18 (conditional on denial): elevated relative to the docket because the SG conceded error and a live split, and the equity/remedies theme attracts separate writing from Justices Gorsuch and Thomas; still a minority outcome because the Court usually denies CVSG'd petitions on the SG's say-so without comment.

## What I read

Provisioned: `questions-presented.txt`, the petition (introduction, proceedings below, and the vehicle section; `documents.json` marks it truncated at 118 pages, which cut only the appendix), and the full-text BIO (introduction, procedural background, the Fifth Circuit and vehicle sections). Retrieved: the public docket for 25-590 on supremecourt.gov, the SCOTUSblog case page, and the Solicitor General's amicus brief (introduction, discussion, conclusion). I did not read petitioners' September 16 supplemental reply, so my read of their answer to the SG is inferred from their cert reply as characterized in the SG brief.

## Uncertainty and where to discount me

The conditional grant rate given an SG denial recommendation is from memory, not from a committed statpack cut. I could not read the supplemental reply, which may argue Regions is a rabbi-trust trustee and therefore a fiduciary in CIGNA's sense more forcefully than I credit. The corpus's CVSG rows in the 2020s slice I pulled were too few (6) to condition on the SG's position, so that pull informed shape only. This predictor also has an earlier-run cell on this event (August 2026, before the SG brief); I did not read it and this forecast is formed from this moment's record.
