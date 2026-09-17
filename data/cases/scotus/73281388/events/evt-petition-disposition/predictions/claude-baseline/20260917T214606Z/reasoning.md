# Why P(grant) = 0.14, and the rest of the numbers

## Inputs actually used

- Snapshot `record/snapshots/2026-09-17.json` (as-stored, forward mode, no
  cutoff): 19 docket entries, paid docket 25-1105, First Circuit (No. 25-1007,
  published at 159 F.4th 91, decided Nov. 18, 2025), linked extension
  application 25A734.
- `record/context.json`: `band: elevated` under `sal-v4`, `distribution_count:
  2`, `cvsg_date: null`, `term: 2025`, `signals_observable: true`.
- `record/documents/`: `questions-presented.txt`, `petition.txt` (45 pp.) and
  `brief-in-opposition.txt` (32 pp.), all with `empty_text: false`, read in
  full.
- Retrieved beyond the provisioned set (forward mode, unrestricted): the
  petitioner's July 20 reply and September 9 supplemental brief from the
  supremecourt.gov links the snapshot carries; one CourtListener search
  confirming *Chatrie v. United States* (No. 25-112) was decided June 29, 2026;
  one `fedcourts query` for recent granted SCOTUS priors. Details in
  `retrieval.md`.
- `metrics/statpack.md`, the cert sections and the `sal-v4` segment table.

## Anchor

The scored yardstick for a frozen `elevated` band is the bracketed `reached`
rate pooled over Terms strictly before OT2025. The table shows OT2017–OT2024:

| Term | reached rate | n |
| --- | --- | --- |
| 2024 | 17.9% | 336 |
| 2023 | 17.5% | 354 |
| 2022 | 19.0% | 300 |
| 2021 | 20.5% | 342 |
| 2020 | 16.1% | 397 |
| 2019 | 13.8% | 334 |
| 2018 | 15.9% | 347 |
| 2017 | 17.5% | 400 |

Pooled: about 484 grants over 2,810 weighted petitions, **≈17.2%**. The table's
version stamp (`sal-v4`) matches the context's `salience_version`, so this is the
right table. For shape only, the relist-count cut puts 1-relist paid petitions at
8.2% granted plus 5.1% GVR, and the CVSG cut's `none` row at 4.0% + 2.3%.

## Adjustments from the anchor

**One caution about the band itself.** The `dist-v2` count of 2 here is not a
true relist. The June 11 distribution was superseded by the June 3 call for a
response, so the petition has never been considered at conference; September 28
is its first look. The `elevated` population mixes genuine post-conference
relists (a strong signal) with call-for-response redistributions like this one.
I treat the call for a response as roughly comparable evidence of a chambers'
interest, which keeps me near the anchor rather than well below it, but it is
the main reason I do not go above it.

**Upward.**
- The Court called for a response after the State waived. That is an
  affirmative act by at least one chambers, and it is what put this petition in
  the band.
- Experienced cert-stage counsel (Pacific Legal Foundation) and four surviving
  amicus briefs from repeat cert-stage filers.
- The legal question is purely legal on a motion-to-dismiss record, the search
  was conceded, the court of appeals opinion is published, and the district
  court itself called the Fourth Amendment issue significant and invited appeal.
- Recurrence is real: every ASMFC lobster state has adopted or must adopt the
  same rule, and the Fifth Circuit's *Mexican Gulf Fishing* (APA, with Fourth
  Amendment misgivings) shows appellate discomfort with GPS tracking of vessels.
- The originalist, property-based framing is aimed squarely at Justices Gorsuch
  and Thomas, and the surveillance theme has drawn Justice Sotomayor before.

**Downward.**
- Preservation. The BIO's central point is that the word "trespass" appears
  nowhere in the First Circuit briefs and that the panel never cited *Jones*. The
  reply answers that *Jones* and *Carpenter* were argued as general Fourth
  Amendment principles and that the panel rejected them in footnote 18. That is
  enough to say the issue was "passed upon" in a loose sense, but the specific
  "trespass test for reasonableness" the questions presented ask about is a
  cert-stage reframing. The Court is sensitive to that.
