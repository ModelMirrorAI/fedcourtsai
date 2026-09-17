# Why 0.006

## Anchor

`record/context.json` freezes `band: baseline` under `sal-v4`, Term 2025, `distribution_count: 1`, no CVSG, mode `forward`. The statpack's "Segment base rate by salience band (sal-v4)" table gives the baseline band's bracketed `reached` rate per Term. Pooling the eight rendered Terms strictly before OT2025 (OT2017 through OT2024; the OT2026 row is empty) gives roughly 593 grants over a weighted n of about 11,580, so about 5.1%. The paid scored segment's relist-count cut puts the relist-0 bucket at 1.2% granted plus 0.5% GVR, and the CVSG-none bucket at 4.0% granted plus 2.3% GVR. The modern discretionary-cert base rate is about 2.8% for the grant family. So the anchor for a once-distributed baseline paid petition is about 5%, and I moved a long way down from it.

## Downward adjustments, in order of weight

1. **Respondents waived and the Court did not call for a response.** The Court effectively never grants a paid petition without a brief in opposition. The only grant path is a post-conference call for a response followed by a grant, which compounds two unlikely events. This alone takes most of the anchor away.
2. **The decision below is an unexplained discretionary refusal of original jurisdiction.** The South Carolina Supreme Court's one-page December 16, 2025 order (petition App. 1a, as characterized in the petition) declined to entertain a mandamus/prohibition/injunction petition in its original jurisdiction. Under Key v. Currie, which the petition itself cites, that court ordinarily declines original jurisdiction when the trial courts are available. That is a paradigm adequate and independent state ground and no court passed on any federal question, which is a serious §1257 problem the petition concedes at pages 19–22 and tries to convert into an argument for a Philadelphia Newspapers vacatur.
3. **The federal question was barely presented below.** The petition admits (p. 21) the issue "was not labeled below in the refined terms used now"; the original-jurisdiction petition invoked Nectow through lower-court authority and the words "arbitrary and irrational" alongside a state statutory claim under S.C. Code § 6-29-950. Fair presentation is doubtful.
4. **The petitioner does not fit the split it describes.** Every case in the asserted conflict (Brady, Cine SK8, United Artists, Hillcrest, Lewis v. Brown) involves a property owner or applicant claiming deprivation of its own state-created land-use interest. Citizens Alliance is a neighborhood nonprofit objecting to permits issued to a third party. It has identified no property interest of its own, so even a court in the Second Circuit camp would not obviously recognize its claim. The question presented would not be answered by resolving the split.
5. **The controversy is still live in state court.** The petition and supplemental brief describe the Silfab appeal of the zoning board's ruling, a stayed declaratory action, and other related suits. The Court does not step into a multi-track state land-use dispute through review of an extraordinary-writ denial.
6. **Vehicle and advocacy signals.** Unpublished one-page order; no opinion to review; small-firm counsel (Appellate Counsel, PC, Boston) rather than a repeat Supreme Court advocate; distributed to the long conference, where grant rates are at their lowest.

## Why not lower still

The petition is professionally drafted, the circuit disagreement it describes is real and long-standing (the Second Circuit's ultra vires strand against the conscience-shocking majority and the Eleventh Circuit's categorical bar), and the alternative Philadelphia Newspapers request is a genuine if rarely used device. I keep about half a percent for the combined probability that the Court calls for a response and then vacates for clarification or grants outright. I would not go below about 0.003 given the anchor and the fact that baseline-band paid petitions with a plausible split occasionally surprise.

## The supplemental brief

The September 11, 2026 supplemental brief was on the docket but not provisioned, so I fetched it from supremecourt.gov (see `retrieval.md`). It reports that the York County Court of Common Pleas on July 21, 2026 affirmed the zoning board's ruling that solar-panel manufacturing is prohibited in the LI district, and denied reconsideration on August 27, 2026. It cites only Cine SK8 and Philadelphia Newspapers. It does not report any intervening decision of this Court, so it supplies no GVR basis; it strengthens the state-law predicate for the petitioner's allegation but does nothing about the jurisdictional, presentation, and standing problems above. I treated it as neutral to very slightly positive and it did not move the number.

## The other claims

- **relist-increment 0.09.** From one distribution. The paid-segment relist cut shows about a quarter of petitions carry more than one distribution, an upper bound that includes reschedules. This petition has no hold candidate, no response to await, and no stakes that invite a dissent, so I sit well below that population figure; most of the 0.09 is a mechanical reschedule off the long conference.
- **cvsg-increment 0.003.** No federal interest.
- **summary-disposition-route 0.7 (conditional on grant).** Conditional on any grant, the clarification vacatur the petition itself asks for in the alternative is much likelier than plenary review of a case with no adjudicated federal claim. Read this as P(vacate-and-remand in the cert order | any grant).
- **dissent-from-denial 0.02 (conditional on denial).** Property-rights writings on denial happen, but on clean owner-versus-government vehicles.

## Big case score

0.15. Scored on stakes if decided, not on grant odds. A merits decision on the substantive due process standard for executive land-use action would be significant to local governments and the land-use bar nationally, but the case itself is a single county permitting fight and the realistic dispositions (denial or a clarification remand) decide nothing.

## Inputs and uncertainty

Read: `AGENTS.md`, the prompt, `schemas/prediction.schema.json`, `event.yaml` (kind petition, no `stage` or `moment` recorded, so it reads as cert at the distribution moment), `record/context.json`, `record/snapshots/2026-09-16.json`, `record/documents/documents.json`, `questions-presented.txt`, and the full `petition.txt` (35 pages, clean text). No brief in opposition exists because respondents waived. The petition appendix (including the order below) was not provisioned; my characterization of the order is from the petition's own account. Main uncertainty is whether the Court calls for a response after the long conference; if it does, this number should be revisited upward by an order of magnitude. This is a forward cell and the conference is in the future; no disposition surfaced in any retrieval.
