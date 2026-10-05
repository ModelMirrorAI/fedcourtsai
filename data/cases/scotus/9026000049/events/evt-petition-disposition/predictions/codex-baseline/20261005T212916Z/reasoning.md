# Rationale for the probability

## Information set

This is the cert-stage distribution cell for **Brenna Bird, Attorney General of Iowa v. Iowa Migrant Movement for Justice, et al.**, Supreme Court No. 26-49. I used the provisioned `record/snapshots/2026-10-05.json`, `record/context.json`, event definition, questions presented, petition text, BIO text, and document manifest. Context specifies forward mode, Term 2026, `sal-v4` band **state**, two distributions, and no CVSG. The baseline has no dated cutoff and ends with the October 5 distribution for October 9. I forecast from that supplied state, without inferring a later disposition or reconstructing an earlier first-distribution record.

The document manifest records a 182-page petition as truncated; its supplied text ends in the appendix at printed page 48a. The petition's argument through its printed page 38 conclusion is present. The 48-page BIO is marked untruncated and nonempty. I read the QPs and the relevant substantive and vehicle arguments on both sides, not every appendix page. The August 26 reply is docketed but not provisioned; I have not read its rebuttal. These limitations reduce confidence, especially concerning the underlying standing record and the full rehearing dissents.

I did not retrieve this petition's outcome, current docket, later litigation history, other predictors' outputs, or labeling artifacts. I do not independently know its disposition. General-law web lookups yielded no usable source text in this session, so no external legal proposition or case development is treated as independently verified. Discussion of other litigation and federal positions below is attributed to the provisioned advocacy, not to fresh research.

## Baseline: 23.63%, not the whole-docket rate

The committed `metrics/statpack.md` uses the same `sal-v4` as the frozen context. Its displayed window is Terms 2017–2026. I pool **all nine displayed Terms strictly before 2026**, using the state band's bracketed **reached** values rather than its terminal-band rates. The exact companion values in `metrics/statpack.json` give:

| Term | State reached weighted resolved | Grant-equivalent numerator |
| --- | ---: | ---: |
| 2017 | 49 | 9 |
| 2018 | 42 | 9 |
| 2019 | 53 | 8 |
| 2020 | 46 | 19 |
| 2021 | 97 | 22 |
| 2022 | 36 | 5 |
| 2023 | 32 | 6 |
| 2024 | 37 | 11 |
| 2025 | 27 | 10 |
| Total | 419 | 99 |

Thus the anchor is **99 / 419 = 0.23627685**. Numerators are computed as each exact reached rate times its weighted denominator; these are the pack's denial-reweighted estimates, not a fresh census. I exclude Term 2026. I do not reclassify this state petitioner into a private-petitioner band based on its distribution count. The committed pack is the version supplied in this checkout; no live corpus was queried and I make no claim that it reflects a newly refreshed corpus. The case-specific snapshot and document fetches are dated October 5, 2026.

The paid-segment relist and CVSG tables supply context, not incremental probabilities: the one-relist terminal bucket is about 13.3% grant-family, the two-relist bucket about 40.9%, and the CVSG bucket about 34.9%. Those cuts include terminal information, pool caption classes and Terms, and cannot replace this cell's strictly-prior state-band anchor. In particular, the pack warns that a rescheduling can add a distribution without a true relist. That warning applies directly to this snapshot, so I do not treat the October 5 entry as evidence that two substantive conferences have considered the case.

## Why increase to 40%?

**Factors raising the chance above the state-band anchor:**

