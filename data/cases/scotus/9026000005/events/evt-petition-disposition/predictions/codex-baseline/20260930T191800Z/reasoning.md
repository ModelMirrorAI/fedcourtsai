# Rationale

## Information set

This is a forward, cert-stage, distribution-moment forecast of docket 26-5, not the earlier cert-before-judgment petition or the stay application. I read the case-level snapshot `record/snapshots/2026-09-30.json`, the event definition, `record/context.json`, the questions presented, the petition, and the brief in opposition. The document manifest reports 29 petition pages and 12 opposition pages, neither truncated nor text-empty. No reply, supplemental brief, lower-court opinion body, or Slaughter opinion body was provisioned. Their absence from this input is not proof that none exists elsewhere.

The frozen context supplies sal-v4 band `elevated`, Term 2026, two distributions, and no CVSG. The snapshot records an August 5 distribution for September 28, an August 13 response request after the government's waiver, the September 14 opposition, and a September 30 distribution for October 16. I use the harness's band without reclassification. Two distribution entries do not establish two completed substantive conferences: the intervening request for a response can account for rescheduling. This makes the trajectory less striking than a clean post-conference relist. No disposition of this target petition was sought or encountered.

## Baseline and adjustments

The committed `metrics/statpack.md` sal-v4 table is the appropriate starting population, not all cert petitions and not a government-petitioner population merely because the President is respondent. Pooling all rendered Terms strictly before 2026, namely 2017–2025, and using the elevated band's bracketed reached denominators gives 521 grant-side outcomes / 3,085 weighted resolved petitions = 0.1688817. I calculated this from the corresponding `prefix_est_grant_rate` and `prefix_weighted_resolved` fields in `metrics/statpack.json`, avoiding rounding of the displayed percentages. The leading terminal-band rates are not the anchor.

These are figures from the committed statpack available to this cell, not a newly refreshed corpus query. The pack does not expose a build timestamp or corpus-wide newest-pull/newest-snapshot vintage in the material read. I therefore make no claim that its population is current to September 30. The target information set is specifically the provisioned September 30 snapshot; its corpus row's separate last-pulled stamp was not retrieved.

The paid-segment relist cut reports grant plus GVR shares of about 1.7% at terminal relist 0, 13.3% at 1, 40.9% at 2, and 36.8% at 3+. The CVSG cut reports about 34.9% grant-side with a CVSG and 6.3% without. These are terminal population descriptions, not forward probabilities of another distribution or a new CVSG. They justify taking procedural attention seriously but do not override the reached-band anchor or supply increment baselines.

My final P(any grant) is 0.12, below the 0.1689 anchor for these reasons:

- The petition's strongest argument is agency specificity, not just disagreement with removal doctrine. QP 1 and petition pages 15–18 emphasize that the General Counsel prosecutes while the Board adjudicates, and that Board orders require judicial enforcement. QP 2 argues for severing any residual executive functions rather than tenure protection. Those are intelligible grounds for a GVR or a narrower follow-on case.
- The petition was filed June 27 and anticipates an imminent Slaughter decision. The later opposition, pages 3–7, reports that Slaughter overruled Humphrey's Executor, characterizes administrative enforcement adjudication itself as executive power, and treats severance of removal restrictions as the remedial rule. If that account is accurate, the new decision strengthens rather than undermines the result below. Mere intervening precedent is not enough to make a GVR likely.
- The opposition, pages 3 and 7, also reports denial of Harris v. Bessent on June 30, 2026, after Slaughter. Harris involved the MSPB portion of the consolidated lower-court litigation and a related adjudicatory-agency argument. That is a strong related-case signal against needing a plenary NLRB case, though a denial supplies no merits holding and differences between agencies remain relevant.
- The requested opposition and second distribution keep the forecast above a routine low-interest denial. The government's own alternative request for a grant and summary affirmance also matters: the forecasted binary is any grant, not whether Wilcox obtains favorable relief. I retain meaningful grant probability even while expecting her substantive theory to fail to attract review.

For internal coherence, an illustrative allocation is 0.875 denial, 0.005 dismissal/withdrawal, 0.060 grant with summary affirmance, 0.042 GVR, and 0.018 plenary grant. The grant-side total is 0.12 and the cert-order share conditional on grant is 0.102 / 0.12 = 0.85. These are subjective allocations, not additional harness claims. Summary affirmance is expressly not labeled summary reversal.

## Other probabilities and stakes

The 0.30 further-distribution probability reflects a live request for consideration, possible preparation of a summary disposition or separate writing, and the fact that the second listed conference is still ahead. It is moderated by the rescheduling ambiguity and by the related ruling's apparent force. My modal forecast is zero additional distributions, with one or two in the alternative. The 0.005 CVSG probability reflects the Solicitor General's existing participation for respondents, not an inference that a missing CVSG is itself adverse. The 0.35 dissent-or-statement probability is conditional on denial and concerns aggregate recorded existence only; significant institutional stakes can draw an objection even when another plenary case is unlikely.

The stakes score of 0.88 concerns national labor adjudication and presidential control over independent adjudicators, not the petition's prospects. The petition's account of consequences for workers, employers, and unions supports a high score, while the related precedent makes this less novel than a first resolution of the removal question.

## Limits and disclosure

The central legal development and the Harris disposition come from the provisioned opposition, an advocate's account, not independently retrieved opinions. I distinguish its reported holdings from my judgment that they probably dispose of this petition's asserted distinctions. The lack of a post-Slaughter petitioner submission in the provisioned materials leaves an asymmetry that warrants caution. A materially narrower Slaughter holding would raise my estimate of a GVR or plenary grant.

General-rule web search and official-rules retrieval attempts returned no usable content; they supplied no evidence. I did not query CourtListener or the corpus for this case or its outcome. I have no known disposition of this target petition. The related-case developments and the earlier proceedings recounted in the briefs predate this forward snapshot and are not the event being forecast; their substantial influence is disclosed in `flags.json`.

The paths command initially failed because the default uv cache was read-only; using a temporary writable cache resolved that operational issue without changing repository code or input files.
