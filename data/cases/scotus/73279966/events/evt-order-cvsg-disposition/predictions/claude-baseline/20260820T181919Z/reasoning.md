# Rationale — claude-baseline on scotus/73279966, evt-order-cvsg-disposition

**P(grant family) = 0.55.**

**Anchors.** My cell's frozen context is band `high` under `sal-v3`, term
2025, one distribution, CVSG dated 2026-05-18, forward mode. The statpack's
per-Term band table is computed under the same `sal-v3`, so it is a valid
anchor: pooling the `high` band's bracketed `reached` rates over Terms
strictly before 2025 (2017–2024, n ≈ 1,074 weighted) gives ≈ 41%. The CVSG
cut on the paid scored segment gives a grant family of ≈ 35% conditional on a
CVSG (granted 29.4% + gvr 5.5%, n = 163 resolved). So the population yardstick
for a petition in exactly this posture is roughly 0.35–0.41.

**Adjustments up from the anchor.**
- *The Solicitor General's likely position.* The petition states — and the
  BIO does not contest — that the United States has backed GEO's
  intergovernmental-immunity/preemption position across the last three
  administrations, and the current administration's stake in ICE detention
  contracting is unusually strong (the judgment forced suspension of the
  voluntary work program at a federal facility). I put P(SG recommends grant)
  around 0.7, and the Court follows a grant recommendation most of the time.
  A rough decomposition (0.7 × 0.75 + 0.3 × 0.15 ≈ 0.57) sits above the
  empirical anchor.
- *A clean, recently deepened split claim.* 2d (Town of Windsor), 3d
  (CoreCivic v. Governor of N.J., 145 F.4th 315 (3d Cir. 2025)), and 4th
  Circuits against the Ninth on whether contractors performing federal
  functions get the government's own immunity.
- *Recent precedent in the same posture.* United States v. Washington, 596
  U.S. 832 (2022) reversed the Ninth Circuit on a Washington law burdening
  federal contractors; the discrimination theory here (Washington exempts its
  own detainees) maps onto it directly.
- *Speed of the CVSG.* Invited four days after the first conference, on the
  first distribution — the Court reached for the SG immediately rather than
  relisting, a sign of live interest.
- *Stakes and counsel.* ~$37M judgment, Paul Clement for petitioner, a trade
  amicus (Day 1 Alliance / Professional Services Council) already at the
  petition stage.

**Adjustments down / uncertainties.**
- *Vehicle risk is real.* The BIO's strongest cards are fact-bound: the ICE
  contract required GEO to comply with state and local labor laws, ICE told
  GEO there was "no maximum" on detainee pay, and GEO in fact paid above $1
  when it suited it. If the SG treats those as making this a poor vehicle,
  the recommendation could be to deny despite the government's doctrinal
  sympathy, and the Court would very likely follow.
- *The split is contested.* Washington's BIO argues CoreCivic expressly
  aligns itself with the Ninth Circuit's framework; if that reading holds,
  the split evaporates into case-specific application.
- *State-law predicate is settled.* The Washington Supreme Court held
  detainees are employees under the MWA, so only the federal defenses are
  open — that sharpens the QP but also means a grant decides a constitutional
  question on a jury-trial record.

Netting these, I land at **0.55** — above the ~0.35–0.41 population anchors
because the SG-alignment and split signals here are stronger than the median
CVSG'd high-band petition's, but well short of the ~0.7+ I would give a case
where the SG's recommendation were not the dominant uncertain node.

**Other claims.** Relist increment 0.96: a CVSG'd petition is redistributed
once the SG files, failing only on withdrawal/settlement-style exits. CVSG
increment 0.02: already on the docket — vacuous for this cell; the harness
masks it. Summary-disposition route 0.05 conditional on grant: no intervening
decision to GVR against (Menocal, decided 2026-02-25, was appealability only),
and a summary reversal of a jury judgment on a contested split is not this
Court's practice. Dissent-from-denial 0.20 conditional on denial: no published
baseline exists for this claim; 0.20 reflects that most denials draw no
writing, adjusted up for a high-band CVSG'd federalism case with the federal
government's stated interest on the petitioner's side.

**Inputs and caveats.** I worked from the provisioned snapshot (2026-05-19,
truncated provenance), the provisioned petition, QP, and BIO texts (the BIO
file concatenates Washington's and the Nwauzor class's briefs; both are
page-truncated per documents.json, so my read of each is of its front
sections including the full reasons-for-granting/denying tables and
introductions), the committed statpack, two corpus queries, and two
CourtListener lookups (retrieval.md). I did not query this case's own docket
beyond the snapshot, so I do not know whether the SG has filed or anything
else has happened since 2026-05-19; the forecast is from the frozen record.
Statpack figures are from the committed `metrics/statpack.md` in this
checkout. My main uncertainty is the SG's actual recommendation, which
dominates the posterior; a reader should discount my 0.55 toward the ~0.4
anchor to the extent they think the vehicle problems will drive the SG to a
deny recommendation.
