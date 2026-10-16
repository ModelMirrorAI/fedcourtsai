# Basis for the forecast

**P(any grant) = 0.025; predicted disposition: denied.** This is a cert-arrival forecast, not a prediction of the merits of the civil action.

## Record and information boundary

I read the provisioned `2026-10-16.json` snapshot, `context.json`, event definition, `documents.json`, questions presented, and selected substantive portions of the petition, including its reasons for review and the attached Sixth Circuit opinion. The context identifies a forward cell, a date cutoff of October 16, 2026, OT2026, `baseline` under `sal-v4`, zero distributions, and no CVSG. The snapshot records filing on October 9, docketing on October 15, and a response due November 16, 2026. Absence of a distribution is the arrival moment's defining condition, not evidence of rejection or missing proceedings.

The manifest dates document retrieval to October 15, 2026. It marks the petition as truncated but not text-empty. The questions presented, petition's reasons for review, and the appellate opinion's relevant grounds are available in the supplied text. I did not assume the remainder of the appendix was complete. No brief in opposition is provisioned; I therefore cannot assess respondents' actual Supreme Court arguments. The attached appellate opinion supplies a useful counterweight to petitioners' characterization, but is not a substitute for a BIO.

I did not retrieve this petition's current docket, disposition, subsequent history, other predictions, or outcome artifacts. I have no known prior knowledge of its Supreme Court outcome. External legal retrieval concerned only Chiaverini, a preexisting precedent. General web requests returned no visible source material and supplied no evidence.

## Base-rate anchor

The petitioners are private parties and the filing is paid. The appropriate arrival anchor is the `baseline` class floor's bracketed **reached** rate, not the terminal baseline rate, the federal/state caption classes, or the terminal zero-relist bucket. The committed `metrics/statpack.md` uses `sal-v4`, matching the context.

I pooled every displayed prior-Term baseline risk set, OT2017–OT2025, excluding OT2026. The displayed reached percentages and weighted denominators are: 2017 4.7%/1,643; 2018 4.6%/1,524; 2019 4.6%/1,399; 2020 4.5%/1,739; 2021 5.6%/1,500; 2022 5.8%/1,192; 2023 5.9%/1,312; 2024 5.7%/1,271; 2025 3.9%/1,297. Weighting these displayed rates gives approximately **5.00%**, with total weighted resolved denominator **12,877**. This is an approximation from rounded table cells, not an exact grant count. These are the checkout's committed statistical estimates, not a freshly queried corpus; no corpus-wide pull/snapshot vintage was established and I make no current-corpus coverage claim.

I also read the paid-segment relist and CVSG cuts. They describe terminal populations, not forward transition probabilities. In particular, the higher grant share among CVSG petitions does not estimate this petition's chance of receiving a CVSG, and the zero-relist row is not an arrival anchor. My increment probabilities are judgmental forecasts, not rates purportedly measured by those tables.

## Case-specific adjustment

The petition raises a serious accountability concern: petitioners allege that officials knowingly omitted the visitation-period element of Tennessee's custodial-interference statute to prosecute conduct that was not criminal. Its three questions concern reasonable legal error and probable cause, prosecutorial immunity, and the treatment of pleaded facts and unbriefed grounds. These concerns, a published appellate opinion, and the national reach of immunity doctrine keep the forecast above a negligible probability. Sources: questions-presented text; petition pp. 4–8, 24–37; appendix pp. 1a–20a.

The most important downward adjustment is the **independent-ground problem**. The panel says it need not conclusively decide whether the statutory interpretation was reasonable because individual defendants receive immunity on other grounds. It then relies on absence of clearly established law for officers and the child-services attorney, and the advocacy function of drafting an indictment for prosecutors. It additionally gives qualified-immunity treatment to any investigative-conspiracy theory. The municipal claim fails on final-policymaker grounds. Thus a victory on the petition's headline Heien argument would not automatically change the judgment. Sources: appendix pp. 11a–19a, 20a.

Second, the petition's claimed conflict is not presented as a developed, contemporary inter-circuit split on materially identical facts. Its first section invokes disagreement discussed in Heien and argues that the result undermines Thompson and Chiaverini. That is a less compelling review vehicle than competing post-Heien appellate holdings resolving the same immunity question differently. This is an assessment of the supplied petition, not a claim to have exhaustively searched for splits. Source: petition pp. 24–28.

Third, Chiaverini's rejection of a categorical bar based on another valid charge does not itself decide these distinct immunity grounds. I checked the Supreme Court's June 20, 2024 opinion through CourtListener: Chiaverini v. City of Napoleon, 602 U.S. 556, 558–59 (2024). The provisioned panel opinion does not apply the invalidated any-charge rule. Treating Chiaverini as a direct mandate for a GVR would overstate the analogy.

Finally, the prosecutorial question turns on the functional characterization of particular acts. The panel expressly applies Buckley's distinction between advocacy and investigation rather than openly rejecting it. Petitioners dispute that application and the pleading treatment, but this makes the requested review partly an error-correction exercise. Sources: petition pp. 28–35; appendix pp. 16a–19a. I give the alleged intentional misconduct genuine weight without adopting it as an adjudicated finding or assuming it defeats every immunity defense.

Together these considerations reduce the roughly 5% class-floor anchor to **2.5%**. This is a qualitative adjustment, not a fitted likelihood ratio. The missing BIO and incomplete appendix constrain confidence; neither warrants inventing a procedural defect or a split.

## Other judgments

The 0.97 distribution increment reflects the ordinary next procedural step from zero, while the modal path is no second distribution. The very low CVSG probability reflects the absence of a case-specific reason to seek federal views, not merely the absence of a federal party. The 0.25 summary-route probability is conditional on a grant: no identified intervening decision supplies a straightforward remand trigger. The 0.04 denial-writing probability allows for concern about immunity without predicting a separate writing as likely.

The **0.42 stakes score** is separate from grant likelihood. A broad ruling could affect national civil-rights remedies against several classes of officials; the actual vehicle remains a relatively localized, fact-dependent dispute, without a supplied basis for calling it a major national policy controversy.
