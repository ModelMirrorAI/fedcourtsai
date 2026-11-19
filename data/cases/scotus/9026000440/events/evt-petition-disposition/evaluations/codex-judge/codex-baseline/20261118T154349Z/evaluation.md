# Evaluation of codex-baseline

This is a cert-stage evaluation of Mohammed Jabateh v. United States, No. 26-440. The prediction called denial with P(any grant) = 0.035. The recorded outcome is denial on November 16, 2026, so `correct = 1` and `brier_score = (0.035 - 0)^2 = 0.001225`.

## Rationale

`reasoning_quality = 0.94` grades reasoning.md alone. The analysis separates certworthiness from the substantial liberty interest and gives concrete reasons for a low grant probability: a nonprecedential collateral decision, no identified circuit conflict, an already-litigated claim and a waived response. It also takes the petition's strongest argument seriously: twenty additional years on counts outside the statute's scope. Those features are supported by the petition, especially pp. 9–20, and the appendix, App. 1a–9a.

Its strongest legal distinction is that the favorable construction occurred on the petitioner's own direct appeal rather than through a later intervening decision. The appendix expressly relies on that distinction at App. 6a–7a and 18a–19a. It also correctly distinguishes relitigation from procedural default (App. 7a n.3), and deficient performance from Strickland prejudice (App. 8a–9a). The petition's claimed waiver of default therefore does not dispose of the lower court's actual rationale. These are reasons for a defensible forecast, not findings that the silent denial approved the lower court's law.

The adjustment from the statistical anchor to the individual probability remains a judgment rather than an empirically estimated effect; the rationale acknowledges this. The waiver and absence of a split carry predictive weight but do not quantify the residual chance of exceptional error correction. That limits precision without undermining the core analysis.

I assessed base-rate use against reconstructed statpack build `7bcde3b105cb212283905eda17b827efc188e80c` (landed October 28, 2026; digest `sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`), obtained by `fedcourts statpack-at`. It differs from today's pack and has no alternative build. The candidate correctly uses the sal-v4 bracketed reached population, strictly prior Term rows, private-petitioner class and grant-family definition. I have not substituted today's sal-v8 context or reported a separately pooled evaluation anchor. The stamped segment base rate and derived skill belong to the harness.

## Predicted reasoning

`predicted_reasoning_quality = 0.95`. The central procedural calls were specific and held: denial after the first conference, zero further distributions and no CVSG. The docket records the single October 28 distribution for November 13, followed by the November 16 denial; outcome.signals agrees. These claims discriminate between plausible procedural paths and earn more than generic credit for denial alone.

The prediction of no separate writing is supported as to a noted dissent by `noted_dissent_from_denial = false`. The broader absence of a statement or explanation is unresolved because the record contains neither a full disposing order nor a complete inventory of writings. Conditional discussion of summary reversal, the question selected and remand is untested after denial and earns neither credit nor penalty. No inferred reason for denial is treated as a Court holding.

## Leakage and scope

The log identifies forward mode and an October 30 prediction, preceding the November 16 resolution. I reviewed all 53 calls: 52 have captured results and one web search is unobserved. Its visible query concerns Bousley generally, not this case. The CourtListener searches concern Davis and the comparator corpus query has a pre-October-30 boundary. The log and rationale show no current-petition disposition. The earlier 2021 cert denial is legitimate history of a different petition. An unobserved result is not an empty result, but nothing in that query or the prose suggests the present outcome was sought or used. `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`.

My independent stakes assessment is 0.30: the twenty-year incremental sentence and possible effect on section 2255 doctrine matter, while the nonprecedential ruling, unusual posture and lack of an identified circuit conflict limit broader reach. Cert votes are unscored. No semantic grades apply at this stage, and quantitative claims are left to the harness.
