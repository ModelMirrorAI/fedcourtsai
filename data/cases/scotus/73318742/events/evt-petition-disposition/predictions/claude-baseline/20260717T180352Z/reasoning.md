# Wain v. Bunnell, No. 25-1271 — cert petition disposition

**Prediction: denied. P(grant, GVR included) = 0.004.**

## The case

Douglas and Elisa Wain, proceeding pro se, petition from the Sixth Circuit's
unpublished February 13, 2026 affirmance (No. 25-5722) of the dismissal of
their § 1983 suit against two Kentucky state judges — Judge Kimberly Bunnell,
who presided over the foreclosure case brought against them by Central Bank &
Trust, and Judge Jacqueline Caldwell of the Kentucky Court of Appeals. The
petition's three questions presented all reduce to one theory: that a judge who
is served with a § 1983 complaint naming her as a defendant acquires a
Caperton/Williams "significant personal stake" that (a) required her
disqualification and (b) strips or limits her absolute judicial immunity for
subsequent rulings against the § 1983 plaintiffs — here, a dispositive ruling
issued 72 hours after service. The petition also argues (Part I.F) that the
courts below skipped the Forrester v. White functional analysis for assertedly
administrative/ministerial components of the judges' conduct (non-disclosure of
a campaign-depository relationship with the plaintiff bank, docket-management
choices, motion processing).

## Why this petition is a near-certain denial

Anchoring on the provisioned questions presented, petition, and BIO, the
grant-side and deny-side considerations are lopsided:

1. **No circuit split — conceded.** The petition itself acknowledges it does
   not present "a traditional circuit split in the sense of directly
   conflicting holdings on identical facts" (Pet. 15), offering instead a
   "pattern of cursory application" theory without citing the cases that would
   establish the pattern. Rule 10 review without a split requires importance
   this vehicle does not carry.

2. **Severe preservation problem.** The BIO's lead argument is strong on its
   face: the § 1983 complaint was filed October 28, 2024, *before* the
   January 24, 2025 "three-day judgment," so the complaint could not and did
   not plead the post-service-conduct theory; the Wains never amended to add
   it; and neither the district court nor the Sixth Circuit was asked to decide
   whether service of a § 1983 complaint creates a disqualifying personal stake
   that defeats immunity. The Court is "a court of review, not of first view"
   (Cutter), and this Court almost never grants to decide a question first
   pressed in the petition.

3. **Adequate alternative grounds below.** The dismissal rested not only on
   judicial immunity but on the Eleventh Amendment (the judges were sued in
   their **official capacities only**), the inapplicability of Ex parte Young,
   and § 1983's own bar on injunctive relief against judicial officers absent a
   violated declaratory decree. Even if the Court were interested in the
   immunity question, the official-capacity pleading posture makes this a poor
   vehicle: reversal on immunity would not disturb the independent Eleventh
   Amendment holding. The motion to amend to add individual-capacity claims was
   denied as futile, adding a discretionary-review layer.

4. **Settled law points the other way.** Mireles and Stump hold immunity
   survives allegations of malice, corruption, and bad faith; Caperton and
   Williams are disqualification/vacatur doctrines whose own remedial logic
   (vacatur of the judgment, not damages against the judge) cuts against using
   them to carve back immunity. The Forrester argument is developed only in
   the petition, not below.

5. **Case profile.** Pro se petitioners (paid docket, but self-represented
   non-lawyers), an unpublished non-precedential decision below, a
   fact-intensive foreclosure grievance, no amicus support, ongoing parallel
   state proceedings held in abeyance, and a respondent BIO from a major firm
   raising threshold defects. This is the classic profile of a petition denied
   without comment at its first conference.

6. **Docket signals.** Docketed May 8, 2026; BIO filed June 8; distributed
   June 24 for the September 28, 2026 conference (the summer-list "long
   conference," which clears the term's accumulated petitions with a
   near-uniform wave of denials). No relist yet (none possible), no CVSG, no
   amici.

## Base rates and adjustment

From the committed statpack (live/historical slice, denial-reweighted):
modern discretionary-cert petitions resolve ~95% denied / ~3% granted / ~2%
dismissed overall; Term-2025 paid petitions grant at ~5.4% vs ~1.1% IFP;
petitions from the Sixth Circuit grant at ~3.5%; petitions never relisted grant
at ~0.8%; no-CVSG petitions grant at ~3.0%. (This statpack build carries no
salience-band table, so I anchored on the disposition/relist/CVSG/circuit cuts.)

The paid-docket anchor (~5%) is the wrong prior for this petition: the paid
class's grant rate is driven by counseled petitions presenting genuine splits,
often with amici. Every observable discriminating signal here — pro se,
conceded no-split, preservation defect, independent alternative grounds,
unpublished below, no amici, long-conference distribution — sits in the deniest
tail of the paid class. The 0-relist bucket (~0.8% grant) is the closest
observable cut, and this petition is weaker than that bucket's average because
of the vehicle defects. A GVR is essentially impossible (no intervening
decision in sight; no mootness event). I set P(grant incl. GVR) = 0.004, with
the residual mass on denial (dismissal is possible but rare and there is no
sign of settlement or withdrawal).

**Predicted disposition: denied**, most likely without recorded dissent on the
Order List following the September 28, 2026 conference.

## Big-case score

0.07. If the Court somehow took it, an immunity-limiting holding would matter
doctrinally, but the case as filed is an obscure pro se foreclosure dispute
with no public profile; the score reflects stakes, not the (already low) odds.

## Inputs used

- Provisioned snapshot `record/snapshots/2026-07-17.json` (docket 25-1271:
  filing, BIO, and distribution entries; paid case type; Term 2025).
- Provisioned `record/documents/questions-presented.txt`, `petition.txt`
  (50 pp., full), and `brief-in-opposition.txt` (23 pp., full) — the QPs
  anchored the analysis; the petition was weighed against the BIO's
  preservation and Rule 10 arguments as described above.
- Committed `metrics/statpack.md` + `metrics/statpack.json` (per-fee-class
  detail) for base rates; one `fedcourts query` priors pull (see
  `retrieval.md`).

Mode is `forward`; the case is genuinely pending (conference date is in the
future), so no leakage is possible and no outcome was sought or seen.
