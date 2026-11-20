# gemini-baseline on Overton’s application for a stay

The Court denied the stay on November 19, 2026. gemini-baseline predicted denial and assigned 0.800% to relief. With `interim_granted` equal to 0, the disposition is correct (1) and the Brier score is 0.000064. The harness computes the interim baseline and Brier skill score from prior application Terms.

## Reasoning quality

**0.94.** The rationale explains why the Governor’s reported refusal to commute murder sentences and the request for clemency records posed distinct obstacles to a stay. It connects the narrow federal protections under *Woodard* with the state-law limits on post-warrant records requests, identifies the similar *Guardado* proceeding and checks the recent experience of private capital applicants. Those comparisons support a substantial downward adjustment. The 0.8% figure is more precise than the evidence can establish. Two recent Terms with no grants leave uncertainty about the next application, and examples selected from denials cannot independently establish the frequency of grants. Calling the federal merits “foreclosed” also understates the applicant’s argument that categorical precommitment made access to clemency illusory.

## Predicted reasoning

**1.00.** The forecast specified the sequence that distinguished this case from other possible denials. Florida filed voluntarily on November 17, Overton replied the same day, and Justice Thomas referred the application to the full Court. The November 19 entry used the predicted referral language and denied certiorari in the next sentence. The record shows zero amici and no separate writing. These specific calls support full credit on the central claims. The docket confirms the date only. The precise hour and the conditional merits analysis add no credit.

## Leakage

Forward forecast made November 15. The log shows requests for both live dockets, the November 14 petition and appendix, and earlier Florida cases. All 61 calls have outcome_only capture, so the log preserves queries and call status without returned text. The candidate reports both dockets pending. The staged docket independently dates Florida’s response and Overton’s reply to November 17 and the referral and denial to November 19. Nothing in the reasoning reports those later events as known.
