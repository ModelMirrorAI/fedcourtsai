# Rationale

## Prediction and information set

I assign **P(any grant) = 0.015** and predict denial. This is a cert-stage petition-disposition forecast, not a forecast that petitioners lose a merits judgment. The grant probability includes a partial grant, GVR, or summary reversal.

I read the provisioned `record/snapshots/2026-09-17.json`, `record/context.json`, `record/documents/questions-presented.txt`, `record/documents/petition.txt`, and `record/documents/documents.json`, along with this event's definition. The context identifies a forward cell with no cutoff, observable proceedings, one distribution, no CVSG, and the `baseline` band under `sal-v4`. Its Term is 2025, notwithstanding the 2026 calendar date. The private petitioners, not the governmental respondents, determine the relevant caption class.

The snapshot records a paid petition, the respondent's response waiver, and distribution for the September 28, 2026 conference. It shows no request for a response or further distribution. The waiver is evidence about the docket's present posture, not an adjudication of the petition's strength. The document manifest reports an untruncated, nonempty 22-page petition, fetched July 18, 2026; no opposition brief is provisioned, consistent with the waiver. I do not infer opposition arguments from an absent brief.

The case baseline is dated September 17, 2026, but its last listed proceeding is June 24, 2026. I did not retrieve a current Supreme Court docket or this petition's disposition. I have no known outcome to disclose. I retrieved only the already-filed appendix containing the lower proceedings and a cited 2024 appellate precedent. Those retrievals do not supply later Supreme Court history.

## Statistical anchor

The committed `metrics/statpack.md` salience table matches `sal-v4`. Pooling every displayed strictly prior Term, OT2017 through OT2024, gives **593 estimated grants / 11,580 weighted resolved private petitions = 5.1209%** for the bracketed baseline-*reached* risk set. I calculated this from `prefix_est_grant_rate` and `prefix_weighted_resolved` in `metrics/statpack.json`, not rounded printed percentages. I exclude OT2025 and OT2026. I do not substitute the much lower terminal-baseline rate for the reached rate.

The paid-segment terminal relist cut has grant-family rates around 1.7%, 13.3%, 40.9%, and 36.8% in the 0, 1, 2, and 3+ buckets. The CVSG cut is approximately 34.9% with a call versus 6.3% without one. These describe eventual states, not forward increment probabilities. The modern-cert disposition section supplies a low whole-population cross-check, not my selected-population anchor. The case comes from a state appellate court, so I do not assign it a Tenth Circuit originating-court rate.

These figures describe the committed pack, not a newly refreshed corpus. The pack exposes no build timestamp or corpus-wide pull vintage in the fields I consulted; I made no corpus-blob query and make no claim about its current freshness.

## Case-specific adjustment

**The subject warrants attention.** The QP asks whether retention after the authority for an initially valid taking fails itself violates the Fifth Amendment. The petition alleges years of retention after successful tax challenges, with property eventually returned in 2023. It invokes disagreement about constitutional protection for continued possession of seized property. These considerations give the petition more substance than an unsupported error-correction request. Sources: provisioned QP; petition, printed pp. 3–11.

**But the claimed split does not line up cleanly with the proposed holding.** In *Asinor v. District of Columbia*, 111 F.4th 1249 (D.C. Cir. 2024), slip opinion pp. 17–20, the court rejects the idea that potential Fifth Amendment protection excludes Fourth Amendment protection. It does not establish the mutually exclusive Fourth-versus-Fifth alternatives the petition suggests. This supports a recurring Fourth Amendment question without establishing that this Fifth Amendment formulation cleanly presents it. Source: CourtListener opinion 10502326, passages located by the literal phrase `due process`.

**The actual judgment has substantial additional barriers.** The appended Kansas opinion expressly rejects mootness because damages remain at stake. But it separately discusses the state agency's section 1983 defendant status, official-capacity damages immunity, and insufficient allegations against the director individually. It also reads the claim as a Takings Clause claim and identifies tax-assessment, public-use, and vested-interest pleading problems. Thus, changing the abstract constitutional rule might not change the judgment. These are descriptions of the lower court's reasoning, not endorsements of every proposition it states. Source: filed appendix, printed pp. 11a–14a, particularly 12a–14a.

My inference is that the Court would have to navigate both a mismatch between the petition's due-process/retention formulation and the claim adjudicated below, and additional obstacles concerning the defendants and allegations. The petition's final section does not meaningfully resolve those obstacles. Its characterization of *Norman*, *Ecco Plains*, and *Aerolineas Argentinas* as Supreme Court precedents also conflicts with its own lower-court citation identifiers. I discount that claimed direct conflict rather than assuming its accuracy. Source: petition, printed pp. 11–13 and table of authorities.

Taken together, these considerations outweigh the upward pressure from the general retention issue. I move materially below the 5.12% risk-set anchor to **1.5%**, rather than treating an asserted multicircuit split as sufficient by itself. The adjustment is judgmental, not a fitted likelihood ratio. My main uncertainty is whether the Court would overlook this vehicle's obstacles to address the recurring constitutional issue, or identify a narrower corrective route not established by the materials I consulted.

## Other probabilities and stakes

- **Further distribution: 7%.** Starting from one distribution, I expect zero more; one additional distribution is my main alternative. This is an assessed hazard, not the terminal relist table read backwards.
- **New CVSG: 0.2%.** I see little reason for an invitation in this state tax/individual-damages vehicle. A request for the respondent's brief would be a different procedural step, not a CVSG.
- **Summary route given a grant: 12%.** Conditional on the rare grant, a fully briefed consideration is likelier than an immediate disposition. I identified no intervening controlling decision requiring a GVR. Unconditionally, the implied summary-route probability is 0.18%, not the 12% entered in the conditional claim.
- **Separate writing given denial: 3.5%.** The retention allegations could attract attention, but the vehicle weaknesses favor a routine denial. I forecast no named Justice's cert vote or writing.

The **0.34 stakes score** reflects the potential reach of constitutional protections for retained property, discounted for the narrow dispute and its obstacles. It is independent of the grant probability.

## Tool limitations

The browser returned no usable content on four attempts concerning the filed appendix. A direct request to that exact public Supreme Court PDF succeeded; extraction occurred in memory without saving a new input file. The CourtListener citation search for the lower opinion returned no result, so the filed appendix supplied that opinion instead. CourtListener successfully supplied the *Asinor* passages. The initial CLI call could not use its default cache directory; routing the cache to writable temporary storage resolved that environmental issue. None of these limitations required changing inputs, code, or validation.
