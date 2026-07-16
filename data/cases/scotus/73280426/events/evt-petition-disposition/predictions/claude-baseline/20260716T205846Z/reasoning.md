# Trevino v. Hobbs, No. 25-918 — petition disposition

**Prediction: GVR in light of *Louisiana v. Callais* — P(any grant, GVR included) = 0.65; likeliest label `gvr`.**

## The case

Petitioners Jose Trevino and Rep. Alex Ybarra are Yakima Valley Hispanic voters who
intervened (permissively) in *Soto Palmer v. Hobbs* to defend Washington's
commission-drawn Legislative District 15 against a VRA §2 vote-dilution claim and to
assert that any race-conscious remedy would itself be a racial gerrymander. The
district court (Judge Lasnik) found a §2 violation in 2023 and in 2024 adopted the
plaintiffs' remedial map, which cut LD-15's Hispanic CVAP from 52.6% to 50.2% and
redrew 13 of 49 districts. The State did not appeal. The Ninth Circuit (Aug. 27,
2025, 150 F.4th 1131) held the intervenors lacked standing to appeal the §2
liability ruling or to press their own §2 dilution claim, and that on the one claim
with standing (Trevino's equal-protection challenge to the remedial map) race did
not "predominate," so strict scrutiny did not apply.

The questions presented are (1) intervenor/candidate standing to challenge a
court-drawn remedial map and the underlying §2 liability determination, and
(2) whether a race-conscious remedial map must satisfy strict scrutiny.

## What drives the forecast

**The intervening decision.** *Louisiana v. Callais*, 146 S. Ct. 1131 (decided
April 29, 2026, 6–3), post-dates the Ninth Circuit's decision and reworked §2
vote-dilution doctrine — per contemporaneous coverage it requires challengers to
prove a race-based motive, holds that §2 as reconstrued did not require Louisiana's
second majority-minority district, and polices the use of §2 "racial garb" for
partisan ends. The §2 liability finding and race-conscious remedial map below were
produced under the pre-*Callais* Gingles framework; the petition's own footnote 2
anticipated a reverse-and-remand in light of *Callais*, and the reply (June 10)
post-dates the decision.

**The Court's revealed post-*Callais* practice.** In May 2026 the Court GVR'd
pending §2 redistricting petitions from Mississippi, North Dakota, and Alabama
(*Allen v. Caster*) "in light of Callais," over a Sotomayor/Kagan/Jackson dissent —
and commentators (e.g., a May 18 Volokh Conspiracy post) noted it was GVR-ing even
cases that arguably did not turn on *Callais* issues. This petition completed
briefing June 10, too late for the final June conferences, and was distributed
June 17 for the September 28, 2026 long conference — consistent with routine
scheduling, not with a decision to pass over it.

**The State respondents support GVR.** The State of Washington's June 2, 2026
response brief (StateBOR.pdf on the docket; reported June 2–3 under headlines like
"WA urges US Supreme Court to take redistricting case") asks the Court to grant,
vacate, and remand for the Ninth Circuit to apply *Callais*. A respondent state —
the party that administers the map — siding with review removes the usual
adversarial obstacle to a GVR. Only the Soto Palmer plaintiff-respondents
(Campaign Legal Center) oppose, arguing the standing holdings are independent of
*Callais*, the racial-gerrymander theory was forfeited, and the remedial map was
drawn without considering race.

**Docket signals.** Paid petition, Term 2025, elite election-law counsel (Holtzman
Vogel). Both respondent groups initially waived; the Court called for a response on
March 25, 2026 — a classic signal that at least one chamber is interested (CFR'd
paid petitions grant at several times the base rate). The Court denied the Rule 21
motion to expedite (May 26, 2026), which reads as unwillingness to disturb the map
before Washington's 2026 primary (a Purcell-flavored timing call), not as a merits
signal. Petitioners' post-*Callais* Rule 60(b) attempt below was denied (May 17
letter), leaving this Court as the only path to reconsideration.

## Base rates and adjustment

From the committed statpack (modern discretionary-cert slice): overall grant rate
~2.5–3% per Term; zero-relist petitions grant at 0.8%. This petition sits far from
the unconditional base rate: it is paid, CFR'd, fully briefed, in the Court's
highest-salience current subject area, with an on-point intervening landmark and a
respondent state affirmatively requesting GVR. The Court's demonstrated behavior in
May 2026 — near-categorical GVRs of pre-*Callais* §2 judgments — is the closest
reference class, and in that class the State's support makes this a stronger GVR
candidate than *Caster*.

The main deny-side scenario (~1/3 weight): the Court concludes the Ninth Circuit's
standing holdings are an adequate, *Callais*-independent basis for the judgment and
that the forfeited equal-protection claim makes a poor remand vehicle — the Soto
Palmer respondents' core argument. A plenary grant on QP1 (standing) is possible
but less likely: the Court decided candidate standing in *Bost* in January 2026,
petitioners allege no circuit split, and the posture (permissive intervenors with a
documented partisan motive, shifting positions) is a weak vehicle.

Rough decomposition: P(GVR) ≈ 0.53, P(plenary grant/grant-in-part) ≈ 0.12,
P(denial) ≈ 0.34, P(dismissed/other) ≈ 0.01 → P(any grant) ≈ 0.65,
modal label `gvr` (a GVR counts as a grant on the binary axis, so `granted = 1`).

## Votes

For the modal GVR outcome I project the *Caster* pattern: the six-Justice *Callais*
majority (Roberts, Thomas, Alito, Gorsuch, Kavanaugh, Barrett) supporting the GVR,
with Sotomayor, Kagan, and Jackson noting dissent (recorded as `denied`). Timing:
disposition likely on or shortly after the October 5, 2026 order list following the
September 28 long conference; a relist for the linked *Garcia v. Hobbs* petition
(No. 25-901) or for plenary consideration would not change the binary call.

## Leakage note

This is a forward cell: the petition is genuinely undecided (distributed for the
9/28/2026 conference). I did not search for — and there does not exist — any
disposition of this petition. The decisive external facts used (*Callais*'s
holding, the May 2026 GVR wave, and the State's GVR-supporting brief) all predate
the provisioned snapshot and are legitimate forward signal; a one-line note is in
`flags.json` per the contract's hygiene guidance.

## Inputs used

Provisioned: `record/snapshots/2026-07-16.json`, `questions-presented.txt`,
`petition.txt` (39 pp.), `brief-in-opposition.txt` (Soto Palmer respondents,
87 pp.), `documents.json`, `record/context.json` (mode `forward`),
`metrics/statpack.md`. Retrieval beyond these is itemized in `retrieval.md`.
