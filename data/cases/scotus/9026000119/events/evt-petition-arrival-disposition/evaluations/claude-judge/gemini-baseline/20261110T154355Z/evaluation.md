# Evaluation — gemini-baseline

Cell: scotus/9026000119 (Guam v. Ybanez, No. 26-119), `evt-petition-arrival-disposition`. This is a cert-stage arrival cell, and the prediction ran forward on 2026-08-16. Outcome: **denied** on 2026-11-09 (`actual_granted` 0). The petition was distributed once (the conference of 11/6/2026), with no relist, no CVSG and no noted dissent; one respondent waived a response on 2026-08-26. The harness stamps the segment base rate, the skill and the basis, so this note quotes no rate of its own.

**Score.** The prediction was P(grant) = 0.03 with a predicted disposition of `denied`, so it is correct (1) with a Brier score of 0.0009.

**Reasoning quality: 0.55.** The direction and the anchor choice are sound: the weakest band's bracketed reached rate at the arrival moment, cited at about 5.4% for OT2025 and 6–7% over recent Terms. I did not rebuild the candidate's statpack build because the figure plays only an anchoring role and is plausible on its face. The downward adjustment rests on general points: the case is likely governed by local professional-conduct rules, it asks to extend federal doctrine, and there is "no clear indication" of a split. Those points are right, but the rationale never engages the record. It does not mention the substitute-counsel dismissal below, the trial court's conflict findings, or the problem of a government claiming due-process rights. A competent reader could have written it from the caption and the question presented. It honestly discloses that CourtListener was rate-limited.

**Leakage.** Forward, `not_applicable`. The log is entirely uncaptured (coverage 0.0, which is this engine's standing shape), so I graded on the queries. They are provisioned-record reads, a statpack grep, two CourtListener searches for the Guam lower-court opinion, and a corpus query. None targets this petition's outcome, and the reasoning presupposes nothing past the cutoff.

## Predicted reasoning

**Grade: 0.6.** I treated three claims as central: no relist beyond the initial conference; no CVSG; and no dissent or separate writing. All three were borne out. The document is brief and its claims are the default path, with reasons that stay generic ("does not implicate typical ideological divides"). Its content conditional on a grant (a due-process or separation-of-powers focus, no summary disposition) did not come into play. It is right but commits to little beyond the outcome, so it sits just above the 0.5 anchor.

**Big case.** 0.15 (my own read).
