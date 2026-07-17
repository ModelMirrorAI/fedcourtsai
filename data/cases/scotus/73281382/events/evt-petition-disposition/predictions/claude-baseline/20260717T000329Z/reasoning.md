# Reel v. North Carolina, No. 25-1099 — cert disposition prediction

**Prediction: deny. P(grant, GVR included) = 0.07.**

## The legal question

The petition asks whether police conduct a Fourth Amendment search when they
enter the curtilage of a home to conduct a "knock-and-talk" with the purpose of
gathering incriminating evidence against the homeowner — i.e., how *Florida v.
Jardines*, 569 U.S. 1 (2013) (implied license limited by purpose) and *Collins
v. Virginia*, 584 U.S. 586 (2018) (physical intrusion on curtilage to gather
evidence is a search) govern the ubiquitous knock-and-talk technique. High Point
(NC) officers, acting on anonymous drug tips, cut through the petitioner's side
yard, stood behind an arriving guest as she knocked, held the storm door as she
entered, and — after the officer smelled marijuana when the door opened and the
petitioner shut it — kicked the door in and seized drugs. The trial court denied
suppression; a divided NC Court of Appeals affirmed (Judge Thompson dissenting,
calling the knock-and-talk a pretext to search the curtilage); the NC Supreme
Court affirmed per curiam without reasoning.

## Signals for grant

- **Call for response.** The State waived; after distribution for the 5/1/2026
  conference the Court requested a response (Apr 27, 2026), and later granted the
  State an extension. A CFR is the docket's strongest pre-conference interest
  signal — historically it lifts a paid petition's grant odds from the ~2–3%
  baseline into the high single digits.
- **Petition-stage amici.** Two briefs, from an ideologically diverse pair
  (America's Future/Gun Owners of America et al.; National Association for
  Public Defense/MACDL) — a modest salience boost.
- **Expressed interest in the area.** Justice Gorsuch's statement respecting
  denial in *Bovat v. Vermont*, 141 S. Ct. 22 (2020), joined by Justices
  Sotomayor and Kagan, flagged lower courts' failures to apply *Jardines* to
  knock-and-talks. The facts here (video-recorded piggybacking on a guest's
  entry, no knock by officers, forced entry within a minute) are vivid.
- **Divided lower court** with a substantial dissent; paid petition; competent
  counsel (Wake Forest appellate clinic + Nelson Mullins).

## Signals for denial

- **A serious preservation/vehicle problem.** The BIO documents (with record
  cites to the suppression transcript and both state appellate briefs) that
  petitioner never made the officer-purpose argument below — his state-court
  theory was scope-of-license (parking, side-yard path, standing behind the
  guest), not purpose. Under *Yee v. City of Escondido* the Court rarely takes
  questions not pressed or passed on below, and the only reasoned decision below
  is an intermediate state court that *did* cite and apply *Jardines*
  (distinguishing *Bovat*, where the state court ignored it).
- **No square split.** The petition frames lower-court "confusion," not a
  crisp conflict; the BIO plausibly recharacterizes most of the cited cases as
  fact-specific applications rather than doctrinal division.
- **Factbound.** The officer testified he came to knock and talk, and the trial
  court found no pretext as a factual matter; granting would look like
  error-correction on a disputed record. The trial court also rested
  alternatively on exigency (odor of marijuana, door barricading), a potential
  independent ground that muddies the vehicle.
- **Track record.** The Court has denied a string of knock-and-talk petitions
  posing adjacent questions — *Bovat* (2020, despite three justices writing),
  *Michigan v. Frederick* (2019), *Fairfield County v. Morgan* (2019),
  *Minnesota v. Chute* (2018), *Christensen v. Tennessee* (2018), *Brienza v.
  City of Peachtree* (2023). Three interested justices in *Bovat* is not four
  votes, and *Bovat* was a cleaner vehicle than this one.
- **No relist yet.** The case sits at first post-briefing distribution, for the
  9/28/2026 long conference; the strong pre-grant signal (repeated relists) has
  not had a chance to appear, and most long-conference petitions are denied.

## Calibration

From the committed statpack: modern discretionary-cert petitions resolve
granted at a low single-digit rate (Term 2024: 3.0%; Term 2025: 2.5%); relist
count 0 runs ~0.8% granted, and no CVSG is present here. This cell's positive
signals (CFR after waiver, dual amici, dissent below, paid case, live interest
from at least three justices in the doctrine) justify a substantial upward
adjustment from the anchor; the preservation defect, the factbound/alternative-
ground posture, and the Court's repeated denials of better-postured vehicles in
this exact space cap it well below coin-flip territory. A GVR is implausible —
there is no intervening decision to GVR against — so P(grant) is essentially
P(plenary grant). I land at **0.07**, with denial (plausibly accompanied by a
statement or dissent from denial) the modal outcome.

## Inputs used

Snapshot `record/snapshots/2026-07-16.json` (docket through the 7/1/2026
distribution); provisioned `questions-presented.txt`, `petition.txt` (35 pp.),
and `brief-in-opposition.txt` (57 pp., including suppression-hearing transcript
excerpts); `metrics/statpack.md` base rates. Corpus `fedcourts query` lookups
returned no matching priors (see `retrieval.md`). Mode: forward; no outcome
exists and none was retrieved.
