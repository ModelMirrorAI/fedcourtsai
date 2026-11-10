# Evaluation — codex-baseline

**Cell.** Cert stage, `moment: distribution`, forward mode. Guam v. Ybanez, No. 26-119. Outcome: petition **denied** Nov 9, 2026. That was a clean first-conference denial after the single distribution for the 11/6/2026 conference: no response request, no CVSG, no relist and no noted dissent. `actual_granted` = 0. The segment base rate and skill score are harness-stamped. I have not pooled or quoted a rate of my own; any comparison should use the stamped segment base rate. Votes are not scored on a cert cell. No semantic set is declared, so this cell carries no `semantic_grades`.

**Scores.** Predicted `denied` at P(grant) = 0.08, so `correct` = 1 and Brier = 0.0064.

**Reasoning quality: 0.85.** This is the most thorough rationale of the three. It read the lower-court appendices and used them well. The trial court held evidentiary hearings and made organizational-client and ineffective-screening findings (App. D). The separation-of-powers argument was raised late and declined below (App. D). The Supreme Court of Guam set an express deadline for substitute counsel and warned the petitioner before the dismissal (App. C, App. A), which undercuts the petition's no-notice framing. It checked the petition's main analogy, *United States v. Bolden*, against the opinion itself and correctly found an extension rather than a split. It also weighed real counterweights: the Organic Act hook, public-corruption enforcement and alleged recurrence. Those support a forecast above the floor for a weak petition, and the case is clearly argued. The 0.08 is somewhat generous given the vehicle problems the candidate itself identified. Every reason it gave pointed toward a clean denial, which is what happened. I take off a little for that calibration, not for the analysis.

## Predicted reasoning

**Grade: 0.55.** Central claims: (1) denial after the 11/6 conference, in November, with no further distribution and no separate writing, (2) no relist as the modal path and (3) no CVSG. All were borne out. Its conditional content (80/20 plenary over summary, and a narrowed QP on substitute counsel under the Organic Act) is unresolved because no grant occurred. The timing commitment, denial in November 2026, is slightly more specific than the bare disposition and held. Overall it is still the modal path for an unopposed weak petition, so the grade sits a little above the generic anchor.

## Leakage

Forward log with capture coverage 1.0 and 7 captured calls, all shell reads of instructions and the statpack. Its retrieval.md also discloses a web search for Rule 10 (no usable content) and CourtListener lookups of *Bolden* (10th Cir. 2003) that are not in the captured log. I recorded that as an info-level capture-gap flag. None of it concerns this petition's disposition. Its explicit statement that it neither sought nor encountered the disposition counts in its favor. `not_applicable`; not suspected.
