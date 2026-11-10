# Evaluation — codex-baseline

## Cell

Cert stage, `moment: sg-brief`, forward mode. The outcome is **GVR** (`actual_disposition: gvr`, `actual_granted: 1`). On Nov 9 2026 the Court granted the petition, vacated the judgment and remanded for further consideration in light of *West Virginia v. B.P.J.* and *United States v. Skrmetti*. That followed one more distribution (Oct 14 2026, for the 11/6/2026 conference). All three candidates predicted `gvr`, so `correct` = 1 for each. The segment base rate, `base_rate_basis` and skill are the harness's to stamp. The candidates froze band `high` (sal-v4), so the anchor is the risk-set rate, and I quote no figure of my own. Cert votes are not scored, so I wrote no `vote_accuracy`. A cert cell declares no semantic set, so I wrote no `semantic_grades`.

## Big case

0.55. The questions matter nationally to correctional administration: Turner deference vs. VMI scrutiny for sex-based jail policies applied to a transgender detainee, and cross-sex strip searches. They drew a 23-State amicus brief and a CVSG. But the Court resolved nothing and remanded by routine GVR after *B.P.J.* had already narrowed the questions.

## Scores

- `correct`: 1. `brier_score`: (0.88 − 1)² = 0.0144.
- `reasoning_quality`: 0.85.

## Reasoning

This is the best-calibrated and most self-aware rationale. It anchors on the CVSG cut (34.8%) and the high band (≈34.95% over OT2017–24, matching the statpack). It says explicitly that the jump to 0.88 is a judgment about this specific SG GVR recommendation, not a measured SG-follow rate, and gives the concrete reasons: the panel relied on *Fowler*/*Hecox*, the SG offered a limited exit without deciding *Turner*, and petitioners asked for a GVR in the alternative. It lists the BIO's substantive objections to justify the 12% residual. It is also careful about what the distribution claim measures. It has no material analytic error. It is slightly less detailed on the doctrine than gemini-baseline.

## Predicted reasoning

Grade **0.90**. It commits to a short GVR in light of *B.P.J.*/*Skrmetti*, not a plenary grant or summary reversal. It commits to exactly one more distribution to consider the brief, then a prompt fall-2026 disposition rather than a hold, with no question taken for plenary resolution. Every central claim is specific and borne out: the Oct 14 distribution for the Nov 6 conference, then the Nov 9 GVR. Only the predictability of a GVR after the SG's recommendation keeps it short of 1.0.

## Leakage

Forward. The run came before the resolution. The web searches and URL fetch concerned *Lawrence v. Chater* (1996) and were uncaptured, so I graded them on their queries. None touched this docket, and the candidate disclosed them. Graded `not_applicable`, `leakage_suspected` false.
