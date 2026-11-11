# Evaluation — gemini-baseline

**Cell.** Cert stage, `moment: distribution`, forward mode. Guam v. Ybanez, No. 26-119. Outcome: petition **denied** Nov 9, 2026. That was a clean first-conference denial after the single distribution for the 11/6/2026 conference: no response request, no CVSG, no relist and no noted dissent. `actual_granted` = 0. The segment base rate and skill score are harness-stamped. I have not pooled or quoted a rate of my own; any comparison should use the stamped segment base rate. Votes are not scored on a cert cell. No semantic set is declared, so this cell carries no `semantic_grades`.

**Scores.** Predicted `denied` at P(grant) = 0.01, so `correct` = 1 and Brier = 0.0001.

**Reasoning quality: 0.5.** The conclusion is right and two of the three reasons are sound: no national importance and no split, and no amicus support. The weak-federal-question point gets at something real, since Guam's claim against its own courts is largely structural and local. But it is framed loosely. It argues from Fourteenth Amendment due process for states, while the petitioner is a territory proceeding under the Organic Act, and the rationale never engages that statute. The rationale also overstates the record when it says "the respondent has explicitly waived". Only one of several respondents waived, and it treats that waiver as a signal of weakness without qualification. The analysis rests on the QP and the opening of the petition. It shows no engagement with the lower-court orders, so it misses the concrete vehicle problems: the notice and deadline history, the screening findings and preservation. The 0.01 is lower than the generic reasons strictly support for a government petitioner. It happened to be the best Brier here, but the rationale does not show why the probability should be that low.

## Predicted reasoning

**Grade: 0.6.** Central claims: (1) outright denial at the first conference, (2) no relist and no call for a response, and (3) no CVSG. All were borne out. It committed a little more firmly than the others by ruling out a response request, and that held. Its conditional merits content (no structural protection, or a DIG) is unresolved because no grant occurred. It is still mostly the modal path, so the grade is only modestly above the generic anchor.

## Leakage

Forward log with capture coverage 0.0. Every call is unobserved, so I graded each on its query. There was one topical CourtListener search ("entire office" disqualification prosecutor), one failed `fedcourts query` and reads of the provisioned record and statpack. There was no query for this caption, docket or disposition, and no `data/qp-topics/` read. `not_applicable`; not suspected.
