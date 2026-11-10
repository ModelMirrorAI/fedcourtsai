# Evaluation — gemini-baseline

**Cell:** scotus/73522552 (*Isaacson v. Moses*, No. 25-1411), `evt-order-call-for-response-disposition`, cert stage, moment `response-requested`, forward mode. **Outcome:** petition denied 2026-11-09 (`actual_granted` 0), two distributions in total, no CVSG, no noted dissent or statement. Both respondents filed BIOs on Sep 18, the Chamber of Commerce filed an amicus brief the same day, the petitioner replied Oct 2, and the case was distributed Oct 7 for the Nov 6 conference.

The segment base rate, brier skill score and basis are the harness's to stamp (cert cell, frozen band `baseline` under sal-v4 → risk-set pool). Here I refer only to "the stamped segment base rate" and do not give a figure of my own. Votes are not scored on a cert cell. No semantic set is declared on a cert event, so there is no `semantic_grades` block.

## Score
- Predicted `denied` at P(grant) = 0.06 → `correct` 1, `brier_score` 0.0036.

## Reasoning quality: 0.40
The bottom line was sound and well calibrated. A call for a response on a waived petition is a real but weak signal, and the issue had a long history of denials. Netting those to a mid-single-digit probability was the right call. But the document's grounding has material problems:
- **Base-rate anchor misreported.** The rationale says the sal-v4 band table "renders OT 2024 and OT 2025" and quotes an OT 2024 baseline `reached` rate of 2.1% (n=1,210). I rebuilt the statpack the candidate was placed against (`statpack-at`, build 7bcde3b105cb, digest sha256:84feb679…). It renders ten Terms (2017–2026). Its OT 2024 baseline row is 5.9% reached (n=1,274), and 4.0% reached (n=1,314) for OT 2025. Neither of the candidate's figures appears in the build. The anchor the candidate described does not exist in its input.
- **Unsupported sourcing.** The rationale says "the petition itself candidly catalogues (Pet. 3, 21 & nn. 5, 65)" a list of prior certiorari denials with S. Ct. citations: *Carson v. Hyland*, *Murray*, *Kazman*, *Isaacson v. Toy* (No. 23-908) and *Dart v. Scott*. The staged petition text contains no such catalogue. A search of it for "cert. denied" and the cited reporter pages finds nothing. The candidate's only outside lookups (CourtListener) were throttled, so it verified none of these. The downward adjustment, its biggest driver, therefore rests on authority the document attributes to a source that does not carry it. That may be accurate recall, but it is presented as a record citation.
- **Docket details misstated.** It gives the first distribution as July 29 (the docket says Aug 5) and the NYT waiver as July 22 (July 21). It dates the decision below (*Moses II*) to Dec. 17, 2025, but the petition appendix gives Feb. 10, 2026. It also describes a "10–1" split, while the petition identifies five agreeing circuits.
- The vehicle analysis is good: law of the case, an unpublished summary order, no amici at the time. So is the rest of the analysis.

## Predicted reasoning: 0.70
I treated four claims as central: the procedural path (one more distribution, terminal count 2, denial at that conference, ~15% chance of a real relist), denial, no separate writing, and no CVSG. All were borne out. The path forecast is specific: a CFR could plausibly have led to a relist or a writing, and the document committed against both. Denial itself is the modal outcome and earns little credit as discriminating content. The conditional merits material earns nothing, because the grant never happened. The Jul 29 distribution date is a minor error. Grade: between 0.75 and 1.0 for specificity, held to 0.70 because the main calls are close to the base case.

## Leakage
Forward cell, `not_applicable`. The prediction was placed Oct 29 and the event resolved Nov 9. Retrieval was corpus queries and two throttled CourtListener searches for other cases. Nothing touched this petition's disposition.

## Big case
My own read is 0.35. See the JSON notes.