- The split is thin. *Rush* (9th Cir. 1985) predates *Burger* and turned on
  overbreadth of home day-care inspections; *Taylor II* (6th Cir. 2021) held
  that municipal parking is not a closely regulated industry and expressly
  declined to reach the trespass-versus-privacy methodology point; *Patel I* and
  the other Ninth Circuit cases discuss *Jones* and *Katz* at step one (whether
  a search occurred). *Johnson v. Smith* (10th Cir. 2024) is a routine
  statement that *Burger* governs once a search in a closely regulated industry
  is found. The BIO's account of these cases reads accurately against the
  petition's own descriptions. The supplemental brief's *Richards v. Newsom*
  (9th Cir. Aug. 27, 2026) upheld 24/7 surveillance of gun dealers under
  *Burger*, so it is in tension with the petition's theory rather than a new
  conflicting holding; its value is as evidence of judicial disagreement
  (a dissent), not as a split.
- The petitioner conceded below that lobstering is closely regulated, so the
  *Patel*-style question of the exception's scope is not presented. The
  interesting vehicle here would be one where that is contested.
- Maritime context: vessels have always been subject to suspicionless boarding
  (*Villamonte-Marquez*), which gives the Court an easy reason to see this as a
  fact-specific application rather than a doctrinal fault line.
- State respondent defending a conservation rule adopted under an interstate
  compact with federal backing; the Court rarely takes a private petitioner's
  challenge to a state fisheries rule absent a clean split.

Net: I come out a little under the anchor, at **0.14**. The affirmative
interest signal (call for response) and counsel quality roughly offset the
preservation and split problems relative to the typical `elevated` petition; the
concession and maritime posture push down.

## The other claims

- **relist-increment 0.30.** From a first-conference state. Most of the mass is
  P(grant) times the near-certainty of a pre-grant relist, plus a denial-side
  relist for a statement or dissent, plus ordinary long-conference carryover.
- **cvsg-increment 0.06.** CVSGs are about 1.2% of the paid scored segment.
  This case has a plausible federal interest (ASMFC mandate, NMFS monitoring,
  the SG's stake in administrative inspection doctrine generally), which lifts
  it, but the Court already chose the call-for-response step and the respondent
  is a State. I do not see a strong CVSG candidate.
- **summary-disposition-route 0.05** (conditional on grant). No intervening
  decision on point; *Chatrie* (decided June 29, 2026) is a criminal geofence
  warrant case. A published, reasoned panel opinion on a novel framing is not a
  per curiam target.
- **dissent-from-denial 0.15** (conditional on denial). Above the typical paid
  petition because a chambers already showed interest and the petition's theory
  fits Justice Gorsuch's Fourth Amendment writings; below a coin flip because
  the preservation and concession problems give an interested Justice a reason
  to let it go quietly.
- **big_case_score 0.55.** Stakes if decided are doctrinally broad (every
  "closely regulated" industry, continuous electronic monitoring under
  *Burger*), but the subject is niche and the immediate reach is one fishery.

## Where to discount me

- I did not read the First Circuit opinion itself, only the parties' accounts
  of it; the preservation dispute turns on what the panel said at App. 14a–19a
  and 28a n.18, and I am weighing the BIO's and the reply's characterizations
  against each other.
- I did not read the amicus briefs or the *Richards v. Newsom* opinion; the
  supplemental brief's description of *Richards* is the petitioner's.
- My read that a call-for-response redistribution is roughly as informative as
  a true relist is a judgment, not a measured rate; the statpack does not cut
  the `elevated` band by how its second distribution arose. If
  call-for-response petitions grant at materially lower rates than true
  relists, 0.14 is too high; if at higher, too low.
- I did not consult the earlier predictions on this docket from the July 17
  run, by design.