1. **Broad stakes and repeated litigation.** QP 2 concerns state illegal-reentry crimes and state-directed removal, not a narrow evidentiary error. The petition, printed pages 12–14 and 37, describes similar laws in multiple states and pending challenges. The snapshot lists six amicus filings, including a coalition identified as Oklahoma, Florida, and 23 additional states. This is stronger evidence of institutional importance than the caption alone, although amicus volume is not itself proof of a legal conflict.
2. **Federal support below.** The petition, pages 12–13 and 30–31, says the United States supported rehearing and considered Iowa's law complementary to federal enforcement. The BIO, pages 33–34, addresses that position and argues that executive agreement does not settle Congress's preemptive design. Their disagreement makes the federal interest a concrete reason for further consideration or a CVSG. It does not establish that the Solicitor General has supported certiorari in this Court; no such filing is in the supplied docket.
3. **A developed alternative legal theory.** The petition, pages 11 and 22–37, presents the rehearing dissent's objections to facial relief and a preemption rule based on possible conflicts with enforcement discretion. This supplies a plausible reason for Supreme Court interest beyond disagreement over the result. The Court could regard the relationship between federal criminal overlap and immigration-specific preemption as important even without a square split.

**Factors keeping denial more likely:**

1. **The alleged standing split has a substantial vehicle problem.** QP 1 describes plaintiffs threatened only by disavowed enforcement. The BIO, pages 9–14, contends that organizational member David lacks lawful status and remains covered even on the Attorney General's construction. It also distinguishes permission to reenter from lawful status obtained later. The petition disputes what was adequately alleged, including David's location and reentry history, but a fact-sensitive alternative basis for standing makes a clean categorical disavowal ruling less attractive. I treat the claimed nine-circuit conflict as disputed advocacy, not an established split.
2. **Different procedural outcomes are not necessarily a merits split.** The petition, pages 13–14, describes Texas enforcement after standing-based and stay rulings, while the BIO, pages 20–21, argues there is no conflicting merits holding on the preemption question. On this record I cannot equate those different enforcement postures with a square conflict about Iowa's statute. Additional appellate development remains a plausible reason to wait.
3. **The actual statute is more complicated than 'mere overlap.'** The BIO, pages 24–37, emphasizes missing federal exceptions, state removal requirements, limits on abatement, and an alternative field-preemption ground. Those arguments contest the petition's framing and could preserve the injunction even if the Court rejects one broad obstacle-preemption proposition. Federal support for enforcement does not, by itself, eliminate those asserted statutory obstacles.
4. **Rescheduling is weak evidence of sustained interest.** The September 28 rescheduling and October 5 redistribution justify some attention, but not the boost I would give repeated genuine post-consideration relists. There is no CVSG in the snapshot. I do not infer one from a federal brief filed below.

The resulting **0.40** is a judgmental increase of about sixteen percentage points from the 0.2363 anchor, not a fitted model or an additive estimate for each consideration. The large national question, state coalition, and federal interest warrant a material increase; uncertain vehicle quality, lack of a demonstrated square merits split, and the preliminary posture prevent a grant-majority forecast. A small allowance for dismissal or withdrawal remains within the non-grant complement; denial is by far its principal component.

## Other probabilities and stakes

- **Further distribution, 0.58:** priced from the frozen count of two. The complicated standing/preemption interaction and potential federal consultation raise the likelihood of at least one more distribution, without treating rescheduling as a completed relist or converting terminal-bucket rates into hazards.
- **CVSG, 0.30:** federal immigration interests make an invitation credible, but the legal positions are already developed and the Court could deny without seeking another executive submission. This is not the grant rate among cases with a CVSG.
- **Summary route given grant, 0.12:** there is no identified controlling intervening ruling for a GVR; deciding the broad statutory issue would more naturally require plenary review. A narrower standing correction or a later companion development leaves some summary-route probability. This number is conditional, not 0.40 times that probability.
- **Separate writing given denial, 0.30:** the sovereignty and obstacle-preemption dispute makes a statement more plausible than in a routine petition, but an unexplained denial remains more likely. The number concerns existence only and does not predict a recorded vote count.
- **Stakes, 0.85:** independent state immigration enforcement and removal could affect multiple states and many noncitizens, while QP 1 potentially affects pre-enforcement litigation more broadly. This is significance if decided, not a disguised grant probability.

The principal uncertainty is whether enough Justices see this case as a useful vehicle to revisit the boundary of state immigration enforcement despite the alternative standing and preemption grounds. The incomplete appendix and unavailable reply make that uncertainty substantive rather than merely statistical.
