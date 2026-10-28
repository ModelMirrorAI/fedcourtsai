# Rationale for P(disturbed) = 0.87, judgment `reversed`

**Inputs used.** Snapshot `record/snapshots/2026-10-08.json` (granted Mar 9 2026;
argued Oct 7 2026); `record/documents/`: the argument transcript (read in full),
the petition (lower-court holdings and VanDyke dissent), questions presented, and
skims of the merits briefs; `record/argument-features.json` (coverage: 204 Justice
turns, 203 attributed, 3 of 3 segments attributed). Mode is `forward`; I did no
retrieval beyond the provisioned inputs and the committed statpack. I do not know
the outcome — the case was argued after my training data ends.

**Anchor.** Grant Term is OT2025 (grant order Mar 9 2026). The statpack merits
section (which publishes an `excluded` count, so it is quotable) shows grant
Terms 2017–2024 among the ten preceding Terms (2015–2016 carry no parsed rows).
Pooled: 378 disturbed / 537 parsed = **70.4%**, well above the 30-judgment floor;
coverage in those Terms is near-complete (e.g. 2024: 76 parsed of 79 granted).

**Adjustments upward.**
- The Solicitor General is the petitioner, and the Court granted a government
  petition from a divided Ninth Circuit panel with a vigorous dissent — a
  profile that reverses well above the base rate.
- Argument: the finality question went badly for respondent. Thomas pressed
  twice for any example of a regulated party's application being final agency
  action, and counsel conceded none came to mind in the Court's cases. Jackson
  articulated the government's best point herself (the application is a
  proposal the regulator can rewrite, so its terms are unknown). Barrett's
  questions noted that the intuitive final action is Guam EPA's decision and
  that NEPA challenges often come at the back end. Gorsuch elicited that the
  Air Force cannot proceed without Guam's permit. Kagan was the government's
  sharpest questioner on line-drawing but then suggested waiting for the permit
  made better sense. Roberts and Kavanaugh's concern ("never reviewable") was
  partly met by the government's rebuttal (an order to carry out operations
  after a permit would be final).
- argument-features.json is consistent with this: petitioner's counsel drew
  136 Justice turns vs 67 for respondent, but counts are not votes; Sotomayor's
  heavy questioning of petitioner (30 turns) matches her evident skepticism.

**Adjustments downward / uncertainty.**
- Sotomayor clearly favored respondent; Kagan's and Jackson's ultimate votes are
  uncertain; Gorsuch and Jackson were hostile to the government on QP2. If a
  majority found finality on a pragmatic theory, it would then face QP2 where the
  government looked weak — that path leads to affirmance.
- Possible procedural off-ramps (vacatur for a narrower jurisdictional point)
  still count as disturbed, so they do not lower the number.
Net: 0.87.

**Votes.** Per-Justice section, Terms strictly before OT2025 (OT2020–OT2024):
all Justices vote with the judgment ~70–96% of the time and to disturb ~55–77%;
I depart from those rates on the argument's evidence, placing only Sotomayor in
dissent. Vote block banks unscored.

**Authors.** No assignment information for the October sitting is in my inputs;
the distribution reflects who engaged most with the eventual rationale, shrunk
toward an even spread.

**Where to discount me.** Reading a bench's questions as leans is noisy,
especially for Kagan and Jackson, who probed both sides.
