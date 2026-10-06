# Evaluation: gemini-baseline

## Outcome and quantitative score

This cert-stage event resolved October 5, 2026 with `actual_disposition = denied`
and `actual_granted = 0`. gemini-baseline's September 17 prediction named `denied`
with P(any grant) = 0.01. Its exact-label **correct = 1** and
**Brier = (0.01 - 0)^2 = 0.0001**. A small realized error on this denial does
not establish that its probability estimation method is well calibrated.

The prediction freezes `baseline`, `sal-v4`, and Term 2025. The matching
Markdown heading supports **risk_set** scoring. I pool the bracketed reached
figures across all displayed strictly prior Terms, not just OT2024 as the
candidate did. OT2024 through OT2017 contribute rate/weighted-n pairs of
5.7%/1271, 5.9%/1312, 5.8%/1192, 5.6%/1500, 4.5%/1739, 4.6%/1399,
4.6%/1524, and 4.7%/1643. The displayed pool is 592.925 / 11,580 =
**0.05120250431778929**. The table renders all ten of ten Terms; OT2025 and
OT2026 are excluded. Rates and denominators are denial-reweighted estimates at
the table's published precision, not raw counts or newly refreshed observations.
**Brier skill = 0.961856758794282**, from
1 - 0.0001 / 0.05120250431778929^2, is a single-event descriptive comparison.

## Reasoning quality: 0.62

The concise rationale identifies two genuine weaknesses in the cert petition:
the waived response and the distinction between military-specific statutory
protections and the proposed civilian remedy. The petition itself acknowledges
uniformly adverse civilian decisions, so questioning whether its military
comparators establish a true appellate conflict is well grounded. These support
a low grant probability independently of knowing the denial.

The probability derivation is materially weaker. The analysis starts with only
the most recent prior Term's 5.7% reached-baseline rate rather than pooling the
eligible Terms. More importantly, it then uses a terminal zero-relist bucket as
the operative 1.2% anchor for a live petition with one distribution. A petition
that has not yet been relisted can subsequently be relisted; the terminal
population is not the same prospective risk set. The cited 1.2% also counts
`granted` alone: the displayed bucket adds 0.5% GVRs, producing approximately
1.7% on the headline any-grant axis. Its adjustment therefore starts from both
a selected population and an incomplete grant-family numerator.

The doctrinal explanation remains limited to identifying the mismatch; it does
not develop the section 337(a) enforcement obstacle or the right/remedy inquiry
described in the supplied petition. Calling salience minimal because the
petitioner is private and seeks a novel remedy is an assertion, not a sufficient
assessment of institutional importance. These are limitations of the rationale
itself, not a penalty for brevity, retrieval telemetry, or any ancillary forecast.

## Leakage and retrieval disclosure

The harness records forward mode and 29 calls on September 17, before this
petition's October 5 disposition. All call results are unobserved. I do not
interpret their null dates or digests as empty results, nor treat 0.0 capture
coverage as misconduct or a defect. Visible searches target the Ninth Circuit
docket and the case caption. They are legitimate retrieval for an unresolved
forward case, not evidence of leakage merely because one query lacks a date
filter. The rationale does not presuppose the denial. On the visible timing,
queries, and prose, I record no evidence of retrieved outcome material,
`not_applicable` influence, and no suspected leakage; unseen result content
cannot independently be audited here.

One disclosure discrepancy is recorded in the cell's `flags.json`: retrieval.md
says no corpus queries were executed, but the harness logs a shell call attempting
`fedcourts query --court scotus --decided-before "2026-09-17" | head -n 5`
at 19:16:43.851Z. Its result is unobserved, so I cannot say that the command
succeeded, returned records, or incurred transfer. The note should distinguish
an attempted query from no attempt. This discrepancy is not evidence that the
candidate knew the outcome and does not change its numerical scores.

I read the pointed-to forecast for context only and did not grade its separate
CVSG, disposition-route, writing, or merits assertions. Quantitative claim scores
remain the harness's; no cert vote or semantic grade is written. The optional
independent stakes assessment is omitted after exposure to candidate stakes
material. No external retrieval was needed.
