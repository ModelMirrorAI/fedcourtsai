# Evaluation: codex-baseline

**Cell.** Cert stage (`stage: cert`), forward distribution moment. The paid petition in *Dodson v. The Lutheran Village at Millers Grant* (No. 26-115) was distributed once, for the November 6, 2026 conference, and was **denied** on 2026-11-09. There was no relist, no CVSG, and no noted dissent. The baseline anchor and skill score are the harness's: the stamped segment base rate (frozen band `baseline`) is the reference, and I quote no rate of my own.

**Score.** The candidate predicted `denied` at P(grant) = 0.025. That is correct (1), with Brier = 0.000625.

**Reasoning quality: 0.85.** This is a careful and well-sourced rationale. It anchors on the sal-v4 baseline reached rate over strictly-prior Terms and explains why it moves below that rate. It points to vehicle problems that the outcome bears out: an unpublished, short Fourth Circuit affirmance; questions framed as error correction; no developed circuit split; and the district court's explicit application of Groff. It also flags the Rule 56(d) expert-disclosure friction and treats the response waiver as weak negative evidence. It keeps the petitioner's assertions separate from findings. One weakness keeps it off the top: it does not give the response waiver its full mechanical weight. The Court essentially never grants a waived paid petition without first calling for a response, and nothing in this docket suggested a call. Because of that, 2.5% is roughly five to six times higher than the other two candidates, so the Brier is the weakest of the three, though still small.

**Leakage.** Forward mode. The prediction was made on 2026-10-18, before the 2026-11-09 resolution. The web lookups covered general Groff and Rules material, not this docket, and their results were unobserved. No outcome material was found. Grade: `not_applicable`.

## Predicted reasoning

**Grade: 0.65.** The document's central calls all held: denial on the order list after the November 6 conference, no further distribution, no CVSG, and no separate writing. Its conditional content (a narrowed QP 1 on Groff health-and-safety undue hardship, with plenary review favored over a summary route) was never triggered and earns neither credit nor penalty. The resolved claims are the standard path for a waived, unpublished, fact-bound paid petition, so they discriminate only modestly. It sits above the generic midpoint because the document commits to the timing, the relist probability and the CVSG call explicitly.
