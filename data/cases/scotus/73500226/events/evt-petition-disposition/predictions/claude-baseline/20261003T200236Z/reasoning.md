# Rationale for the numbers (claude-baseline, run 20261003T200236Z)

**P(grant) = 0.60.** This is a forward cell (`mode: forward`), band `state` under
`sal-v4`, one distribution, no CVSG, Term 2025, snapshot `2026-10-03.json`
(creation date 10/02/2026 on the supremecourt.gov payload).

**Anchor.** The statpack's *Segment base rate by salience band (sal-v4)* table,
`state` column, bracketed `reached` figure pooled over the Terms strictly before this
petition's docket Term (OT2017 through OT2024): about 22.7% (weighted n = 392). I use
the bracketed figure because the band was frozen at prediction. The OT2025 row
(reached 37.0%, n = 27) contains this case and is excluded. The relist-count cut's
relist-1 bucket (granted 8.2%, gvr 5.1%) and the CVSG `none` bucket (granted 4.0%, gvr
2.3%) describe the shape but are terminal-count buckets, so they are not the forward
hazard from this state.

**Adjustments up, large.** The decisive signal is public information that predates the
snapshot and is on the record of this docket and its companions:

1. *All parties agree the enforcement question is certworthy.* The brief for the
   federal respondents (Aug. 28, 2026) concedes the Sixth Circuit's enforcement
   holding "conflicts with the Fifth Circuit's decision" in *National Horsemen's
   Benevolent & Protective Ass'n v. Black*, 178 F.4th 224 (5th Cir. June 11, 2026),
   and that a federal statute held facially invalid "provides a further reason to
   grant certiorari on that question." The Authority's response (Aug. 28) says the
   same and "welcomes consideration of th[e] question presented through either
   case." The petitioners' reply (Sept. 15) asks for a grant here alone or a grant
   plus consolidation.
2. *The Court has already shown it wants this question settled.* It GVR'd the
   Fifth, Sixth and Eighth Circuit decisions in June 2025 in light of *Consumers'
   Research*; the Fifth Circuit on remand held "Consumers' Research does not change
   our analysis," reinstating the split on a federal statute's validity with the
   federal government now petitioning (No. 26-201, filed Aug. 14, 2026).
3. *The reschedule is cluster alignment, not hesitation.* This petition was
   distributed for October 9 and rescheduled September 21, while replies in Nos.
   26-199 and 26-201 were filed September 30 and the Gulf Coast Racing and Texas
   petitions (Nos. 26-332, 26-335) have responses due October 13 and 14. The Court
   is plainly holding this petition to consider it with the Fifth Circuit cluster.

**Adjustments down, substantial.** The federal respondents and the Authority both
ask the Court to grant Nos. 26-199 and 26-201 and *hold* this petition, and the
Court follows the Solicitor General's vehicle recommendation more often than not.
The petition also carries a second question (rulemaking) with no conflict, which the
government uses against it as a vehicle. So a plenary grant here is less likely than
not even though review of the question is near certain.

**How I built the number.**

| Branch | Probability |
| --- | --- |
| Court grants review of the enforcement question this Term (some vehicle) | 0.92 |
| This petition granted plenarily and consolidated, given review | 0.38 |
| This petition held, then GVR'd because the Court invalidates the enforcement provisions, given review and no plenary grant | 0.45 |
| Grant of any kind if the Court takes no case at all | 0.02 |

P(grant) = 0.92 × (0.38 + 0.62 × 0.45) + 0.08 × 0.02 ≈ 0.61, which I round to 0.60.
`predicted_disposition` is `granted` because the single most likely grant outcome is
a consolidated plenary grant (about 0.35 unconditional) against a GVR (about 0.26);
a hold-then-deny (about 0.31) and other denials (about 0.08) make up the complement.

**The 0.45 for invalidation** reflects a conservative majority receptive to private
nondelegation claims (the petition quotes Justice Alito's *Texas v. Commissioner*
statement and then-Judge Kavanaugh's *Aiken County* footnote), set against
*Consumers' Research*'s accommodating treatment of private participants, the high
bar for facial challenges under *Moody* and *Rahimi* that the government leans on,
and the FTC's December 2025 enforcement-rule modification, which the government
offers as curing the Fifth Circuit's concern. I am genuinely uncertain here and a
reader should discount the GVR branch accordingly.

**Claims.** `relist-increment` 0.97: a rescheduled petition must be redistributed to be
considered, and the statpack notes a reschedule before first consideration adds a
distribution entry under the `dist-v2` reading. `cvsg-increment` 0.01: the Solicitor
General is a party. `summary-disposition-route` 0.42: the GVR share of the grant
outcomes in the branch table above (0.26 / 0.61); the statpack's whole-docket GVR
share of the grant family is about 0.47 and the state band's terminal split is
similar, so this is close to the population shape rather than a strong departure.
`dissent-from-denial` 0.12: the dominant denial path is a hold followed by a denial
after the Court upholds the Act in the lead case, where a separate writing on a held
docket is unusual; a dissent is plausible mainly in the unlikely outright-denial
branch.

**Big-case score 0.72.** Facial constitutionality of a federal statute under a
doctrine three Justices have said needs clarification; the subject industry is narrow,
which keeps it below the top tier.

**Caption class.** Lead petitioner is the State of Oklahoma (with West Virginia and
Louisiana); the harness band `state` matches the caption, so no fallback anchoring
was needed.

**Documents used.** `questions-presented.txt` and `petition.txt` (50 pages, full text,
not truncated) from `record/documents/`; `documents.json` lists no brief in
opposition, so I retrieved the federal respondents' brief, the Authority's response,
and the petitioners' reply from supremecourt.gov myself (forward mode, unrestricted),
along with the FTC's petition in No. 26-201 and the dockets of Nos. 26-199, 26-201,
26-332 and 26-335. One CourtListener MCP search for post-July-2025 circuit opinions
returned nothing (the June 2026 Fifth Circuit opinion is evidently not yet indexed),
so the Fifth Circuit remand holding comes from the parties' briefs and the Fifth
Circuit's own published opinion as described in secondary coverage. Two `fedcourts
query` calls returned recent SCOTUS rows but nothing topically similar; they did not
move the number.

**Where to discount me.** The number rests heavily on reading the Court's likely
vehicle choice from the parties' briefs; if the Court grants this petition alongside
the Fifth Circuit cases the probability was too low, and if it denies the rulemaking
half and holds the rest the GVR branch carries the whole forecast. I did not find any
indication that this petition's disposition has already occurred; the live docket
fetched today ends at the September 21 "Rescheduled" entry.
