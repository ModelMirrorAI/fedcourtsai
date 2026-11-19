# Evaluation: codex-baseline

The cert prediction correctly named denial: `correct = 1`. Against `actual_granted = 0`, its 0.22 probability gives `(0.22 - 0)^2 = 0.0484`. The Court denied the petition on November 16, 2026. Cert votes are not scored; no semantic grading applies. The segment base rate, its basis, and Brier skill are left to the harness.

`reasoning_quality = 0.90`. The rationale carefully distinguishes a pre-conference reschedule from actual post-conference consideration, counts four amici without treating a null context count as zero, and separates marginal terminal statistics from a prospective hazard. Its legal discussion engages both the opposition's immunity argument and the reply's strongest counterargument: the opposition itself calls Minton an outlier (BIO printed p. 20; reply pp. 2-3). It also correctly treats Judge Carson as concurring in the judgment while questioning the majority's breadth (petition App. 34a-38a). These are substantial reasons for a denial forecast without pretending denial establishes the Court's reasoning. The precise downward adjustment remains judgmental and the asserted doctrinal grounds were not adjudicated by the Supreme Court.

Calibration was checked against the candidate's recovered placement build, `ca0c9e1a49e292692bdc5b092cd9f868561169b8`, digest `sha256:9da7dbfa464075bfc7fab6e6b641ec9060684cd53259a76380a32823adf6f653`, rather than the newer committed pack. Its quoted relist, CVSG, and amicus figures match that build. Any skill comparison uses the stamped segment base rate.

## Predicted reasoning

`predicted_reasoning_quality = 0.85`. The specific modal path held: denial immediately following the November 13 conference, no further distribution beyond the existing two, and no CVSG. This earns more than a generic denial call. No noted dissent is recorded, but the absence of an order or writings manifest leaves the broader no-separate-writing forecast unresolved. Conditional grant scope and plenary review were never tested and earn neither credit nor penalty. The denial supplies no substantive explanation of the Court's reasons.

Leakage: `forward`, outcome material `false`, influence `not_applicable`, suspected `false`. The November 9 log predates resolution and shows local baseline reads, unrelated granted-case context, and older precedent research. Its two uncaptured web calls are assessed from their historical-authority queries; they are not credited as empty returns. Nothing shows this petition's own disposition surfacing before the forecast. The evaluator's November 16 snapshot does not redefine that baseline.

My case-significance assessment is 0.58: the questions could affect public participation in legislative hearings nationwide and the boundary between constitutional relief and legislative independence, although this petition concerns a confined procedural setting and produced no Supreme Court merits precedent.
