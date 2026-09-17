# Why 0.005

## What I read

- `record/snapshots/2026-09-16.json`: paid docket No. 25-1308, Term 2025, from the Eleventh Circuit (No. 24-14143, decided Oct. 29, 2025, rehearing denied Dec. 23, 2025). Petition filed Mar. 23, 2026 and docketed May 26, 2026 (the clerk extended time for a corrected filing under Rule 14.5). Both respondent groups (Orange County; six county officers) waived the right to respond on June 23, 2026. Distributed once, for the conference of Sept. 28, 2026. No CVSG, no amicus, no related cases.
- `record/context.json`: mode `forward`, band `baseline` under `sal-v4`, `distribution_count` 1, `cvsg_date` null, term 2025, `signals_observable` true. No cutoff; the snapshot is the latest poll.
- `record/documents/petition.txt` (37 pages, OCR-derived, not truncated) and `questions-presented.txt`. No brief in opposition exists to read; both respondents waived. The QP file carries a stray OCR line ("il", a page marker) but the question itself is legible.

## The petition

Petitioners are self-represented (the caption says "Pro Se"; David Foley is listed as counsel of record at a residential address). The petition is well organized for a pro se filing and cites real authority, but its core moves do not survive scrutiny as cert-worthy:

1. **The claimed split is not one.** The petition says "every other circuit" holds Rule 60(b)(4) relief mandatory when a judgment is void. That is true and uncontroversial (Espinosa says as much), but the Eleventh Circuit did not hold otherwise. It held that the earlier panel's res judicata affirmance had already necessarily decided the point petitioners call the voidness defect, so the law-of-the-case doctrine barred relitigating it. No cited circuit holds that a Rule 60(b)(4) movant may relitigate an issue an appellate panel already decided in the same case. The conflict is with the petitioners' reading of their own complaint, not between circuits.
2. **The "void" theory stretches Reynolds v. Stockton (1891) well past Espinosa.** Espinosa confines voidness to jurisdictional defects and due-process violations that deprive a party of notice or an opportunity to be heard. Reading a complaint's property interest as an aviary rather than toucans is, at most, a merits error, and the petition's own Statement concedes the real grievance is how the courts read allegation 10(b).
3. **Vehicle.** The decision below is unreported, the panel affirmed with Rule 38 sanctions for a frivolous appeal, the same petitioners' earlier cert petition on the underlying judgment was denied in 2024 (145 S. Ct. 172, per the petition's Related Cases), and the underlying dispute is a local code-enforcement matter dating to 2007. Respondents' waivers signal they see no risk.

## Anchor and adjustments

- **Anchor.** Context gives band `baseline` under `sal-v4`, which matches the statpack's "Segment base rate by salience band (sal-v4)" table, so that table is my anchor. Pooling the `baseline` bracketed `reached` figure over the rendered Terms strictly before OT2025 (OT2017 through OT2024) gives about 5.1% on a weighted n of roughly 11,600; the three most recent prior Terms alone run about 5.8%. That is the rate the evaluator scores against.
- **Down, hard.** The baseline-band reached rate is a class average over counseled and uncounseled paid petitions alike, and its grants are overwhelmingly counseled petitions presenting genuine splits. This petition has every feature that sits at the bottom of that class: pro se, unreported affirmance, sanctions below, no response, no amicus, a repeat filer already denied once on the same dispute, and a QP whose conflict claim dissolves on inspection. The relist-count cut's relist-0 bucket (denied 97.0%, granted 1.2%, gvr 0.5%) is a terminal-state figure and so understates the forward hazard, but it is the right order of magnitude for a petition I expect to die at first conference. Within that bucket, pro se paid petitions grant at a small fraction of the counseled rate.
- **Circuit and CVSG cuts.** Eleventh Circuit petitions grant at 1.7% plus 1.9% GVR overall, indistinguishable from the docket average; no adjustment. CVSG none bucket: granted 4.0%; no CVSG is conceivable here, so no upward pull.
- **Result.** P(any grant) = 0.005. I would not go lower than about 0.003 because the Court does occasionally summarily vacate an appellate sanctions award or GVR an odd pro se petition, and one of those routes is the only realistic grant path here.

## The other claims

- `relist-increment` 0.08: mostly the chance of a reschedule off the long conference, which the stored distribution count reads as an added entry. A substantive relist is well under half of that.
- `cvsg-increment` 0.005: no federal interest at all.
- `summary-disposition-route` 0.55 (conditional on grant): if granted, plenary review is implausible; a summary route is the more likely shape, though with no intervening decision even that is a stretch. The prior-Term cert-order share of grants (roughly 30 to 55% where the `gvr` label is populated) is the baseline; I sit slightly above it because of the pro se, sanctions-driven profile.
- `dissent-from-denial` 0.01: nothing in the record draws a separate writing.
- `big_case_score` 0.03: stakes are confined to the parties.

## Uncertainty and where to discount me

- I never saw the Eleventh Circuit's opinion or the respondents' view; CourtListener returned no hits for the decision below (two searches), so my account of the reasoning below is the petition's own, which is adverse-party-authored in the sense that it is one side's characterization.
- The corpus `query` calls I ran returned recent stay applications and one relisted paid petition rather than comparable pro se cert petitions, so they gave me no case-level priors; the anchor is the statpack alone.
- The statpack's OT2025 row is this case's own Term and was excluded from the pool per the leakage rule; OT2026 is empty.
- Mode is forward; the case is genuinely pending (distributed for Sept. 28, 2026) and no retrieval surfaced a disposition.
