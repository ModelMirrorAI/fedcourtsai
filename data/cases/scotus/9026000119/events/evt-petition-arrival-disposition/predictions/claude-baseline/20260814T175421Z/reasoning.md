# Rationale — why P(grant) = 0.06

## The cell and its anchor

This is an arrival-moment cert cell (`moment: arrival`): zero distributions,
no CVSG, forecast before any docket-acquired signal exists. The frozen context
carries `band: state` under `sal-v2` — the caption-class band for a
state/territorial government petitioner (Guam, through its elected Attorney
General). Per `docs/salience.md`, the state class never drives arrival
selection, so this cell exists via the random arrival draw; the band is the
caption class, fixed at filing and legitimately observable at arrival.

The statpack's sal-v2 band table carries a `state` column, so the published
anchor for the frozen band exists. Pooling the **bracketed `reached`** figures
over all nine rendered Terms strictly before this case's (OT2017–OT2025, the
rendered window being the pooling window) gives **≈ 36.0%** (507/1410
weighted). I did **not** adopt that as my prior, for a reason recorded in
`flags.json`: the reached-state risk set is nested and terminal-band-keyed, so
it pools the `federal` and `high` terminals — populations selected on docket
trajectory (relists, CVSG) or on the federal carve-in class. At arrival, a
state-caption petition has none of that trajectory, and the class itself never
climbs to `federal`. The arrival-time rate for the state *class* is better
reconstructed from the same table's terminal-state figures — pooled ≈ **15.5%**
(41/264 over OT2017–OT2025) — plus something for the class members that later
strengthen into `high`, i.e. a class marginal of very roughly **15–20%**. That
is my starting anchor, consistent with the general prior that state-government
petitioners grant far above the paid-segment rate (pooled paid-segment
bracketed rate ≈ 6.5%).

## Adjustments — this petition sits far below its class average

The state-class rate is carried by state AG/SG offices filing selective,
professionally drafted petitions, typically on developed splits. Reading the
provisioned petition text (98 pp., fetched clean), this petition lacks
essentially every correlate of that class rate:

- **No split — the petition concedes uniformity.** It states the federal rule
  against office-wide disqualification is "uniformly settled" and asks the
  Court to *extend* it to state and territorial courts. An extension request
  with no lower-court conflict is the classic deny.
- **Inverted constitutional theory.** The claim is that "the People of Guam" —
  the government, as an "artificial person" — hold Fourteenth Amendment due
  process and equal protection rights that the Supreme Court of Guam violated.
  A government claiming due-process rights against its own courts runs into
  settled doctrine that a State is not a "person" for these purposes; the cert
  pool will flag it immediately.
- **Thin authority.** The certworthiness argument rests on one Tenth Circuit
  case (*U.S. v. Bolden*), two district-court decisions (D. Utah 1995;
  D.P.R. 1971), and general citations to *Heller* and *Boumediene* for
  propositions they do not carry.
- **Vehicle problems.** The underlying disqualification was under the Guam
  Rules of Professional Conduct (GRPC 1.7) and the Guam Supreme Court's
  supervisory authority under 48 U.S.C. § 1424-1(a)(6) — a plausibly adequate
  local-law ground; the federal notice theory looks first-pressed at the cert
  stage; and the petition is filed by the very office the court below
  disqualified, inviting a threshold representation objection.

Against that, three things keep the number well above the baseline band's
~1% and at the paid-segment rate rather than below it:

- **Structurally dramatic and arguably review-evading facts.** A territorial
  supreme court disqualified the entire elected AG's office — the only body
  empowered to prosecute under Guam law — then dismissed a public-corruption
  appeal when no substitute appeared, having directed no one to appoint one,
  and has already applied the ruling to a second case (CRA24-023). The
  "evades any other review" point is substantially true (no District of Guam
  appellate route), and the Court is the only forum.
- **Government petitioner with a real federal-structure hook.** The office is
  a federal statutory creation (48 U.S.C. § 1421g(d)); an Organic Act
  separation-of-powers question lurks even if poorly presented, and a state-AG
  amicus coalition supporting review is conceivable.
- **Direct jurisdiction is clean.** 28 U.S.C. § 1257(a) / 48 U.S.C. § 1424-2;
  the petition is timely (extension to July 19, 2026, a Sunday, filed
  Monday July 20) and paid.

Netting these: I take the class marginal (~15–20%) and cut it by roughly
two-thirds for the petition-quality and vehicle defects, landing at
**P(any grant, GVR and summary reversal included) = 0.06** — essentially the
unconditional paid-arrival rate (~6.5%), which is where this case belongs: the
caption-class uplift and the case-specific defects approximately cancel.
`predicted_disposition: denied`; `granted: 0`.

## The other claims

- **relist-increment = 0.96.** From a zero-distribution state this is P(the
  petition is ever distributed). A docketed paid petition with a response due
  reaches a conference unless withdrawn or terminated first; a criminal
  prosecution posture cannot settle out under Rule 46 and the petitioner AG is
  visibly determined. The residual covers procedural termination oddities.
- **cvsg-increment = 0.03.** Paid-segment CVSG incidence is ~1.3%
  (173/13,404 in the statpack's CVSG cut). I adjust up modestly for the
  genuine federal interest in the Organic Act office, capped low because CVSGs
  track petitions the Court is seriously entertaining, which I forecast this
  is not.

## Uncertainty and where to discount me

The dominant uncertainty is my quality judgment: I am weighing a
professionally unusual petition (drafted in-house by a small territorial AG
office) heavily against its class, and if a Justice's chambers engages with
the review-evasion structure rather than the drafting, a call for response and
a relist would follow and 0.06 would look low. Conversely, if the
representation defect (the disqualified office filing the petition) draws a
motion or the waived-response path runs silent to the long conference, the
true number is nearer the baseline 1–2%. The statpack's per-Term state-band
cells are thin (n = 15–46 per Term), so the 15.5% terminal-class anchor
itself carries wide error. I consulted no material postdating the snapshot;
retrieval beyond the provisioned inputs was minimal and is listed in
`retrieval.md` (the corpus citation lookup for a comparable Guam prior
returned nothing — a stated coverage gap — so my sense that direct grants
from the Supreme Court of Guam are rare-but-real rests on general knowledge,
e.g. Limtiaco v. Camacho (2007), not on a corpus row).
