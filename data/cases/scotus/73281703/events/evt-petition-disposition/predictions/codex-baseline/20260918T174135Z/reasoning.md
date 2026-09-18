# Rationale for the probability

## Information set and posture

This is a cert-stage prediction of the unresolved petition-disposition event, with **P(any grant) = 0.36** and denial as the categorical call. The petition-kind event has no explicit stage; I apply the contract's cert default. I read the case-level `record/snapshots/2026-09-17.json`, `record/context.json`, the event definition, and the provisioned questions presented, petition, brief in opposition, and document manifest. The manifest identifies the petition and opposition as nonempty and untruncated. Page references below use the briefs' printed page numbers.

The frozen context is forward mode, Term 2025, band `elevated`, salience version `sal-v4`, two distributions, and no CVSG. It is an as-stored snapshot with no cutoff. The dated snapshot is the baseline vintage; its latest docket entry is August 26, 2026. I make no claim to have refreshed the case or the live corpus after that record. The September 28 conference remains in the future at prediction time.

The docket records a June 11 request for a response, an August 7 opposition, and an August 18 reply. Only the opposition and petition texts were provisioned; I did not read the reply or separately retrieve the appendix. Thus I can evaluate the opposition against the petition and two historical authorities, but cannot claim to have considered the petitioner's reply to these vehicle objections. No disposition of this petition was retrieved or encountered, and I do not carry a known outcome for this case.

## Anchor and calibration

I use the committed `metrics/statpack.md` as a static aggregate, not a current corpus census. Its salience version matches the context. The private petitioner's frozen elevated band determines the anchor; the school district's presence as respondent does not make this a state-petitioner case.

Pooling every displayed Term strictly before 2025 gives these elevated **reached** rates and weighted denominators:

| Term | Reached grant rate | Weighted resolved n |
| --- | ---: | ---: |
| 2024 | 17.9% | 336 |
| 2023 | 17.5% | 354 |
| 2022 | 19.0% | 300 |
| 2021 | 20.5% | 342 |
| 2020 | 16.1% | 397 |
| 2019 | 13.8% | 334 |
| 2018 | 15.9% | 347 |
| 2017 | 17.5% | 400 |

The executed weighted calculation gives approximately **17.24%**, with denominator **2,810**. This is approximate because the published rates are rounded. I exclude the 2025 and 2026 rows and do not substitute the lower terminal-band rates. The pack does not expose a build timestamp or live-corpus pull vintage in the metadata inspected; these figures describe only the committed pack consulted for this cell, not verified present-day corpus coverage.

The pack's modern-cert disposition counts imply a much lower whole-docket grant-family rate, but that is not the proper selected-cell anchor. Its paid-segment terminal relist cuts report grant-family shares of approximately 1.7%, 13.3%, 40.9%, and 36.8% for zero, one, two, and three-plus relists; the CVSG/no-CVSG cuts report approximately 34.9% and 6.3%. These all-Term terminal-state cuts describe the population's shape, not an as-at-prediction hazard or another independent multiplier. I do not treat a later CVSG or another relist as already observed.

## Why this petition is stronger than the anchor

**There is a concrete statutory conflict, not merely an assertion of error.** The petition, pp. 11–19, identifies opposing interpretations of section 504(d), particularly Flynn and Fleming against Wojewski and the Arkansas decision. The opposition, pp. 11–14, acknowledges the independent-contractor discrimination split while disputing its fit to retaliation. That concession and the alleged express rejection of the competing circuit approach distinguish this petition from ordinary fact-specific error correction. The petition describes a final judgment after trial, rather than the interlocutory posture it attributes to the earlier Fleming petition (petition pp. 3–7, 19–20).

I independently checked the historical Flynn opinion through CourtListener: **Flynn v. Distinctive Home Care, Inc., 812 F.3d 422 (5th Cir. 2016)** squarely permits independent-contractor employment-discrimination suits under section 504. The retrieved discussion of Hiler also cautions that Hiler did not itself involve an independent contractor. Accordingly, the broad conflict is supported, but I do not count every case in the petition's expanded tally as an equally direct holding on this precise question.

