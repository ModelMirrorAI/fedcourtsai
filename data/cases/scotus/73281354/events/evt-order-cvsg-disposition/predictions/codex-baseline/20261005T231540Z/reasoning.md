# Rationale

## Evidence and vantage

I assign **P(any grant) = 0.45** and predict **denial**. This is the cert-stage CVSG moment in AstraZeneca Pharmaceuticals LP v. Mosaic Health, No. 25-1070, not a prediction about the ultimate antitrust judgment. Any grant includes plenary review, a limited grant, GVR, or summary reversal; it is not a probability that the manufacturers ultimately win.

I read the provisioned `2026-10-05.json` snapshot, `event.yaml`, `context.json`, `documents.json`, the questions presented, and the principal arguments and vehicle discussions in the petition and brief in opposition. The documents manifest reports both briefs as nonempty and untruncated. References below use their printed page numbers. The reply is recorded as filed but its text is not provisioned and I did not retrieve it. Nor is there an SG recommendation in the baseline.

The frozen context is forward mode, sal-v4 band **high**, docket-number Term **2025**, and **two distributions**, with a CVSG on **October 5, 2026**. Although the snapshot contains three lines saying DISTRIBUTED, two concern the same September 28 conference with an intervening rescheduling. I use the harness's count of two, not three presumed substantive considerations. The April response request also interrupted the earlier schedule. These facts do not establish repeated substantive relists. The October 6 date cutoff bounds the supplied snapshot, not forward retrieval. I did not retrieve this petition's disposition or subsequent docket history, and do not carry a known outcome for it.

## Calibration

The committed `metrics/statpack.md` sal-v4 table matches the context. Pooling **all displayed Terms strictly before 2025**, namely 2017–2024, gives **314 / 898 = 34.97%** for the high band's bracketed reached rate. I calculated this from `metrics/statpack.json` using each high segment's `prefix_weighted_resolved` and `prefix_est_grant_rate`. I exclude the 2025 and 2026 rows even though the CVSG occurred in calendar 2026: the conditioning Term is the docket-number Term, not the October Term in progress when the order issued.

The paid-segment CVSG cut is consistent with that starting point: 163 weighted resolved petitions, 29.4% ordinary grants plus 5.5% GVRs, or about **34.9% any grant**. That all-Term cut is a descriptive cross-check, not a second prior or an independent adjustment. The relist cut also describes terminal buckets, not the hazard of another distribution from the present state. I do not substitute the whole-docket grant rate or multiply correlated CVSG and high-band signals.

These figures describe the committed pack, whose last modifying commit is `808f812e9`, dated September 28, 2026. They are not asserted to describe a freshly pulled corpus. An attempted `fedcourts corpus-info` could not report corpus-wide pull/snapshot freshness because the cell uses the service backend without a client-side connection. The case evidence's known vintage is the provisioned October 5 snapshot; no separate case-level `last_pulled` value was supplied.

## Why 45%, rather than 35% or a likely grant

The strongest upward consideration is **QP1's substantive disagreement about indirect-purchaser standing and lost-profit claims**. Petition pp. 13–17 identifies the Third Circuit's Howard Hess decision and the Sixth Circuit's Academy of Allergy litigation, including separate writings explicitly discussing the Second Circuit's different approach. This is more concrete than an unsupported assertion that a fact-bound result conflicts with general antitrust principles. A rule affecting which businesses may bring federal antitrust damages actions extends beyond this particular pharmaceutical dispute. The Court's response request and business amici reinforce attention and broader relevance, although the CVSG itself is already incorporated in the anchor. See snapshot proceedings; petition pp. 25–27.

The opposition supplies substantial reasons not to move above 50%. It argues that the challenged policy eliminated a purchasing channel rather than imposing an overcharge passed through a chain: the providers were the first injured parties, intermediaries had no duplicative claim, and the cited circuit cases involved different injury structures. That makes the conflict's precise scope contestable and the 340B transaction mechanics an important vehicle complication. It also questions preservation, which I treat as an adversarial contention, not an established defect. See BIO pp. 26–33 and n.6.

For general doctrinal context I checked Apple Inc. v. Pepper, 587 U.S. 273, 279, 285–87 (2019), through CourtListener's opinion record. Its categorical direct-purchaser language supports petitioners' concern, but its discussion distinguishing separate injuries from passed-on overcharges gives respondents a serious response. Those passages do not settle how a blocked contract-pharmacy transaction should be characterized here. I therefore do not equate a plausible merits argument with a clean cert vehicle.

**QP2 is materially weaker as a reason for review.** Petition pp. 21–25 treats lobbying and association membership as an improperly credited plus factor. BIO pp. 17–20 responds that the panel relied on a broader combination of alleged parallel conduct, common incentives, and action against individual economic interests, with communications only providing additional support. On this record the latter characterization makes fact-bound application of Twombly a substantial obstacle to review. I do not treat alleged conspiracy as a proven fact or independently resolve the parties' competing readings of the appendix.

Taken together, the identified QP1 conflict and its commercial reach warrant an upward adjustment from roughly 35% to **45%**, while the opposition's distinctions, the remand/pleading posture, and the unknown SG recommendation keep denial the modal disposition. The BIO's discussion of the separately pending United Biologics petition, No. 25-1388, also leaves a possible hold-and-GVR route; I have not checked that petition's later status. My forecast rests on its pre-decision mention in BIO pp. 33–35, not on any assumed grant in that matter.

## Additional numbers

- **Further distribution: 0.96.** I expect the invited federal brief to be followed by renewed conference distribution. This prices any increase from two, not necessarily a contested relist after actual consideration. Withdrawal or unusual procedural termination supplies most of the small complement.
- **CVSG increment: 0.00.** The invitation has already issued. The required claim is vacuous and harness-masked; zero is not a denial of the observed invitation.
- **Summary route given any grant: 0.20.** A plenary or limited-question grant is more likely than immediate disposition. A related-case hold followed by GVR accounts for most of the summary-route possibility; immediate summary reversal is a weaker fit for the disputed legal and factual characterization.
- **Separate writing given denial: 0.12.** There is a plausible disagreement worth flagging, but I expect an unsigned denial without a public statement. I make no per-Justice prediction.
- **Stakes: 0.65.** The potential effects on national antitrust litigation and safety-net pharmacy access are substantial, while the particular vehicle could produce a narrow, technical ruling. This score is independent of the grant probability.

The principal uncertainty is the SG's eventual assessment of the split and vehicle, not the existence of the CVSG. The timing forecast is a judgmental horizon, not an estimate from the pack's mixed-population termination-time statistic.
