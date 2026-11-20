# Reasoning for my numbers

**P(grant) = 0.004.**

## What I read
- Snapshot `2026-11-20.json`: paid petition, docketed October 27, 2026; respondent (Commissioner, through the Solicitor General) waived a response on November 13; distributed November 17 for the December 4 conference. No amicus briefs, no call for a response, no CVSG.
- `petition.txt` and `questions-presented.txt`: a self-represented petitioner (a CPA) seeks a tax whistleblower award under 26 U.S.C. § 7623, arguing the courts ignored § 7623(c) and over-deferred to the IRS.
- `appendix.txt`: the D.C. Circuit's one-paragraph unpublished per curiam judgment (Katsas, Walker, Childs) affirming the Tax Court's dismissal for lack of jurisdiction because the IRS commenced no action against the identified taxpayers, citing *Kennedy v. Commissioner* (2025) and *Li v. Commissioner* (2022). Rehearing en banc was denied with no judge requesting a vote.
- No brief in opposition exists (waiver). `same-question.json` lists no similar pending petitions, so there is no hold candidate.

## Anchor and adjustments
- `context.json` gives band `baseline` with `cert_anchor.rate` 0.052 (reached rate) and the no-amicus line 0.027. Both pool petitions that later climbed out of the baseline band; the terminal baseline rate in the statpack is about 1.5% per Term.
- I go well below those figures because every case-specific feature points down:
  - Self-represented petitioner; such petitions are almost never granted.
  - Response waived and not called for by the time of distribution. The Court does not grant without a response, so a grant would need a call for response first.
  - Unpublished, summary judgment applying settled circuit precedent. All § 7623 whistleblower appeals go to the D.C. Circuit, so no circuit split can develop, and the petition claims none.
  - The questions presented do not engage the jurisdictional ground the judgment rests on, a vehicle defect.
- The D.C. Circuit's higher origin grant rate (about 6% in the statpack) reflects agency cases with counsel and is not informative here.

## Other claims
- `relist-increment` 0.02: a further distribution needs a call for response (a few percent of waived paid petitions at most, lower for this one) or an administrative reschedule.
- `cvsg-increment` 0.001: the government is a party.
- `summary-disposition-route` 0.5: conditional on a grant I have no real view; a grant here would most plausibly follow some intervening development, which favours a GVR, but none is visible.
- `dissent-from-denial` 0.003 and the per-Justice `order-writers` numbers: nothing here attracts a writing.

## Uncertainty and caveats
- The petition's stamps show it was first filed February 9, 2026 and docketed only on October 27, 2026, apparently after correction and resubmission. I treat it as timely since the Clerk docketed it; it does not affect the forecast.
- I did not look up whether a petition is pending in *Kennedy v. Commissioner*; the same-question list shows none, and I assume there is none.
- The corpus query I ran returned generic recent denials, not tailored priors; it did not move the number.
