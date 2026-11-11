# Evaluation: claude-baseline

**Cell.** Cert stage (`stage: cert`), forward distribution moment. The paid petition in *Dodson v. The Lutheran Village at Millers Grant* (No. 26-115) was distributed once, for the November 6, 2026 conference, and was **denied** on 2026-11-09. There was no relist, no CVSG, and no noted dissent. The baseline anchor and skill score are the harness's: the stamped segment base rate (frozen band `baseline`) is the reference, and I quote no rate of my own.

**Score.** The candidate predicted `denied` at P(grant) = 0.004. That is correct (1), with Brier = 0.000016.

**Reasoning quality: 0.85.** This is a tight and well-targeted rationale. It anchors on the sal-v4 baseline reached rate and then explains a large downward move with the features that actually decided the petition: response waived and none called for, an unpublished per curiam affirmance, error-correction framing with no split alleged, and QPs that duplicate one another. Its central mechanical point is right: the Court almost never grants without first calling for a response, so the realistic path to a grant runs through a response request, and none came. It ties its relist probability directly to that path, which is coherent. Minor deductions: it leans on "my experience of the cert docket" and the counsel profile without sourcing either, and it is short on engagement with the post-Groff legal question itself.

**Leakage.** Forward mode, predicted 2026-10-18. All five calls were captured shell reads of the provisioned record and the statpack. There was no external retrieval. Grade: `not_applicable`.

## Predicted reasoning

**Grade: 0.65.** The central calls all held: denial after the November 6 conference, no further distribution (with the call-for-response path named as the only route to one), no CVSG, and no separate writing. The conditional analysis of the QPs and the summary route was not triggered. The document is specific and correct, but its central calls are the modal path for this posture, so it cannot reach the top anchor.