**The response request is a real attention signal.** The June 11 request precedes the first scheduled conference. It is more informative than a voluntarily filed opposition, although it does not establish support from four Justices. I retain the harness's elevated band but discount any inference that the two distributions necessarily reflect a substantive relist: the intervening request and briefing provide an administrative explanation for the second distribution. The frozen count remains two for the increment forecast.

**One asserted distinction is weaker than the opposition suggests.** I checked **Redd v. Summers, 232 F.3d 933, 941 (D.C. Cir. 2000)** through CourtListener. Its concluding discussion allows further consideration of section 504 discrimination or retaliation claims despite the Bureau not being the plaintiff's employer. That weakens the proposition that nonemployment status and retaliation necessarily remove this case from the conflict. It does not settle Greer's case: Redd concerned a federally conducted program and the worker's own alleged exclusion, rather than this parent's advocacy for her child against a funding recipient.

## Why denial still leads

**The actual cause of action creates a substantial vehicle risk.** The QP speaks broadly of discrimination against independent contractors. The facts instead concern a staffing company's employee alleging retaliation by a school district for advocacy about her child's disability. The opposition, pp. 11–14 and 17–18, makes that mismatch concrete and raises the antecedent availability of a private retaliation action. Its account of the Arkansas court assuming rather than resolving that issue is a reason a grant might require more than answering the petition's stated employment-status question. I treat the opposition's discussion of Smith as advocacy in a provisioned brief, not as an independently verified holding or current rehearing status. It is not independently decisive to this forecast.

**The separate claims and remedies complicate the vehicle, but are not an automatic jurisdictional veto.** The opposition, pp. 15–16, argues that unchallenged dispositions of the ACRA and section 1983 claims, together with a general damages verdict, prevent meaningful relief. Those grounds concern separate theories. On the materials read, they do not establish that an independent ground necessarily defeats section 504 relief after reversal. A remand could matter even without automatic reinstatement of the entire damages award. I therefore apply a modest vehicle discount, rather than accept the opposition's assertion that the case goes nowhere. The absence of the reply and independently read lower opinion leaves uncertainty about the force of these arguments.

**A longstanding split does not guarantee immediate review.** The petition presents a respectable opportunity to settle the disagreement, but the employment/discrimination/retaliation framing provides an understandable reason to wait for a cleaner vehicle. This combination raises my estimate from the roughly 17% anchor to **36%**, without making grant the most likely outcome. That adjustment is judgment, not a fitted coefficient or an empirically estimated effect of these particular features.

## Remaining claims and significance

The **43%** further-distribution probability balances the real split and requested response against the fact that the September conference is the first listed after full briefing. It forecasts a count above two, not merely the already-recorded second distribution. **10% CVSG** reflects federal administration of the statute, but no government request, invitation, or distinctive federal operational conflict is shown. The record does not justify turning federal statutory subject matter alone into a high CVSG probability.

The **6% summary-route probability is conditional on grant**. I identify no intervening controlling case requiring reconsideration and expect a grant to address the contested statutory interpretation through plenary review. The **10% separate-writing probability is conditional on denial**, aggregate only. Both conditional figures are subjective judgments rather than published matched baselines; no justice-level cert votes are assigned.

The **0.44 stakes score** concerns significance if decided, independently of the 0.36 grant probability. Coverage of nonemployees and disability advocates across federally funded programs extends beyond one substitute teacher's small damages award. Nevertheless, the potential holding is a bounded statutory-coverage rule, not a wholesale constitutional or institutional change.

## Tool limitations

The initial path command failed because the default uv cache was read-only. Re-running with a temporary writable cache and the existing environment succeeded. General web searches for the historical Flynn opinion and Supreme Court Rule 10, and an attempt to open the historical opinion's official PDF, returned no usable content in the tool responses. I relied instead on the provisioned briefs and successful CourtListener historical-opinion lookups. This did not require retrieving the target case's current docket or outcome.
