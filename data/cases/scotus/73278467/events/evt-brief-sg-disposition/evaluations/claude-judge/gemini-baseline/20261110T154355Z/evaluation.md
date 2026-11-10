# Evaluation — gemini-baseline

## Cell

Cert stage, `moment: sg-brief`, forward mode. The outcome is **GVR** (`actual_disposition: gvr`, `actual_granted: 1`). On Nov 9 2026 the Court granted the petition, vacated the judgment and remanded for further consideration in light of *West Virginia v. B.P.J.* and *United States v. Skrmetti*. That followed one more distribution (Oct 14 2026, for the 11/6/2026 conference). All three candidates predicted `gvr`, so `correct` = 1 for each. The segment base rate, `base_rate_basis` and skill are the harness's to stamp. The candidates froze band `high` (sal-v4), so the anchor is the risk-set rate, and I quote no figure of my own. Cert votes are not scored, so I wrote no `vote_accuracy`. A cert cell declares no semantic set, so I wrote no `semantic_grades`.

## Big case

0.55. The questions matter nationally to correctional administration: Turner deference vs. VMI scrutiny for sex-based jail policies applied to a transgender detainee, and cross-sex strip searches. They drew a 23-State amicus brief and a CVSG. But the Court resolved nothing and remanded by routine GVR after *B.P.J.* had already narrowed the questions.

## Scores

- `correct`: 1 (gvr = gvr). `brier_score`: (0.78 − 1)² = 0.0484.
- `reasoning_quality`: 0.80.

## Reasoning

The analysis is sound and closely sourced. It identifies the decisive facts: the SG's explicit GVR recommendation, and the panel's reliance on *Fowler* (later GVR'd after *Skrmetti*) and *Hecox* (reversed in *B.P.J.*). It also notes the hold-then-CVSG docket pattern and that petitioners asked for a GVR in the alternative. It takes the BIO's counterarguments seriously: the interlocutory 12(b)(6) posture and the unchallenged individual-capacity Fourth Amendment claim. It answers them through the reply's binding-precedent point. The probability decomposes coherently (0.69 GVR + 0.09 plenary vs. 0.22 deny). Its base-rate figures (high band pooled 35.0% over OT2017–24; CVSG cut 34.8%) match the statpack it ran against (eb6830084a18). Weaknesses: the "historically ~75–85%" SG-follow rate is asserted without a source, and the 22% denial mass is somewhat generous given how strongly the reasoning itself points to GVR. That is defensible, but it was the least confident of the three.

## Predicted reasoning

Grade **0.85**. The central claims are the GVR in light of *B.P.J.*/*Skrmetti*, summary GVR rather than plenary review, 1–2 more distributions toward a late-Oct/Nov conference, and no second CVSG. All are specific and all were borne out: one distribution for the Nov 6 conference, then the Nov 9 GVR. Once the SG recommended a GVR, that route was the natural call, which keeps this below 1.0. The conditional plenary-QP and dissent-from-denial content did not arise.

## Leakage

Forward. The run (2026-10-23) came before the 2026-11-09 resolution. Retrieval was one CourtListener search for the 10th Cir. *Fowler v. Stitt* opinion and one corpus query of GVR dispositions. Neither targets this docket, and the reasoning does not assume the result. Result capture was 0.0, so this rests on the queries. Graded `not_applicable`, `leakage_suspected` false.
