# Rationale

P(any grant) is **0.90**, with an ordinary grant for briefing and argument the modal disposition. This is a cert-stage arrival prediction, not an immigration-merits prediction.

## Baseline and conditioning state

I read the event definition and the provisioned `record/snapshots/2026-09-21.json`. The snapshot records the petition's filing on September 21, 2026, an October 21 response deadline, and a paper-only filing instruction. It contains zero distributions and no CVSG. `record/context.json` freezes forward mode, the federal band under sal-v7, Term 2026, and a date cutoff of September 22. The baseline is the arrival record, not an inference that later activity never occurred. I did not retrieve this petition's disposition or subsequent Supreme Court history.

The frozen cert anchor is **0.7311320754716981**. This is the appropriate caption-class arrival population: federal officials represented by the Solicitor General, not private petitioners. The statpack's strictly prior displayed federal-band rows, Terms 2017–2025, total weighted n=212 and reproduce approximately 73.1%. I exclude the Term 2026 row. The fixed federal caption class means its terminal and reached rates coincide; no selection on future relisting is required.

For scale only, the whole modern-cert table has 638 grants and 637 GVRs among 45,084 resolved petitions, about 2.83%. That is the wrong anchor here. Likewise, the paid-segment terminal relist-zero bucket has n=10,204 and about 1.8% grants plus GVRs: it describes where petitions ended, not the future facing this newly filed government petition. The CVSG bucket has n=164 and 34.8% grants plus GVRs, but this petitioner is already the Solicitor General's client; that selected population does not supply this case's CVSG hazard.

## Case-specific evidence and adjustment

The official DOJ petition, cover, questions presented, and printed pp. 1–3 and 17–27, seeks certiorari before judgment as a replacement for Genalo v. Black. Black previously received review but became moot. The government presents the same two constitutional questions about prolonged detention under 8 U.S.C. 1226(c) and the government's evidentiary burden at bond hearings. The petition alleges continuing circuit disagreement. These are the government's representations, not an independent merits finding.

The strongest upward adjustment is demonstrated prior interest in the same questions, rather than speculation about political salience. I move about seventeen percentage points above the federal anchor. The retrieved Second Circuit record in 26-1396 corroborates an unresolved appeal and a September 2 government motion for summary affirmance; it does not establish an appellate judgment. I therefore do not treat this as ordinary review of a completed Second Circuit judgment or confuse that lower-court motion with the Supreme Court's eventual route.

The before-judgment posture and the replacement history also supply the main downside: vehicle stability matters, and I lack opposition text testing the government's presentation. The 0.90 is consequently not certainty. Mootness or another vehicle problem can defeat a petition even where the Court wants the legal issue. I have no known or inadvertently encountered outcome for this petition.

## Other probabilities

- **Further distribution, 0.99:** the claim starts from zero. A first distribution satisfies it; it is not a 99% prediction of a true post-conference relist. My modal path is one initial distribution and zero or one additional distributions before the petition order.
- **New CVSG, 0.001:** an invitation adds little where the Solicitor General already signed the petition. This is a judgment, not the terminal CVSG table's rate.
- **Summary route given a grant, 0.07:** demonstrated interest in plenary consideration favors briefing and argument. The record does not identify a new controlling merits decision disposing of these questions.
- **Writing given denial, 0.12:** an unexplained denial remains likelier than an explanatory writing even on that less likely branch. The order-writer numbers are unconditional, independent probabilities, not cert votes or a distribution summing to one; they include writings on either disposition branch.

The stakes score of 0.82 concerns the liberty interests and nationwide governmental practices implicated, not the 90% review probability.

## Limits and tooling

No petition, opposition, questions-presented extract, lower-court opinion, or document manifest was provisioned. `same-question.json` has `petitions: null`, which means no QP-based match was available, not that there are no related legal questions elsewhere. I recovered the official petition externally and verified its text with the project's pinned PDF extractor. I did not recover an opposition or independently read a separate lower-court opinion. This remaining paper-only visibility limitation is recorded in `flags.json`.

The structured corpus sweep supplied three grant-selected examples, not an unbiased frequency sample; I did not estimate probabilities from their proportion of grants. A separate docket lookup confirmed Black's earlier grant, not its later termination. The official petition is the source for its replacement history. All retrieval attempts, including unsuccessful searches and CLI errors, are listed in `retrieval.md`. The initial `uv` cache permission error was resolved by setting `UV_CACHE_DIR=/tmp/uv-cache`; no packages were installed.
