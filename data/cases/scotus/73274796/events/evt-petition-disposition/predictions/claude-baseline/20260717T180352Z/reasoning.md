# Renteria v. New Mexico Office of the Superintendent of Insurance (25-113) — cert disposition

**Prediction: GVR (grant, vacate, and remand) as the likeliest disposition; P(any grant, GVR included) = 0.72.**

## The case

Petitioners are two New Mexico members of Gospel Light Mennonite Church Medical
Aid Plan, a health care sharing ministry (HCSM) recognized under the ACA's
individual-mandate exemption, 26 U.S.C. § 5000A(d)(2)(B). New Mexico's Office of
the Superintendent of Insurance found Gospel Light was operating as an
unauthorized insurance carrier, fined it $2.51M, and ordered it to cease
operating in the state. The district court denied a preliminary injunction; the
Tenth Circuit affirmed over Judge Carson's dissent (No. 23-2123, Feb. 27, 2025;
rehearing en banc denied Apr. 28, 2025).

The petition (filed July 28, 2025, paid) presents four questions: (1) whether
*Employment Division v. Smith* neutrality requires proof of subjective religious
animus; (2) whether general applicability lets courts disregard secular
exemptions on a "different purposes"/"ancillary conduct" rationale rather than
comparing risk to the asserted state interest (*Tandon*/*Fulton*); (3) whether
official hostility alone establishes a free-exercise violation; and (4) whether
the ACA's HCSM exemption preempts New Mexico's order.

The BIO (Erwin Chemerinsky, counsel of record for respondents) is
vehicle-focused: interlocutory preliminary-injunction posture, no fact-finding,
no record evidence that exempt secular entities engage in comparable conduct,
petitioners are individual members rather than Gospel Light itself, and a denial
that any circuit split exists.

## The docket signals (from the provisioned 2026-07-17 snapshot)

- Respondents waived; the Court **requested a response** (Aug. 14, 2025) — a
  screening signal that a clerk or chambers saw something worth engaging.
- Distributed for the 9/29/2025 and 10/10/2025 conferences, then on **Oct. 14,
  2025 the Court called for the views of the Solicitor General (CVSG)** — the
  strongest pre-grant signal in the record.
- The **SG's amicus brief was filed May 26, 2026**; the case was redistributed
  for the **6/25/2026 conference**; petitioners filed a supplemental brief
  June 9, 2026.
- As of the snapshot (created 7/16/2026) and a live docket check today, **no
  order has issued after the 6/25/2026 conference** — the petition is still
  pending.

## The decisive forward signal: the SG recommended a hold for *St. Mary*

This is a forward cell, so pre-decision public context is fair game. The DOJ
OSG's public brief listing (confirmed via web search; the DOJ page itself
returned 403 to direct fetch) shows the SG's CVSG response **recommends that the
Court hold the petition pending *St. Mary Catholic Parish v. Roy*, No. 25-581,
which overlaps with the first question presented, and then dispose of the
petition as appropriate.**

*St. Mary* was **granted certiorari on April 20, 2026**. It is another **Tenth
Circuit** free-exercise case (Colorado's universal-preschool nondiscrimination
condition) presenting exactly the *Smith* general-applicability/secular-
exemption comparability question that Renteria's QP1–QP2 raise. It will be
argued in OT2026 and decided by roughly June 2027.

The docket behavior corroborates the hold: a case redistributed once after the
SG's brief, considered at the 6/25 conference, and then left untouched through
mid-July with no relist entry is the classic signature of a petition being held
for a granted lead case. The Court follows SG hold recommendations almost
without exception.

## Base rates and priors (corpus statpack)

- Modern discretionary-cert baseline: grants are ~3% of resolved petitions
  (Term 2025 row: 2.5%).
- **CVSG cut: 27.1% granted / 71.2% denied** (61 CVSG'd petitions) versus 3.0%
  granted without a CVSG — a ~9x lift, and that figure blends hold/GVR
  dispositions into the deny column where GVRs were labeled denials.
- Relist cut: 2+ relists run 22–34% granted; this case has had multiple
  distributions (9/29/25, 10/10/25, 6/25/26).
- Tenth Circuit origin: 5.0% granted, modestly above baseline.
- Corpus priors (`fedcourts query --court scotus --disposition granted --era
  2020s`) include *Hoffmann v. WBI Energy* (25-159): CVSG Dec. 2025 → SG brief →
  distributed 6/25/2026 → **granted 6/29/2026**. That is what a
  grant-recommended CVSG case looked like at the same conference; Renteria's
  silence after the same conference is affirmative evidence the Court took the
  hold path instead.

## Probability construction

Branching from the SG's recommendation:

1. **Court holds for St. Mary (~0.92).** The docket already behaves like a hold,
   and the Court nearly always follows SG hold recommendations.
   - *St. Mary* ends favorably to the religious claimants (~0.85 — this Court
     has ruled for free-exercise claimants in essentially every merits case
     since 2012: *Fulton*, *Tandon*, *Kennedy*, *Carson*, *Groff*, *Catholic
     Charities* (9-0, 2025), *Mahmoud* (2025)). A decision tightening
     general-applicability doctrine against the Tenth Circuit's approach makes a
     **GVR of Renteria near-automatic** — same circuit, directly overlapping
     QPs, and GVRs do not require a clean vehicle, so the BIO's vehicle
     objections lose their force. P(GVR or plenary grant | favorable) ≈ 0.90
     (GVR heavily dominant; a small slice of outright grant if the Court wants
     the ACA-preemption QP4, which St. Mary will not resolve).
   - *St. Mary* affirms or resolves narrowly in the state's favor (~0.15):
     Renteria is then most likely denied; P(grant/GVR | unfavorable) ≈ 0.15.
   - P(grant | hold) ≈ 0.85×0.90 + 0.15×0.15 ≈ **0.79**.
2. **No hold — the Court acts independently (~0.08).** Given the CVSG lift and
   this Court's free-exercise appetite, P(grant) ≈ 0.35 against the vehicle
   problems the BIO presses.

P(any grant, GVR included) ≈ 0.92×0.79 + 0.08×0.35 ≈ **0.72**.

Modal disposition: **gvr** — vacate the Tenth Circuit's preliminary-injunction
affirmance and remand for reconsideration in light of *St. Mary* — likely in
summer 2027. `granted=1` per the contract (a GVR counts as a grant on the
binary axis).

Residual uncertainty keeping the probability from going higher: *St. Mary*
could be decided on the narrower *Carson*/status-use QP2 in a way that arguably
leaves the Tenth Circuit's Renteria reasoning intact; the interlocutory posture
plus the absence of merits fact-finding gives the Court a low-cost deny even
after a claimant win; and QP4 (preemption) — the question the CVSG most
plausibly targeted, since the free-exercise questions need no SG input — got a
hold recommendation rather than a grant recommendation, signaling the SG saw no
independently cert-worthy preemption issue.

## Votes

No per-judge votes predicted: cert-stage conference votes are unpublished, and a
GVR issues as an unsigned order.

## Big-case score

0.45 — the underlying stakes are real (the viability of ACA-recognized HCSMs
nationwide given the statute's continuous-operation quirk, plus the scope of
*Smith*), with a CVSG, an Alliance of Health Care Sharing Ministries amicus, and
trade-press coverage; but the doctrinal action will be in *St. Mary*, and this
case most likely resolves as an unsigned companion order.
