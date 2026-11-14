# Evaluation: claude-baseline

**Outcome.** On 2026-11-13 the Court granted the petition, limited to the first question in the Solicitor General's reformulated wording (`actual_disposition: granted`, route plenary). This is a cert-stage cell; the segment base rate and skill are the harness's to stamp.

**Scores.** Predicted `granted-in-part` at 0.84. Brier = 0.0256, the best of the three. `correct` = 0 under the exact-label rule, because the outcome label is `granted` and the prediction's is `granted-in-part`. That zero is a label mismatch and not a substantive miss: the order reads "Petition GRANTED limited to the following question," which is what the candidate forecast. I have flagged the vocabulary question in `flags.json`.

**Reasoning quality: 0.62.** The analysis is short and gets the decisive points right. It identifies the SG's grant recommendation on Question 1 with a reformulated question as the dominant signal, notes that the committed CVSG cut pools grant and deny recommendations and so understates this posture, correctly reads the three distributions as only one true relist, and lists the right downside risks (interlocutory posture, the surviving Item 303 claim, a relist for a writing). The resulting number was well placed.

What holds it down is depth and sourcing. The candidate says it did not read the brief in opposition or the decision below closely, only skimmed the respondents' supplemental brief, and "did not weigh the BIO in detail." The vehicle objections were the only real route to a denial, so the forecast was confident without having examined the main counter-case. The key quantitative step (roughly three-quarters or more of SG-supported CVSG petitions are granted) is stated from general knowledge without support in the provisioned tables. The candour about both limits is to its credit, and the judgment was sound, but the legal analysis itself is thin.

## Predicted reasoning

Grade 0.9. Central claims: a grant limited to Question 1, most likely in the SG's reformulated wording, which the document quotes (borne out; the granted question is that wording verbatim); grant from the Nov. 13 conference with no further distribution (borne out); no summary disposition (borne out). The conditional merits holding is unresolved. The disposition and its scope were specific and correct on points a competent reader could have called otherwise: petitioners asked for both questions, and the Court could have kept the original wording. Slightly short of 1.0 because the document is brief and its remaining content is conditional.

## Leakage

Forward cell, written four days before resolution. Fully captured log shows only provisioned reads, the statpack, and generic corpus queries. `not_applicable`.
