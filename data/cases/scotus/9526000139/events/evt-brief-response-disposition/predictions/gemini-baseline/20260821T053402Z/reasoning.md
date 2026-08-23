This is a forward prediction for a stay application (26A139) from Alabama et al. against California et al. in the First Circuit.
The application was docketed on July 29, 2026, and Justice Jackson requested a response by August 3, 2026. The response and several amicus briefs were filed on August 3.

The strictly-prior Terms for an OT2026 application are OT2025 and OT2024. As noted in `metrics/statpack.md`, the pooled substantive resolved applications over these two terms yield 225 applications and 30 grants, satisfying the 50-application floor. This gives an unconditioned baseline grant rate of 13.33%.

However, this application sits high on the escalation ladder: a response was requested by the Circuit Justice, and multiple amicus briefs (at least 5 recorded in the docket, 2 frozen in context) were filed immediately. Given the involvement of multiple states and high-profile amici (Former Judges, Governors, National Security Leaders), it is a highly salient application. While the baseline grant rate is 13%, the escalation signals suggest a higher probability. Still, granting a stay is an extraordinary remedy, so I adjust the probability up to 0.22.

The `response-requested-increment` is effectively vacuous since a response was already requested. The `amicus-increment` is priced near certainty, as the snapshot already shows more amicus briefs filed on August 3 than the 2 frozen in the context. The `referral-increment` is priced at 0.65, as contentious multi-state applications are frequently referred to the full Court.

No tool calls beyond checking the docket snapshot and the statpack were successful, as the CourtListener API returned a 429 rate limit error when attempting to fetch the case details.
