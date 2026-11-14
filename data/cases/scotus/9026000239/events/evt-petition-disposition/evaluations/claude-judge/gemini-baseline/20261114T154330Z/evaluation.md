# Evaluation: gemini-baseline

Cert-stage cell, forward mode. Outcome: certiorari granted on 13 November 2026, limited to Questions 1 and 2, after one relist; plenary route.

## Scores

- `correct` = 1: predicted `granted`, actual `granted`.
- `brier_score` = (0.95 - 1)^2 = 0.0025, the best of the three.
- Vote accuracy is not scored on a cert cell. The base rate, the skill score and the claim scores are the harness's.

## Reasoning (`reasoning_quality` 0.5)

The conclusion was right and the main driver was correctly identified: a Solicitor General petition against a lower-court judgment blocking a major presidential immigration policy. The analysis behind it is thin.

- **The anchor is a range, not a pooled rate.** It cites federal-band grant rates of "50-89% in recent terms" and moves to 0.95 without saying how far the case-specific facts carry it or why.
- **No engagement with the opposition.** It names none of the respondents' arguments: the unappealed vacatur, the absence of a split, the narrowed merits defense. The log shows it opened only the first 150 lines of the petition and of the brief in opposition, and not the reply.
- **A loose description of the judgment below** ("upheld (or left in place) a classwide injunction") shows it had not pinned down what the D.C. Circuit held.
- **The relist reasoning is internally uneven.** It puts 0.40 on a further distribution while the forecast document expects a grant "potentially after one relist".

The high probability was rewarded here, but the rationale would not distinguish this petition from any other government petition in a high-profile case.

## Predicted reasoning (`predicted_reasoning_quality` 0.55)

Central claims: a grant, possibly after one relist; plenary route; all three questions; no CVSG.

- The grant and the plenary route were borne out.
- The relist was mentioned only as a possibility, so it earns little.
- The one specific claim beyond the outcome failed: it expected the Court to address all three questions, and the grant was limited to Questions 1 and 2.
- The conditional content on a denial earns neither credit nor penalty.

Right in direction and mostly generic, with its one discriminating secondary claim wrong: just above the 0.5 anchor.

## Leakage

Forward cell, genuinely open when predicted. Every call in the log is unobserved (capture coverage 0.0), so I graded on call targets: all are provisioned inputs, the statpack, the schema, and its own output files. No web or CourtListener call and no path under `data/qp-topics/`. Nothing in the prose presupposes the outcome. `influenced_prediction` = `not_applicable`.
