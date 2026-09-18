# Rationale

## Evidence and information boundary

This is a forward cert-stage prediction of the petition's disposition, not a merits judgment. The event has no express stage or moment field; its petition kind and `evt-petition-disposition` identifier select the cert contract. I used the provisioned September 17, 2026 snapshot, questions presented, and substantive sections of the petition and brief in opposition. The document manifest marks both briefs nonempty and untruncated. The reply is recorded as filed on August 17 but its text is not provisioned; I did not retrieve it or assume what it says.

The frozen context is `sal-v4`, band `elevated`, Term 2025, two distributions, no CVSG, and observable proceedings. The snapshot identifies paid docket 25-1187 and the New York Court of Appeals as the court below. I retain that frozen band; the municipal respondent does not make these private petitioners a government-caption class. I did not retrieve this case's live docket, disposition, subsequent history, or decision coverage, and I do not know its eventual outcome. External retrieval was confined to older general precedent.

## Quantitative anchor

The committed `metrics/statpack.md`, “Segment base rate by salience band (sal-v4),” matches the context version. I pool every displayed Term strictly before 2025 using the **bracketed reached** elevated rate, not the terminal-band rate:

| Term | Reached rate | Weighted resolved denominator |
| --- | ---: | ---: |
| 2024 | 17.9% | 336 |
| 2023 | 17.5% | 354 |
| 2022 | 19.0% | 300 |
| 2021 | 20.5% | 342 |
| 2020 | 16.1% | 397 |
| 2019 | 13.8% | 334 |
| 2018 | 15.9% | 347 |
| 2017 | 17.5% | 400 |

Weighting the displayed percentages by their denominators gives approximately **17.24%**, with total weighted denominator **2,810**. This is approximate because the printed percentages are rounded. Terms 2025 and 2026 are excluded. These are figures from the committed pack available in this checkout, not a freshly queried corpus; I did not load the remote blob or establish its current freshness.

I also read the pack's modern-cert, originating-court, paid-segment relist, and CVSG cuts. The paid relist buckets show much higher grant-family shares at terminal counts of two or more than at zero; the CVSG cohort also has a substantially higher grant-family share than the no-CVSG cohort. These are terminal-state descriptive cuts, not estimates of the next-distribution hazard, and I do not substitute them for the prior-Term reached-band anchor. This case comes from a state high court, so the Second Circuit bucket is not its originating-court prior.

## Why 0.32 rather than the anchor

**A concrete legal disagreement raises the probability.** The petition, pp. 13–19, contrasts the New York in-lieu-only rule with the North Carolina Supreme Court's treatment of monetary exactions. I independently checked *Anderson Creek Partners, L.P. v. County of Harnett*, 2022-NCSC-93, paragraph 42, through CourtListener opinion 9348052. Its reasoning expressly extends beyond fees substituted for land dedications. That supports a genuine disagreement on the legal proposition, though it does not establish that the different property regimes yield indistinguishable vehicles. The petition's additional authorities do not all carry equal weight: the BIO, pp. 22–24, disputes their holdings, precedential status, or procedural maturity.

**There is a plausible doctrinal opening, not an already dictated result.** *Sheetz v. El Dorado County*, 601 U.S. 267, 279–281 (2024), checked through CourtListener opinion 11066690, rejected a legislative exemption while leaving other issues open. Justice Sotomayor's concurrence, joined by Justice Jackson, emphasized the antecedent compensable-taking inquiry. I treat that concurrence as evidence of an unresolved issue, not a majority holding that every monetary demand qualifies. This leaves room both for clarification and for disagreement over whether this petition presents the question cleanly.

**The docket shows real attention, but not a mature relist sequence.** Five amicus filing entries and the June 2 response request after a waiver support taking the petition more seriously than a routine unsupported filing. However, the August distribution follows the requested BIO and summer interval. I do not interpret two recorded distributions as repeated failures to dispose of the petition after full briefing, or count the response request as a CVSG. The elevated prior already incorporates docket selection, so these signals warrant restrained rather than multiplicative adjustment.

**The vehicle objection is substantial but contested.** The BIO, pp. 12–21, argues that the applicants lack a relevant unrestricted-residential property interest, that conversion is optional, and that the narrow question presented would leave an independent ground untouched. That makes denial possible even for Justices skeptical of the in-lieu rule. But the petition does address entitlement and voluntary permitting at pp. 25–29; I do not accept the BIO's characterization that it simply ignores the problem. The petition argues that discretionary benefits are precisely where unconstitutional-conditions protections operate. Whether this is an independent state-law obstacle or a reviewable federal misconception is itself disputed. I therefore discount for vehicle risk without treating jurisdiction as conclusively absent.

Together, the verified legal disagreement and response request justify moving meaningfully above the approximately 17% anchor; the alternative-ground dispute, distinctive artist-loft regime, and modest procedural history keep the forecast below even odds. **0.32** is a judgmental synthesis, not a fitted estimate. The modal label remains denial.

## Other claims and stakes

The **0.46** further-distribution probability reflects a substantial chance of additional examination but no established multi-conference persistence. **0.04** for a CVSG reflects the limited apparent need for federal-government input. **0.16** for a summary route is conditional on a grant: the legal disagreement favors plenary resolution, while possible straightforward correction leaves a smaller summary branch. **0.18** for a dissent or statement is conditional on denial, recognizing the property-rights issue while retaining silent denial as the modal result. These four estimates are subjective; the terminal cuts do not supply conditional forward hazards for this specific record.

The **0.65 big-case score** measures potential nationwide consequences for monetary land-use conditions, not the likelihood of certiorari. The local arts-fund program and large charges alleged in the question presented illustrate the stakes, but the distinctive restricted-use properties limit the case's immediate breadth. The absence of the reply and independent review of the complete lower-court appendix are important limits on my vehicle assessment. No outcome-revealing material informed this forecast.
