# Rationale for the probabilities

## Inputs and information boundary

This is a cert-stage forecast of the petition's disposition, not a merits judgment or an interim application. I used the event definition, the case-level snapshot `2026-09-17.json`, the provisioned questions presented, the substantive arguments and relevant procedural passages in `petition.txt` and `brief-in-opposition.txt`, their `documents.json` inventory, and `context.json`. The inventory reports both briefs as complete, nonempty, and not OCR-derived. The snapshot records a September 3 reply, but its text is not provisioned and I have not read it. Statements about the parties' positions below are attributed advocacy, not independently established findings about the alleged diversions.

The frozen context specifies forward mode, sal-v4, elevated band, Term 2025, two distributions, and no CVSG. Its cutoff is null; I used the supplied latest snapshot rather than pretending it stopped at the first distribution. The snapshot is dated September 17, 2026, and its source creation date is September 16. I did not retrieve this petition's outcome, later docket, or subsequent history, and I do not know its outcome. External retrieval was confined to the 2023 precedent Arizona v. Navajo Nation; the complete lookup record is in `retrieval.md`.

## Quantitative anchor

The committed `metrics/statpack.md` uses sal-v4, matching the context. I pooled every displayed Term strictly before the case's Term 2025, using the elevated band's bracketed **reached** figures, not its terminal-band figures:

| Term | Reached grant rate | Weighted resolved denominator |
| --- | ---: | ---: |
| 2017 | 17.5% | 400 |
| 2018 | 15.9% | 347 |
| 2019 | 13.8% | 334 |
| 2020 | 16.1% | 397 |
| 2021 | 20.5% | 342 |
| 2022 | 19.0% | 300 |
| 2023 | 17.5% | 354 |
| 2024 | 17.9% | 336 |

Weighting the displayed, rounded rates gives approximately **17.24% over weighted n=2,810**. This is an approximate reconstruction, not an exact unrounded estimate. I exclude the 2025 and 2026 rows. The pack's whole modern-cert population has an approximately 2.82% grant-family rate from its displayed counts, but that is background only, not the selected elevated petition's anchor. The latter population is the relevant starting point.

The paid-segment terminal relist buckets show grant-family shares of approximately 1.7%, 13.3%, 40.9%, and 36.8% for zero, one, two, and three-plus relists. The CVSG cut shows approximately 34.9% with a CVSG and 6.3% without. These are terminal, pooled descriptive cuts, not transition probabilities from today's state. In particular, the pack itself cautions that an additional distribution can reflect rescheduling before consideration. I do not equate the 13.3% terminal one-relist rate with this petition's forward probability or use any bucket as a direct hazard estimate.

These figures describe the committed pack available in this checkout, whose last modifying commit is dated September 14, 2026. I did not query a live corpus blob and cannot certify its newest pull stamp or newest stored snapshot; the commit date is artifact vintage, not a substitute for corpus-wide freshness. The case-specific evidence is the provisioned September 17 snapshot.

## Why reduce the anchor to 6%?

**The second distribution is weaker evidence than a substantive post-briefing relist.** The May 27 response request intervened just before the first scheduled conference, and the second distribution followed completion of briefing. That sequence shows real judicial interest but can arise from obtaining the response needed for consideration, without any demonstrated repeated consideration of a fully briefed petition. I retain the harness's elevated classification while discounting the apparent relist signal on its facts. The requested response keeps the forecast meaningfully above a routine unsupported petition; it does not outweigh the vehicle problems.

**The petition presents a meaningful boundary question, but not a demonstrated split.** Questions 1 and 3 and petition pages 15–24 distinguish protecting existing water from affirmatively securing new water. The Tribe invokes Hopi, Ute, White Mountain Apache, Winters, and the Secretary's control under section 152.22 to support a compensable protective duty. This is the strongest reason not to dismiss the petition as merely fact-bound: its proposed rule could affect remedies for other tribal resources. Nevertheless, the developed comparisons are primarily to Supreme Court authority and decisions within the Federal Circuit, rather than conflicting inter-circuit holdings requiring resolution. The opposition expressly disputes any conflict (BIO pages 11–12).

