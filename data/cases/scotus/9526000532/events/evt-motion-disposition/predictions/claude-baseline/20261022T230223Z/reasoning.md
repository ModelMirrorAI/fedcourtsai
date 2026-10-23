# Rationale — P(grant) 0.015

**Anchor.** The statpack section "The interim docket (applications)" gives per-Term substantive counts. Pooling application-Terms strictly before OT2026 within the ten-Term window (2016–2025) gives 2025: 17/226, 2024: 16/194, 2023: 18/127. Earlier Terms are fully unparsed (0 resolved). The pool is 51 granted out of 547 resolved, or **9.3%**. That clears the floor of 50, so it is the scored baseline. The pack captions this as a scored base rate, not as descriptive only.

**Adjusting down, sharply.** That pooled cohort mixes in government applicants, emergency applications in high-profile litigation, and represented parties. This application differs on every axis that predicts relief:
- The applicant is **pro se**. Counsel of record is the applicant himself.
- The respondent is **the United States**. CourtListener shows the case below as *United States v. Frank Monte, III*, CA3 No. 26-2501, a federal criminal appeal. A stay sought by a criminal defendant against the government is among the least-granted application types.
- The application is at the arrival rung. There is no response request, no referral, and no amicus. Because selection runs in ladder order, predicted cells usually sit higher than this one. This cell sits at the bottom.
- I could not read the application itself. `documents.json` marks `application.txt` with `empty_text: true` (16 pages, no text layer). I don't know exactly what is being stayed (a mandate, a judgment, surrender to custody, or a district court proceeding). My read comes from the caption, the posture, and the CA3 docket title, not from the filing.

I set 1.5% rather than lower because I can't see the content, and a narrow, unopposed stay (for example, of the mandate pending a cert petition) is occasionally granted.

**Increments.** Response requested ≈5%. Circuit Justices rarely call for a response on pro se criminal stay applications. Referral ≈20%, which comes mostly from the renew-to-another-Justice route. That route is common among pro se applicants and almost always ends in a referral and a denial by the Court. Amicus ≈2%.

**Where to discount me.** I had no application text. I made only one docket lookup in the lower court and did not read any filings there. The nature of the stay sought is unknown, so the referral figure is the softest number here.
