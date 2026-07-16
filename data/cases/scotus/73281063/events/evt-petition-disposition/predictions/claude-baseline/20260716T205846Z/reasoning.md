# Arizona v. Promise Arizona, No. 25-1022 — petition disposition

**Prediction: denied. P(any grant, GVR included) = 0.22.**

## The case

Arizona (through Attorney General Mayes) petitions from the Ninth Circuit's
consolidated judgment in *Mi Familia Vota v. Fontes*, 129 F.4th 691 (9th Cir.
Feb. 25, 2025), reh'g en banc denied, 152 F.4th 1153 (Sept. 22, 2025), which
partially vacated a post-trial finding that Arizona's H.B. 2243 (noncitizen
voter-roll maintenance) was not enacted with discriminatory purpose, and held
that Promise Arizona had associational standing though it identified no
specific injured member. The questions presented (from the provisioned
`questions-presented.txt`):

1. Whether Article III permits an organization to sue when an unknown number
   of unidentified members "may be" injured (claimed conflict with at least
   seven circuits on *Summers v. Earth Island Institute*), and
2. Whether the Ninth Circuit improperly reweighed *Arlington Heights*
   discriminatory-purpose evidence under the guise of clear-error review.

Facially strong grant signals: a state petitioner, a claimed 7-circuit split,
Judge Bumatay's panel dissent plus eleven judges dissenting from denial of
rehearing en banc, a 25-state amicus brief, amici from FAIR and election-law
scholars, this Court's earlier partial stay in the same litigation (*RNC v.
Mi Familia Vota*, No. 24A164, Aug. 22, 2024), and one relist (distributed
6/18/2026, redistributed 6/25/2026).

## What drives the call: the SG's split recommendation and the companion grant

This petition travels with two companions from the same judgment: RNC v. Mi
Familia Vota (25-1017) and Petersen v. Mi Familia Vota (25-1019). The United
States — a respondent here — filed a consolidated brief (the provisioned
`brief-in-opposition.txt`) **supporting cert in 25-1017 and opposing 25-1019
and 25-1022**. Against this petition specifically, the SG argued: (a) the
discriminatory-intent question is interlocutory (the panel remanded for
further proceedings; the district court may again reject the claim, and
petitioners can return from an adverse final judgment); (b) it is fact-bound
error correction; and (c) the standing question is "mostly a matter of
fact-bound error correction that should await the results of any remand" —
indeed the SG deployed the standing defect as a vehicle problem for this
petition rather than a reason to grant it.

The Court followed that recommendation precisely. Per web retrieval (see
`retrieval.md`), on **June 29, 2026 the Court granted certiorari in 25-1017**
on both NVRA questions (SCOTUSblog case page; Democracy Docket, June 29,
2026). That is a companion case's ruling predating nothing in this case — the
outcome of *this* petition does not yet exist — so it is legitimate forward
signal, noted in `flags.json` because it is decisive.

Critically, this petition was **not denied alongside the grant**. The
provisioned snapshot's source docket JSON was generated 7/1/2026 (after the
6/29 orders list) and was still what supremecourt.gov served at the 7/16
fetch: the last entry remains the 6/22 redistribution, with no denial, no
further distribution, and no disposition. Had the Court intended a simple
contemporaneous denial, it would ordinarily have issued it on the same orders
list. The posture is therefore a **hold pending RNC v. Mi Familia Vota**
(OT2026; decision expected by roughly June 2027).

## Disposition scenarios for a held companion

- **Denied after the merits decision (~0.66).** The modal outcome. The
  intent-remand question is interlocutory and independent of the NVRA
  preemption questions the Court took: whatever RNC holds about §8/§9 of the
  NVRA, the *Arlington Heights* equal-protection remand as to H.B. 2243 can
  simply proceed below, and Arizona can re-petition from a final judgment —
  exactly the SG's proposed path, which the Court has so far tracked.
- **GVR in light of RNC v. Mi Familia Vota (~0.15).** The petitions attack
  the same consolidated Ninth Circuit judgment, and RNC's second question
  concerns the same statute (H.B. 2243). If the Court reverses in a way that
  reshapes the case — particularly if it says anything about the plaintiffs'
  standing, which the SG contested — a GVR of the companions is a natural
  cleanup. Counts as a grant on the binary axis.
- **Plenary grant / consolidation (~0.07).** The associational-standing split
  is genuinely certworthy (eleven en banc dissenters), and this Court has
  shown appetite for organizational-standing questions (*FDA v. Alliance for
  Hippocratic Medicine*). But hold-then-plenary-grant is rare, the posture is
  interlocutory, and the Court just declined the invitation once.
- **Dismissed / withdrawn / other (~0.05).** A year-long hold leaves room for
  mootness or voluntary dismissal (e.g., changed litigation posture in
  Arizona), but nothing in the record points to it.

P(granted incl. GVR) ≈ 0.15 + 0.07 = **0.22**; most likely single label:
**denied**.

## Base-rate cross-check

From the committed `metrics/statpack.md` (modern discretionary-cert slice,
denial-reweighted): paid petitions grant ~5.4% (OT2025) / ~6.9% (OT2024);
one-relist petitions grant 7.6%; CA9-originating petitions 3.0%. The
salience-band table the prompt references is not present in the committed
statpack, so I anchored on the relist and fee-class cuts. This petition's
qualitative signals (state petitioner, en banc dissents, companion stay
history) would normally push well above the 7.6% relist-1 anchor — but the
decisive, case-specific evidence (SG opposition to this petition, the Court
granting only the SG-endorsed companion, and the hold posture) dominates the
cuts and lands the estimate at 0.22, most of it GVR risk. Corpus
`fedcourts query` retrieval returned no comparable priors (see
`retrieval.md`), so no analogous-case adjustment was available.

## Big-case score

0.7 — the underlying controversy (documentary proof of citizenship for voter
registration, NVRA preemption, 2026-cycle election administration) is among
the most watched election-law disputes in the country, now set for plenary
review via the companion; this petition's own questions (associational
standing, appellate review of legislative-intent findings) carry significant
doctrinal stakes beyond election law if ever decided. Scored on the
pre-decision record only.
