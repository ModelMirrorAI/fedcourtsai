# Evaluation: claude-baseline

## Outcome and quantitative scores

This cert-stage outcome records `denied` on October 5, 2026, and `actual_granted = 0`. claude-baseline predicted denial at grant probability 0.015: correctness is **1**, and Brier loss is **0.000225**.

The frozen prediction context is Term 2025, band `baseline`, version `sal-v4`. The matching committed statpack table renders all 10 of its 10 Terms. Its bracketed baseline `reached` rates for strictly prior Terms 2017–2024 pool to weighted denominator **11,580** and weighted numerator **592.925**, using the displayed rounded percentages. The **risk-set baseline is 0.05120250431778929** and Brier skill is **0.9141777072871345**. Neither Term 2025 nor 2026 enters the pool. This is the frozen-band population, not a terminal-band fallback. The values are denial-reweighted committed-pack estimates; no live corpus lookup or freshness assertion is involved.

## Reasoning quality: 0.76

The rationale combines a clear prior-Term anchor with substantial case-specific analysis. It distinguishes Bowe's statutory holdings from the question presented here, discusses the state-custody text, and identifies the unpublished COA posture and unusual custody agreement as vehicle concerns. Its account acknowledges that the limitations issue could be outcome-determinative, rather than treating every procedural obstacle as defeating review. The missing appellate order and the limited value of the broad corpus query are candidly disclosed. The staged retrieval log supports the described searches and document reads, including the pre-prediction companion proceeding.

Some decisive assertions outrun the demonstrated support. The claim that the circuit split does not really reach this petitioner requires a more developed comparison between the disciplinary-custody cases and his executive-agreement custody challenge. The supplied petition expressly argues that analogy; simply observing that he remains subject to state judgments does not itself dispose of the competing interpretation. Likewise, the reported timeliness dismissals do not by themselves establish the broader suggestion that no court found the underlying custody theory colorable. The discussion of counsel's specialization, petition length, and the Court having passed on the split for two decades is weakly substantiated and should carry less weight than the concrete procedural record.

There is also an internal numerical inconsistency: the rationale says its upward considerations keep the prediction marginally above a 1.7% comparison, then selects 1.5%. The JSON probability is unambiguous and is scored as written; the inconsistency reduces explanatory precision. The predictor correctly warns that terminal relist statistics are selected populations, but the argument for the exact downward adjustment remains judgmental.

The realized denial is compatible with the forecast, yet it does not establish that the Court accepted any of these legal explanations. The quality score grades only `reasoning.md`; the forecast document and structured claims are not scored here, and their successful predictions do not inflate this grade.

## Leakage and scope

The log is forward-mode and contains 39 calls, all marked captured. The September 16 prediction precedes the October 5 denial. An own-docket lookup is not intrinsically suspect for an unresolved forward case. Searches of the lower proceedings, the March 24, 2026 companion order, the Bowe material, and the broad recent-grants query likewise precede this resolution. The legible result dates and staged prose reveal no retrieval of this petition's denial and no assumption that it had already occurred. Outcome retrieval is assessed false, influence is `not_applicable`, and leakage is not suspected. Captured result digests support an audit trail but do not substitute for full result bodies; this assessment does not claim visibility beyond what was staged.

Votes are unscored on cert, and no semantic grading set applies. Claim scores and harness-owned stamps remain absent. No optional stakes assessment is supplied after exposure to the candidate's own score.