**The government has a substantial answer on the source of the duty.** BIO pages 12–20 distinguish the existence of reserved water rights from a textual federal obligation to police third-party interference and from a money-damages remedy for failure to do so. Its response to section 152.22 is particularly concrete: a restriction on conveyances with Secretarial approval is not obviously an affirmative enforcement duty, and the water claim is not an allegation that the government approved a conveyance of the relevant right. Its discussion of Ute identifies a specific irrigation-infrastructure statute rather than a general new-water/existing-water distinction (BIO page 18 n.2). These are advocacy positions, but they make this an uncertain vehicle for expanding the doctrine.

The independently retrieved passages of **Arizona v. Navajo Nation, 599 U.S. 555, 558–59, 563–66 (2023)** confirm both sides of the doctrinal tension: the majority distinguished the absence of alleged federal interference, but also required duties grounded in the governing legal text and rejected automatically importing private-trust duties. I infer that third-party diversion leaves the Tribe needing an additional argument for why federal inaction breaches a specific protective duty. I do not treat Arizona as already deciding this petition or conclusively rejecting every existing-water claim. The CourtListener opinion lookup corroborates the precedent quoted in the briefs rather than supplying case-specific later information.

**Independent jurisdictional obstacles substantially reduce vehicle quality.** The government's account identifies three CFC dismissal grounds: no qualifying substantive duty, overlapping litigation under 28 U.S.C. § 1500, and the six-year limit under § 2501 (BIO pages 9–11, 21–24). It states that the Federal Circuit did not reach section 1500 for the water claim after affirming on the substantive-source ground. I therefore do not misdescribe all three as appellate holdings. Even so, the government's preserved alternative grounds mean that answering the proposed water-duty question favorably might not rescue the claim. The petition's questions focus on the water duty, not on clearing those separate obstacles. The unavailable reply is important uncertainty because it may answer those objections more effectively than the petition does.

Combining these considerations produces **P(any grant)=0.06**, an approximately eleven-percentage-point reduction from the matched reached-band anchor. This is a judgmental adjustment, not a fitted model or a claimed measured effect. The uncertainty is primarily whether the Court regards the asserted distinction as sufficiently important to overcome this vehicle, not whether the Tribe's alleged resource loss is serious.

## Other probabilities and stakes

- **Further distribution: 0.25.** The requested response and doctrinal sensitivity leave a meaningful possibility of closer consideration or preparation of a writing. The modal path remains disposition after the first scheduled conference with completed briefing. This estimates an increment beyond two distributions, not the chance the petition ever relists.
- **New CVSG: 0.005.** The Solicitor General already represents the respondent and has filed the requested opposition. A request for that response is not a CVSG, and I do not recode it as one.
- **Summary route given grant: 0.10.** No intervening controlling ruling or conceded error appears in the materials consulted. The issue would more naturally receive plenary review if taken; the small residual covers a summary corrective disposition. This is a conditional probability, not 0.10 times the grant probability.
- **Writing given denial: 0.14.** The existing-resource distinction could attract a statement, but the specific-duty and alternative-jurisdiction obstacles favor an ordinary denial. This is the conditional probability of an aggregate public writing, not a prediction of hidden votes.
- **Big-case score: 0.57.** The alleged loss of the homeland's water supply is highly consequential to the Tribe, and a broad protective-duty ruling could affect federal tribal-trust liability nationally. The narrower damages and jurisdictional posture moderates the systemic score. It is independent of the 6% grant assessment.

No votes are supplied because this is a cert petition, not a merits event, and the record gives no basis for a reliable public lineup. The external web search and direct official-PDF attempt returned no usable content; the CourtListener precedent lookup succeeded. Neither failure prevented a record-based forecast, and neither exposed an outcome.
