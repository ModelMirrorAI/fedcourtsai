# gemini-baseline — Mullin v. National TPS Alliance, No. 26A714

The government withdrew its stay application on November 19, one day after filing. On this interim event, `outcome.json` records `withdrawn` and `interim_granted = 0`. The grant call was incorrect. The Brier score is (0.57 − 0)² = **0.3249**. The harness computes the interim baseline and skill from the prior application Terms.

## Reasoning quality

**0.88.** The rationale identifies the development that changed the immediate need for a Supreme Court stay. The government had asked the Ninth Circuit for protection until seven days after judgment (application, p. 14). The candidate's forward retrieval identifies the November 18 order granting that request. It explains why the earlier Supreme Court stays and *Mullin v. Doe* still favored relief if reached, and why those authorities had less bearing on whether the government would keep pressing the application.

The candidate correctly uses the federal-applicant comparison as context and counts voluntary withdrawal as an ungranted outcome. It assigns 20% to prompt withdrawal, another 10% to later withdrawal and 13% to denial without prejudice. Its largest individual scenario, a Supreme Court grant before the Ninth Circuit issued judgment (32%), rests on the government's desire to avoid another emergency filing. The rationale gives little evidence that this concern would lead the government to press for immediate intervention after securing the precise extension it sought. The scenario weights explain the 57% forecast, but their precision exceeds the evidence.

## Predicted reasoning

**0.32.** The forecast favored a supplemental letter maintaining the request, followed by consideration of a stay. The docket shows a letter withdrawing it. Its specific alternative of withdrawal within 24–48 hours before referral or amicus filings fits the sequence exactly. That alternative earns partial credit. The entry confirms the timing and action but leaves the applicant's reason unstated. The proposed briefing schedule, merits ground and lineup all depended on the application surviving, so the withdrawal leaves those details untested.

## Leakage

Forward run. The log records a live 26A714 docket fetch at 14:40 UTC on November 19 and a read of Ninth Circuit document 109. The calls are outcome_only, so their returned text is unavailable. The candidate reports a pending Supreme Court application and quotes the lower court's November 18 extension. That pre-resolution order was available for forward retrieval. Neither the queries nor the reasoning show that the November 19 withdrawal was known.
