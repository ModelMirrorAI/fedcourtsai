# Why P(grant) = 0.06

## What I read

Provisioned inputs: the snapshot `record/snapshots/2026-10-09.json`, `record/context.json` (mode `forward`, band `baseline` under sal-v4, `distribution_count` 1, no CVSG, Term 2026, paid docket), `record/documents/questions-presented.txt`, and `record/documents/petition.txt` (180 pages, `truncated: true`, but the full petition body and Appendix A, the Second Circuit's summary order, were inside the extracted text; the truncation cut only the later district-court appendices). No brief in opposition exists: respondent filed a waiver on October 5, 2026. Beyond the provisioned inputs I used the committed `metrics/statpack.md`, one `fedcourts query` for the shape of recent SCOTUS priors, and CourtListener for the Second Circuit's docket, the Eleventh Circuit's Lapham opinion, and the Second Circuit's November 2025 Haran opinion (see `retrieval.md`). I did not retrieve anything about this petition's own disposition.

## Anchor

The context freezes band `baseline` under `sal-v4`, which matches the statpack's band table version. Pooling the bracketed `reached` figures for `baseline` over the nine rendered Terms strictly before 2026 (OT2017 through OT2025, weighted n ≈ 12,900) gives roughly **5.0%**. That is the rate a once-distributed private paid petition faces, and the yardstick the evaluator will score this cell against. The modern-cert headline (granted 1.5% plus GVR 1.3% of resolved) and the relist-0 bucket (granted 1.2%, GVR 0.5%) are terminal-state figures that understate a live petition's prospects, so I did not anchor on them. The Second Circuit's originating-court cut (granted 2.6%, GVR 2.4%) sits slightly above the circuit average but adds little beyond the band.

## Adjustments up

- **The split is real and acknowledged.** The petition documents a 5-2 split with two internally inconsistent circuits, and quotes recent panels in the Third, Fifth, and Seventh Circuits calling the question open after Loper Bright. This is not a manufactured conflict.
- **The legal hook fits this Court.** The motivating-factor side rests on Chevron deference to 29 C.F.R. 825.220(c); the but-for side rests on Nassar, Gross, and Comcast. The Court has repeatedly treated but-for causation as the default, and Loper Bright invites exactly this kind of re-examination.
- **Counsel and presentation.** A Steptoe petition with a clear QP and a vehicle section that anticipates the preservation objection is well above the baseline band's median petition.
- **Recurring, high-volume claim.** FMLA retaliation is litigated constantly, and the standard decides summary judgment and jury instructions.

Taken alone, these would put a baseline-band petition in the 15-25% range.

## Adjustments down

- **The question was not decided below.** The Second Circuit held the causation argument **waived as invited error** because Radiall itself proposed the motivating-factor jury instruction, and alternatively **forfeited** because Radiall never challenged Woods in the district court and did not raise Loper Bright in its October 2024 post-trial motions even though Loper Bright was three months old. It then reviewed for plain error and found none because the question is unsettled. To reach Question 1 the Court would first have to resolve Question 2, and the invited-error finding is the kind of fact-specific preservation ruling the Court almost never second-guesses (Singleton v. Wulff). United States v. Wells lets the Court reach a question "pressed or passed upon," but it does not make the Court want to.
- **Unpublished summary order.** The decision below is non-precedential and does not bind future Second Circuit panels, so the split is no deeper for it, and the Court routinely treats such orders as poor vehicles.
- **Post-verdict posture.** A $770,000 jury judgment, a good-faith finding, and separate evidentiary and verdict-consistency challenges make the record messier than a summary-judgment vehicle would be.
- **The Court passed on this split in 2024.** The petition itself notes that cert was denied in Lapham v. Walgreen (Eleventh Circuit, but-for side), 145 S. Ct. 162 (2024), after Loper Bright had been decided. That petition came from a published opinion that squarely decided the question. A denial there is not dispositive, but it is evidence the Court is not hunting for this issue.
- **Response waived.** Respondent's waiver is consistent with the low-interest default and means the petition reaches conference with no one pointing out the vehicle problems, which cuts both ways but mostly signals that respondent's counsel expects a denial.

## Net

I split the forecast on whether the Court calls for a response. I put P(CFR) near 0.35, given a professional petition with a real split; conditional on a CFR, P(grant) around 0.14 once the respondent airs the invited-error and summary-order problems; without a CFR, roughly 0.01. That blends to about **0.06**, slightly above the 5.0% anchor: the split and the Loper Bright hook are genuinely strong, but the vehicle is weak in a way the Court cares about, and the invited-error finding is close to disqualifying.

## Other claims

- `relist-increment` 0.40: almost entirely the CFR path, which produces a fresh distribution after briefing; a straight relist off November 6 without a CFR is a small residual.
- `cvsg-increment` 0.05: a federal regulation's deference status is at issue and DOL has taken a side as amicus in the Second Circuit, but a CVSG presupposes a level of interest I do not expect here. The paid-segment CVSG rate is about 1.3%; I am above it for the federal-regulation angle.
- `summary-disposition-route` 0.12 conditional on a grant: no intervening decision supports a GVR; the only summary path is a Davis-style per curiam on preservation, which the invited-error alternative ground makes unlikely.
- `dissent-from-denial` 0.04 conditional on a denial: no Justice wrote on the Lapham denial, and employment-causation denials rarely draw statements.
- `big_case_score` 0.35: a nationwide standard for a common claim and a first post-Loper Bright word on Chevron-era statutory holdings, but technical and low-profile.

## Where to discount me

The two largest uncertainties are (1) how heavily the Court weighs the invited-error ruling against a clean, well-documented split it may eventually want to resolve, and (2) P(CFR), which I cannot observe and which drives most of the relist claim. If a response is called for, my grant number should move up to the 0.12-0.15 range; if the November 6 conference passes with a denial, it was the vehicle. The Haran opinion I retrieved did not address the causation standard, so it neither confirms nor undercuts the petition's claim that the Second Circuit has avoided revisiting Woods; it only confirms that Woods remains the circuit's stated law. The statpack's band table is a same-version match, so no anchoring mismatch flag is owed.
