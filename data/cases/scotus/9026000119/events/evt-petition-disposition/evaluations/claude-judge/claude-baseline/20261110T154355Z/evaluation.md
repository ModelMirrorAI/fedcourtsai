# Evaluation — claude-baseline

**Cell.** Cert stage, `moment: distribution`, forward mode. Guam v. Ybanez, No. 26-119. Outcome: petition **denied** Nov 9, 2026. That was a clean first-conference denial after the single distribution for the 11/6/2026 conference: no response request, no CVSG, no relist and no noted dissent. `actual_granted` = 0. The segment base rate and skill score are harness-stamped. I have not pooled or quoted a rate of my own; any comparison should use the stamped segment base rate. Votes are not scored on a cert cell. No semantic set is declared, so this cell carries no `semantic_grades`.

**Scores.** Predicted `denied` at P(grant) = 0.04, so `correct` = 1 and Brier = 0.0016.

**Reasoning quality: 0.75.** The rationale names the right reasons a cert grant was unlikely. The QP asks the Court to "extend" an unspecified settled doctrine and names no split. The dispute is local and fact-bound. The orders below are unreported and may rest on Guam-law ethics grounds, which raises an adequate-local-ground and preservation concern. The Court had shown no interest before conference. It is also candid about what it did not read: it skipped the appendices, so its local-ground point is inference rather than verified. It explains plausibly why it stayed off 1–2%: a government petitioner can draw a response call or a summary vacatur. The main shortfall is depth. A reader of Appendices C–D would have seen the notice/deadline history and the trial court's screening findings, and those sharpen the vehicle problems considerably.

## Predicted reasoning

**Grade: 0.55.** Central claims: (1) denial at the first conference, (2) no relist, (3) no CVSG and (4) no separate writing. All four were borne out by the docket and outcome signals. It also committed to the specific point that the likelier deviation would be a call for a response, followed by denial anyway. No response was called for, which is consistent with its modal path. The conditional QP reformulation and summary-route content earn neither credit nor penalty, since no grant happened. The document is correct but mostly reads off the modal path for a weak, unopposed petition, which a competent reader would rarely call otherwise. That keeps it slightly above the "right but generic" anchor rather than near the top.

## Leakage

Forward log with capture coverage 1.0. The only external call was a CourtListener docket search for related case 26-264, which returned 0 results. The rest were statpack and record reads, plus a final write of its own output. Nothing dated on or after the resolution, no query for this petition's disposition, and no `data/qp-topics/` read. `not_applicable`; not suspected.
