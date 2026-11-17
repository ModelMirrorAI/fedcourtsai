# Evaluation: codex-baseline

**Outcome:** petition denied on 2026-11-16, with a statement of Justice Thomas respecting the denial. Cert-stage cell (relist moment). The segment base rate and skill are the harness's to stamp.

**Scores:** predicted `denied` at P(grant) = 0.44. `correct` = 1; Brier = (0.44 - 0)^2 = 0.1936. The label was right but the probability was the highest of the three candidates and sat above the frozen anchor.

## Reasoning (`reasoning_quality` 0.55)

The rationale is careful about method. It reproduced the frozen anchor from the statpack, treated the relist, CVSG and amicus cuts as cross-checks rather than multipliers, read the five distributions correctly as three reschedules plus one real relist, and was explicit about what it had and had not verified.

Its weakness is the direction of the adjustment. It moved up from the anchor to 0.44 on a final judgment, location-specific disagreements, Wolford as intervening precedent, and conference interest. Against that:

- Its own "against review" section conceded that the claimed conflicts involve different laws and postures, that the question presented is a broad facial package, and that Wolford decided a different issue. Those concessions point down, not up.
- It did not weigh the Court's recent pattern in Second Amendment cases of relisting to prepare a writing on denial, nor the fact that the Court had passed over the sensitive-places questions when it granted Wolford.
- It gave 0.38 of the grant branch to a GVR in light of Wolford while describing Wolford as narrow and already briefed by both sides.
- It treated a silent denial as the modal denial branch (0.32 for any writing), which the relist history made the less likely reading. A writing issued.

The 0.60 on a further distribution also missed.

## Predicted reasoning (`predicted_reasoning_quality` 0.42)

Central claims: denial (held, though at near coin-flip confidence), at least one further distribution with a late November to December disposition (failed: denied at the first relist conference), a silent denial as the most likely form (failed: Thomas wrote), and no CVSG (held, low risk). The document did name Thomas as the leading candidate should anyone write, which held as a secondary point. The grant-side content was conditional and is not graded. The disposition is right but two of the specific claims a reader could check failed, which places the document between the 0.25 and 0.5 anchors.

## Leakage

Forward cell, predicted a week before resolution. The log is 95% captured. The two unobserved web-search rows were graded on their queries, which target Wolford's docket, not this petition. No retrieved date reaches the resolution. The candidate states it sought no disposition of this petition. `not_applicable`.

## Note on the writing

The docket styles the writing a "statement respecting the denial"; `outcome.json` records `noted_dissent_from_denial: true`. I graded the forecast documents against the docket text and left the claim scoring to the harness.
