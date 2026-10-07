# Evaluation of codex-baseline

## Outcome and scores

The cert-stage outcome records denial on October 5, 2026, and `actual_granted = 0`. codex-baseline predicted `denied` with P(any grant) = 0.02. Exact-label correctness is 1; Brier loss is `(0.02 - 0)^2 = 0.0004`.

## Baseline

The prediction's frozen context identifies Term 2026, `baseline`, and `sal-v4`, matching the committed statpack's salience-table version. I pool the bracketed `reached` rates over all nine displayed strictly-prior Terms, 2017–2025, not the leading terminal rates and not the evaluator's context. The rate/weighted-denominator pairs are 3.9%/1140, 5.7%/1271, 5.9%/1312, 5.8%/1192, 5.6%/1500, 4.5%/1739, 4.6%/1399, 4.6%/1524, and 4.7%/1643, in descending Term order.

The denominator is 12,720 and the reconstructed weighted numerator is 637.385, yielding baseline 0.05010888364779874 and skill `1 - 0.0004 / baseline^2 = 0.8406945856527439`. These are approximate computations from rounded, denial-reweighted paid-segment percentages, not exact raw grant counts. The table displays all 10 of its 10 Terms, including excluded Term 2026; no window-divergence flag is needed. No corpus-refresh timestamp is supplied in the consulted markdown, and no fresh corpus total is claimed. The recorded basis is `risk_set`.

## Reasoning quality: 0.88

The rationale correctly separates the private petitioner's risk set from the federal-petitioner class despite the Attorney General's appearance as respondent. It explicitly pools only prior Terms, distinguishes terminal relist statistics from forward transition rates, and identifies the waiver adjustment as judgmental rather than an empirically measured conditional rate.

Its treatment of missing evidence is particularly sound: absent petition text prevents an assessment of conflict, preservation, and vehicle quality but does not itself show that the case is weak. Likewise, elapsed time after conference is not treated as proof of a hold or denial, and the snapshot's filename is not mistaken for a fresh pull timestamp. Retaining a nonzero grant branch is consistent with the acknowledged uncertainty. These strengths justify a high quality grade independently of the correct outcome.

The principal limitation is substantive incompleteness: no questions presented or lower-court analysis supports a case-specific account of certworthiness. The exact reduction from about 5% to 2% remains a plausible but unmeasured judgment. Denial alone neither identifies the Court's reasons nor validates that numerical adjustment. No credit or penalty here comes from the forecast document or the structured claims; those are outside this qualitative score. Cert vote accuracy and semantic grades are omitted.

## Leakage

The logged mode is forward and all 29 calls occurred October 4, before the October 5 denial. The five web calls concern generic Court rules. Their results are unobserved: although the candidate reports unsuccessful retrieval, the log does not independently establish that nothing was returned. The other 24 calls are captured, for overall coverage 24/29, and their queries concern local inputs, aggregate statistics, schemas, calculations, and output production. A command excludes the prohibited labeling path while searching for instruction files; that is not a read of labeling artifacts. Neither queries nor reasoning show this petition's outcome or an already-decided forward input. I record outcome-material retrieval false, influence `not_applicable`, and suspicion false.
