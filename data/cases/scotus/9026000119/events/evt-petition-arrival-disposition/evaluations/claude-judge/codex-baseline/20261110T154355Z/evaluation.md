# Evaluation — codex-baseline

Cell: scotus/9026000119 (Guam v. Ybanez, No. 26-119), `evt-petition-arrival-disposition`. This is a cert-stage arrival cell, and the prediction ran forward on 2026-08-16. Outcome: **denied** on 2026-11-09 (`actual_granted` 0). The petition was distributed once (the conference of 11/6/2026), with no relist, no CVSG and no noted dissent; one respondent waived a response on 2026-08-26. The harness stamps the segment base rate, the skill and the basis, so this note quotes no rate of its own.

**Score.** The prediction was P(grant) = 0.025 with a predicted disposition of `denied`, so it is correct (1) with a Brier score of 0.000625.

**Reasoning quality: 0.85.** This is the strongest rationale of the three. It anchors on the arrival-moment whole-segment rate and explains why it chose that over the `state` risk-set rate and the terminal relist-zero cut. Its legal analysis then picks out the features that actually make this a poor vehicle:
- no split among courts of last resort, and the petition asks the Court to extend lower-federal-court authority;
- the trial court found a concrete same-matter conflict;
- the Guam Supreme Court did not reach the merits of disqualification and instead dismissed after the petitioner failed to obtain substitute counsel. That raises passed-upon, independent-ground and redressability problems.

It also notes how weak the theory is that a government holds Fourteenth Amendment rights. It names the counterweights (a government petitioner, institutional stakes, recurrence) and does not overweight them. It discloses that its CourtListener searches hit a rate limit. The one thing holding the grade back is that the doctrinal points are asserted rather than tied to cited authority.

**Leakage.** Forward, `not_applicable`. The captured log shows only reads of the provisioned record and the statpack. One "other" row carries a harness credential redaction, which is removed text and not evidence. Nothing in the log or the reasoning postdates the resolution.

## Predicted reasoning

**Grade: 0.75.** I treated four claims as central: denial; exactly one ordinary distribution with no relist; no CVSG; and no dissent or statement on denial. All four held against the docket and the outcome. The document is specific on each point and gives a reason for its CVSG call (Organic Act interest, outweighed by the local, record-bound controversy). Still, every call is the modal path for a paid territorial petition with no split, so it called little that a competent reader would plausibly have called otherwise. That keeps it below 1.0. The content conditional on a grant (a narrowed question, plenary review over summary disposition) never came into play and earns neither credit nor penalty.

**Big case.** 0.15 (my own read): a local disqualification dispute, denied quietly.
