# Rationale for the numbers

**P(grant, any form) = 0.015; predicted disposition: denied.**

## Anchor

`record/context.json` freezes this cell as `forward`, `band: baseline`, `salience_version: sal-v4`, `distribution_count: 1`, `cvsg_date: null`, `term: 2025`. The statpack's "Segment base rate by salience band (sal-v4)" table matches the context's version, so the anchor is the `baseline` band's bracketed `reached` rate pooled over Terms strictly before OT2025. Pooling OT2017 through OT2024 as rendered (n = 1271, 1312, 1192, 1500, 1739, 1399, 1524, 1643) gives a weighted grant-family rate of about 5.1 percent (about 5.7 percent over the four most recent Terms). That is the yardstick the evaluator scores this cell against. For shape I also read the relist-count cut (relist-0: granted 1.2 percent plus GVR 0.5 percent among petitions that ended undistributed again), the CVSG cut (none: 4.0 percent granted, 2.3 percent GVR), and the Tenth Circuit row of the originating-circuit cut (granted 2.5 percent, GVR 1.4 percent, which blends paid and IFP).

## Adjustments down from the anchor

I moved from roughly 5 percent to 1.5 percent on the following, in rough order of weight.

1. **The petitioner's textual position is weak on its own facts, so the circuit split does not really reach him.** Section 2244(d)(1) applies to "an application for a writ of habeas corpus by a person in custody pursuant to the judgment of a State court." St. Clair is serving Oklahoma life-without-parole murder sentences; he is in custody pursuant to a state judgment however the petition is captioned. The Seventh Circuit's Cox v. McBride line concerns administrative (disciplinary) custody, and even that rule would not obviously help him. The petition's reliance on Bowe cuts the other way: Bowe's syllabus (read via CourtListener) reasons that § 2244's strict requirements are ones Congress aimed at state prisoners, and its holdings concern § 2244(b)(1) and § 2244(b)(3)(E) for federal prisoners' § 2255 motions, not § 2244(d) or § 2241. The Court does not grant to resolve a split whose minority position would not change the petitioner's result.
2. **Poor vehicle.** The decision below is an unpublished Tenth Circuit order denying a certificate of appealability (Appendix A per the petition; the CourtListener RECAP docket for No. 24-7090 confirms a COA termination on October 17, 2025). The Court rarely reviews COA denials. The E.D. Okla. order in the companion case (No. 6:24-cv-00275, March 24, 2026, read via CourtListener) records that both federal courts found the petitions untimely even under the most petitioner-friendly trigger, § 2244(d)(1)(D), with no statutory or equitable tolling. That makes the threshold question dispositive, which is a point for the vehicle, but it also shows the underlying custody claim, that an executive agreement between two governors entitles him to release from his Oklahoma sentences, is one no court has found colorable.
3. **Docket signals are the weakest kind.** One distribution, for the September long conference; no response or waiver entry on the snapshot; no amici; counsel is an Oklahoma criminal-defense practitioner rather than a Supreme Court specialist; the petition is fifteen pages with a thin authorities table.
4. **The split is old and the Court has passed on it for two decades.** The circuit decisions the petition cites run 2002 to 2006. Nothing in the record suggests the Court has been waiting for a vehicle.

## Adjustments up

Small. The petition is paid (the anchor already conditions on that), presents a genuine statutory question with a real if shallow split, and the timeliness question is outcome-determinative. Together these keep me above the relist-0 bucket's 1.7 percent grant-family figure only marginally; I land at 1.5 percent because the vehicle problems in items 1 and 2 dominate.

## The other claims

- **relist-increment 0.12.** The snapshot shows exactly one distribution (June 24, 2026, for the September 28, 2026 conference). The statpack shows roughly a quarter of paid scored petitions carry at least one relist terminally, but that population is enriched for strong petitions and includes reschedules. For a baseline-band petition with no response and the weaknesses above, I expect disposition on the first list; the residual covers a reschedule or a call for a response that produces another distribution.
- **cvsg-increment 0.01.** No federal interest; state habeas.
- **summary-disposition-route 0.35 (conditional on grant).** The petition asks for a GVR in light of Bowe in the alternative, and a grant of this weak a petition would more plausibly be a docket-clearing GVR than a plenary grant. Against that, Bowe does not bear on § 2244(d) or § 2241, so an intervening-decision GVR would be doctrinally odd. The prior Terms' cert-order share of grants (roughly 30 to 59 percent where the label is populated) brackets my number.
- **dissent-from-denial 0.02.** No Justice has signaled interest in this question; the decision below is unpublished; the underlying claim is weak.

## Stakes

`big_case_score` 0.2. The legal question has systemic reach for habeas practice if decided, but this case's facts are idiosyncratic and the decision below is unpublished, so a resolution would be narrow and lightly covered.

## Where to discount me

- I could not read the Tenth Circuit's COA order itself (unavailable on CourtListener; the petition's appendix was not provisioned). My read of its ground is from the petition's description and the March 2026 district court order's summary of it.
- The snapshot carries no waiver or brief in opposition. If a waiver was filed and not captured, nothing changes; if the State filed a BIO that the poll missed, that would slightly raise the relist probability but not the grant probability.
- The respondent title on the snapshot header (Willis Pettit, Warden) differs from the petition caption (Christe Quick, Warden), consistent with a substitution of warden. I treated it as immaterial.
- The one `fedcourts query` I ran (court scotus, era 2020s, disposition granted) returned recency-ranked recent grants and stay applications with no topical overlap; it did not inform the number. Corpus retrieval has no text or topic filter for SCOTUS rows, so priors on this statutory question came from CourtListener and the provisioned petition rather than the corpus.
- Mode is forward and the conference is September 28, 2026, after this run, so nothing I retrieved touches the outcome.
