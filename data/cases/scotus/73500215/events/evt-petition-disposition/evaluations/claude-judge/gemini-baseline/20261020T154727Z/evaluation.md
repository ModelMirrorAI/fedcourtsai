# gemini-baseline — scotus/73500215, evt-petition-disposition (cert)

**Outcome:** denied (2026-10-19), no noted dissent. **Prediction:** denied, P(grant) = 0.25.
`correct` = 1; Brier = 0.25² = 0.0625. The prediction froze a band (`baseline`, sal-v4), so the segment base rate, basis and skill are the harness's stamp; I record none.

**Reasoning quality 0.50.** It gets the right direction and spots the main signals: the response request after a waiver, and the Court's habit of summarily reversing Ninth Circuit QI denials (*Emmons*, *Kisela*). But the analysis is thin. The anchor is quoted loosely from two Terms ("~5.7–5.9%") rather than pooled over the prior-Term window, and the move to 0.25 (about 4–5× the anchor) is asserted, not argued. It names vehicle problems only as an "uncertainty", in the petitioner's framing (disobeying commands, scaling a fence). It does not engage with the Ninth Circuit's plaintiff-favorable reading of the record, the unpublished/unanimous posture, the lack of a split, or the BIO, which it did not read. The 0.35 conditional dissent-from-denial is weakly supported for a fact-bound officer-side QI petition (the realized denial had no noted dissent), though that claim is scored in code and not here. Its distribution and route reads are reasonable.

**Leakage:** forward, clean. Every logged call is `unobserved` (coverage 0.0, which is this engine's normal shape), so I graded on queries. These are provisioned files, the statpack, and generic corpus queries naming no case. Nothing targets this petition's disposition. `not_applicable`.

**Semantic grades:** none — cert cell, no declared set.
