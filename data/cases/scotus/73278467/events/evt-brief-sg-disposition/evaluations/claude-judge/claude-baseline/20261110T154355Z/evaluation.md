# Evaluation — claude-baseline

## Cell

Cert stage, `moment: sg-brief`, forward mode. The outcome is **GVR** (`actual_disposition: gvr`, `actual_granted: 1`). On Nov 9 2026 the Court granted the petition, vacated the judgment and remanded for further consideration in light of *West Virginia v. B.P.J.* and *United States v. Skrmetti*. That followed one more distribution (Oct 14 2026, for the 11/6/2026 conference). All three candidates predicted `gvr`, so `correct` = 1 for each. The segment base rate, `base_rate_basis` and skill are the harness's to stamp. The candidates froze band `high` (sal-v4), so the anchor is the risk-set rate, and I quote no figure of my own. Cert votes are not scored, so I wrote no `vote_accuracy`. A cert cell declares no semantic set, so I wrote no `semantic_grades`.

## Big case

0.55. The questions matter nationally to correctional administration: Turner deference vs. VMI scrutiny for sex-based jail policies applied to a transgender detainee, and cross-sex strip searches. They drew a 23-State amicus brief and a CVSG. But the Court resolved nothing and remanded by routine GVR after *B.P.J.* had already narrowed the questions.

## Scores

- `correct`: 1. `brier_score`: (0.82 − 1)² = 0.0324.
- `reasoning_quality`: 0.72.

## Reasoning

The rationale is concise and gets the core right: the SG recommended a GVR, and the Tenth Circuit's heightened-scrutiny holding rested on the since-GVR'd *Fowler*. It has one genuinely good discount: the Court chose to CVSG rather than GVR on its own after *B.P.J.*, which suggests some doubt. The weaknesses:

- It read the petition, BIO and reply only through the SG's account of them.
- It described the high band as "about 31–42% per Term, roughly 37% pooled". In the build it ran against (eb6830084a18, rebuilt with `statpack-at`), the per-Term range is 25.5–41.7% and the pooled rate is ≈35%. The error is minor and did not drive the forecast.
- It asserted that "Respondent will file a supplemental brief opposing a GVR". No such filing appears on the docket.

## Predicted reasoning

Grade **0.80**. The central claims are all specific and borne out:

- a GVR in light of *B.P.J.*/*Skrmetti* at the next conference that takes up the case (the Nov 6 conference, order Nov 9)
- a further distribution for a late-Oct/Nov conference
- the whole judgment remanded with neither QP taken as written

One secondary forecast failed: a "plausible" statement or dissent from the GVR by Justice Sotomayor and/or Justice Jackson. The docket's order text notes none. It was hedged, so it costs little.

## Leakage

Forward. The run came before the resolution. Its 9 captured calls are all local reads of the provisioned record and statpack. There was no external retrieval and no data/qp-topics read. Graded `not_applicable`, `leakage_suspected` false.
