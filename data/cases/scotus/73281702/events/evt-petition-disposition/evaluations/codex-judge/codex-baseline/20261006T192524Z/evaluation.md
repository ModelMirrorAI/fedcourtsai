# Evaluation: codex-baseline

## Outcome and quantitative scores

This cert-stage event resolved as `denied` on October 5, 2026, with
`actual_granted = 0`. codex-baseline's September 17 prediction names that label
and assigns grant probability 0.12. Thus **correct = 1** and
**Brier = 0.0144**. Denial does not resolve the constitutional merits.

The frozen prediction context fixes Term 2025, `elevated`, and `sal-v4`.
The statpack heading matches that version, so the basis is `risk_set`.
I pool the Markdown table's bracketed reached rates over every displayed
Term strictly before 2025: 2024 17.9% (n=336), 2023 17.5% (354),
2022 19.0% (300), 2021 20.5% (342), 2020 16.1% (397), 2019 13.8% (334),
2018 15.9% (347), and 2017 17.5% (400). The weighted total from these
rounded rates is 484.386 over 2,810, yielding
**segment_base_rate = 0.172379359430605** and
**Brier skill = 0.5153904514440745** via `1 - 0.0144 / rate^2`.

The caption reports 10 of 10 Terms rendered, so there is no window mismatch;
2025 and 2026 are excluded rather than used as additional prior data. The
candidate's 484/2,810 figure is described as coming from unrounded JSON;
the tiny difference here is the displayed-rate rounding convention, not an
analysis error. These committed figures are denial-reweighted historical/live
estimates. I did not inspect a live corpus blob or assert its freshness.

## Reasoning quality: 0.90

The rationale carefully separates attention from grant-worthy conflict and
response-driven redistribution from a demonstrated substantive relist. Its
treatment of Richardson is balanced: the petition's incorporation argument
matters, but the earlier discussion is neither a holding invalidating this
statute nor an unconditional endorsement of all such statutes. The account
of the competing arguments is consistent with the provisioned petition and
opposition. The facial-challenge observation is specifically supported by
the lower opinion's appendix 22a–23a and footnote 6, and the candidate does
not invent a forfeiture from that posture.

The candidate also identifies the limits of the absence-of-conflict claim,
avoids treating the concurrent convictions as eliminating the challenged
sentence's stakes, and distinguishes terminal descriptive rates from forward
transition probabilities. The principal remaining limitation is calibration:
12% is a reasoned but unfitted adjustment, with no demonstrated numerical
effect for the cited vehicle and conflict features. The analysis acknowledges
that limitation. Its quality score reflects evidential discipline and
balanced reasoning, not the mere fact that the denial call was right.

The forecast prose is unscored. Mechanical claims are left for the harness;
this cert cell receives neither semantic grades nor vote accuracy.

## Leakage

The log identifies a forward prediction, with 33 of 35 results captured.
The two unobserved web calls seek Richardson, a historical precedent. I do
not adopt the candidate's claim that those calls returned nothing as an
independently captured fact; their queries, not absent digests or dates,
support the assessment. The other substantive retrieval concerns that
precedent and the already-filed September 15 reply. The prediction predates
the October 5 denial, and the prose treats the September 28 conference as
future. No target-case outcome material or mis-provisioned decided posture
is shown: influence is `not_applicable`, and leakage is not suspected.
