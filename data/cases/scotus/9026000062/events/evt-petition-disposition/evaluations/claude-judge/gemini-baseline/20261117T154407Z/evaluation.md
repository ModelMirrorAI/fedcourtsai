# Evaluation — gemini-baseline

**Cell:** scotus/9026000062, `evt-petition-disposition` (cert stage, *Custodia Bank, Inc. v. Federal Reserve Board of Governors*, No. 26-62). Outcome: **denied** on 2026-11-16 after a single distribution, no CVSG, no noted dissent.

## Scores
- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.08 − 0)² = 0.0064.
- Base rate, skill and claim scores are the harness's; I wrote none. No votes are scored on a cert cell.

## Reasoning quality — 0.50
The legal analysis of why the petition was weak is the most developed in the cell: the conceded absence of a split, the textual case for the decision below (permissive "may receive" in § 342, § 248a(c)(2) as a fee-schedule principle, the § 248c database listing "rejected" requests), the waiver holding the petition does not challenge, the all-or-nothing posture, and the pending rulemaking. The 0.08 it lands on is well calibrated to a first-conference denial.

But the rationale rests its upward adjustments on docket facts the record does not carry. It says eleven cert-stage amicus briefs were filed and lists filers (a State coalition, ICBA, Solana Policy Institute, DeFi Education Fund, America First Legal, Gun Owners of America and others); the docket shows three, none of those names appears anywhere in the staged filings, and it attributes `amicus_briefs: 11` to `context.json`, where the candidate's own frozen context shows that field null. It says both respondents waived and the Court called for a response on August 13, 2026, "showing active interest by at least one chambers"; the docket shows the response was due August 13 and was extended twice by the Clerk, with no waiver and no request. Those two invented signals are presented as the main reasons to move above the anchor and also feed the relist figure. The headline number survives because the downward factors were real and were weighted heavily, but a rationale whose stated evidence is partly fabricated cannot be graded as sound, however good the surrounding doctrine. I could not check the candidate's own 2026-11-02 snapshot, which is not staged; the 2026-11-16 docket I hold contains every earlier entry and shows neither event.

## Predicted reasoning — 0.65
Central claims: denial at or shortly after the 11/13 conference without a relist; no CVSG; no separate writing. All three are borne out. The document also states as "current docket state" the waiver, the call for a response and the eleven amicus briefs, which the docket contradicts; that is a failed secondary claim about the record and not about what the Court would do, so it costs some of the grade without overturning it. The conditional merits forecast (affirmance on § 342 and *Farmers & Merchants*) and the GVR route never came into play.

## Leakage
Forward, `not_applicable`. The prediction predates the disposition by two weeks. The log captured call outcomes but not results, so I graded the queries: none reaches for this case's disposition, and there were no web or CourtListener calls.

## Big case — 0.50
Sector-important statutory question about master-account access, with no split and a quiet denial. My read rests on the three amicus briefs the docket shows, not on eleven.
