# Evaluation: gemini-baseline

**Cell.** Cert stage (`stage: cert`), forward distribution moment. The paid petition in *Dodson v. The Lutheran Village at Millers Grant* (No. 26-115) was distributed once, for the November 6, 2026 conference, and was **denied** on 2026-11-09. There was no relist, no CVSG, and no noted dissent. The baseline anchor and skill score are the harness's: the stamped segment base rate (frozen band `baseline`) is the reference, and I quote no rate of my own.

**Score.** The candidate predicted `denied` at P(grant) = 0.005. That is correct (1), with Brier = 0.000025.

**Reasoning quality: 0.6.** The rationale is sound in direction. It cites the baseline reached anchor, the fact-bound Title VII and Rule 56(d) posture, the absence of an alleged split, and the waiver, which it correctly reads as making a grant at the first conference "virtually impossible." But it is brief and thin. It does not engage with the Fourth Circuit's unpublished disposition or with the Groff question on its own terms. Its line about the respondent's view of the merits is speculation that the record does not show. The large adjustment from 5% down to 0.5% is asserted rather than worked through.

**Leakage.** Forward mode, predicted 2026-10-18. No calls were captured. By their queries, the logged calls were reads of the provisioned record, greps of the statpack, and generic `fedcourts query` lookups (topic searches and an unfiltered scotus 2020s listing). None targets this docket's disposition, and the reasoning shows no knowledge of the outcome. Grade: `not_applicable`.

## Predicted reasoning

**Grade: 0.5.** The document's resolved claims (outright denial, no further relists, no CVSG, no separate writing) all held. It is generic, though: it commits to nothing beyond the modal path for a waived, fact-bound paid petition. It offers no timing and no probabilities, and its only specific content is conditional on a grant that did not happen.
