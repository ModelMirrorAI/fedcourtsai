# Reasoning — why P(grant) = 0.015

## Inputs used

- Provisioned snapshot `record/snapshots/2026-09-16.json` (the file `context.json` names). Paid petition, No. 25-1288, docketed May 18, 2026, from the Seventh Circuit (No. 25-1279, decided February 10, 2026, reported at 166 F.4th 627). Entries: petition filed May 11; respondents' waiver June 11; amicus brief of Election Research Institute, Michigan Fair Elections Institute and PA Fair Elections filed June 16; **distributed June 17 for the Conference of September 28, 2026** (one distribution, no relist, no CVSG, no call for a response); petitioners' Rule 15.8 supplemental brief submitted September 15.
- `record/context.json`: mode `forward`, band `baseline` under `sal-v4`, `distribution_count` 1, `cvsg_date` null, term 2025, `signals_observable` true.
- `record/documents/`: `questions-presented.txt` and the full `petition.txt` (56 pages, not truncated, not OCR-derived). No brief in opposition exists because the response was waived; `documents.json` lists only those two files.
- Retrieved (forward mode, unrestricted): the Seventh Circuit per curiam opinion and Chief Judge Brennan's concurrence via the CourtListener MCP server; the amicus brief and the September 15 supplemental brief from supremecourt.gov (see `retrieval.md`).
- Base rates: the committed `metrics/statpack.md`.

## Anchor

Band is `baseline` (private petitioner: caption is a private nonprofit and two individuals against state election commissioners; the state marker places *respondents*, not petitioners, so the petitioner class is private). Under the *Segment base rate by salience band (sal-v4)* table I pooled the bracketed `reached` figure over every rendered Term strictly before OT2025 (OT2017 through OT2024): roughly 593 grant-family outcomes over a weighted n of 11,580, i.e. **about 5.1%**. That is the rate a private paid petition that has reached the baseline band faces, and it is the yardstick this cell is scored against. Cross-checks from the same pack: the paid-scored-segment relist-count cut shows petitions that end at zero relists resolving granted 1.2% plus GVR 0.5%; the no-CVSG bucket shows 4.0% granted plus 2.3% GVR; the Seventh Circuit bucket of the modern-cert-by-circuit table is among the lowest of the regional circuits (granted 1.1%, GVR 1.4%).

## Adjustments down from 5.1%

1. **No response on file and no call for one.** Respondents (the Wisconsin Elections Commission, through the state Department of Justice) waived, and the Court distributed for the long conference without a CFR. The Court almost never grants on a waived petition without first calling for a response, so a grant here requires a CFR that has not happened after three months on the docket. This is the single largest discount.
2. **The claimed circuit split does not reach the provision at issue.** The petition's QP 1 split (First and Sixth Circuits versus Third, Ninth and Eleventh) concerns §§ 21082–21083 (provisional ballots, registration lists). The Seventh Circuit noted, and I confirmed from the petition's own authorities, that no circuit has found a § 1983-enforceable right in § 21112's complaint procedures. After *Medina* (2025) the § 1983 route is in any case largely closed, and the petition itself concedes *Blessing*'s abrogation.
3. **The judgment rests on Article III standing at summary judgment, not on the § 1983 question.** The per curiam held the plaintiffs failed *TransUnion*'s intangible-injury test, failed the Petition Clause theory under *Smith* and *Knight*, and failed *Hippocratic Medicine*'s organizational-standing test on a record the plaintiffs themselves shaped by switching theories mid-case. A unanimous, fact-bound, record-dependent standing dismissal is a weak vehicle even where the underlying doctrine is unsettled.
4. **Recent signals from the Court on adjacent questions point to denial.** The supplemental brief itself reports that the Court denied certiorari in 2026 in *Public Interest Legal Foundation v. Schmidt* (Third Circuit) and *Public Interest Legal Foundation v. Benson* (Sixth Circuit), both election-records organizational-standing cases. Those denials predate this snapshot and are legitimate forward signal: the Court passed on cleaner vehicles for the organizational-standing question this year.
5. **Petition quality and posture.** The petition is diffuse (six headings ranging from *Marbury* and Blackstone to the Spending Clause and a "lawbreaker's charter"), and the supplemental brief pivots the pitch from a HAVA split to a general *Hippocratic Medicine* clarification, which reads as a search for a hook. Counsel's prior election-related filings at this Court (including the 2020 *City of Racine* injunction application cited in the petition) were unsuccessful; I weight this lightly as a general prior, not a case fact.

## Adjustments up

- The doctrinal questions are genuinely live: the panel expressly said whether the history-and-judgment-of-Congress standard "has raised more questions than it answered" is "a question for the Supreme Court," and Chief Judge Brennan's concurrence describes circuit precedent as "largely obsolete" after *Hippocratic Medicine*. Some Justices have shown interest in these standing questions.
- One amicus brief supports the petition and there is a documented federal-enforcement interest (DOJ's June 2025 letter to the Commission).

These are worth a modest upward nudge relative to a bare waived petition but do not offset the vehicle problems.

## Resulting numbers

- **P(grant) 0.015**, about a third of the pooled band anchor. Most of the residual mass is a CFR after the long conference followed by a grant on a reformulated standing question, or a hold-and-GVR if the Court takes an organizational-standing case during OT2026.
- **relist-increment 0.14**: distributed once; the paid scored segment shows roughly a quarter of petitions acquiring at least one further distribution entry, but that figure is an upper bound that includes reschedules, and a waived, uncalled private petition at the long conference sits below the segment average. I add a little for a post-conference CFR, which would generate a redistribution.
- **cvsg-increment 0.02**: above the segment's roughly 1% CVSG incidence because a federal statute with a dedicated DOJ enforcement role is involved, but well short of a real prospect given the standing ground.
- **summary-disposition-route 0.25** (conditional on grant): the grant family is GVR-heavy in the pack, but this case has no intervening decision to be vacated in light of; a GVR is plausible only through a hold for a case not yet identified.
- **dissent-from-denial 0.04**: poor vehicle, unanimous panel, and no dissents noted in the 2026 *Public Interest Legal Foundation* denials.
- **big_case_score 0.35**: a decision on private HAVA enforcement and election-group organizational standing would matter nationally, but the realistic decision footprint is a narrow standing ruling.

## Uncertainties and where to discount me

- I cannot see whether the Court will call for a response after the September 28 conference; if it does, this forecast is materially too low.
- I did not have the district court opinion or the summary-judgment record; my read of the record's thinness comes from the Seventh Circuit's characterization of it.
- The pooled anchor is my own arithmetic over the table's rendered Terms (OT2017 to OT2024); the evaluator's baseline may pool differently.
- No brief in opposition exists, so the respondents' view of the case is inferred only from the waiver.
- The corpus `fedcourts query` run returned recent emergency applications rather than comparable cert petitions (its default ranking is recency and it carries no subject filter that matches HAVA), so it contributed no case-specific priors; the base rates above come from the statpack, not from retrieved priors.
