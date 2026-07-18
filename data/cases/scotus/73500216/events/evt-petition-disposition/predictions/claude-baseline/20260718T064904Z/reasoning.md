# Pearson v. Guerrero, No. 25-1316 — cert petition disposition

**Prediction: denied. P(grant, GVR included) = 0.03.**

## The case

Donnie Ray Pearson, a Texas state prisoner serving life without parole for
super-aggravated sexual assault of a child, petitions from the Fifth Circuit's
unpublished January 28, 2026 affirmance (2026 WL 228764, No. 24-20112) of the
denial of federal habeas relief under 28 U.S.C. § 2254. After voir dire but
before strikes, Juror 27 passed a note saying she had been molested as a child
but "th[ought]" she could be fair; no one questioned or struck her and she
served. Trial counsel later swore he never heard the note read and would have
challenged or struck her had he heard it. The claim reaches the Court as
ineffective assistance of counsel, with prejudice turning on whether the juror
was *impliedly* biased.

The question presented: whether a juror who was the victim of the same type of
crime as the charged offense is impliedly biased where she does not
unequivocally state she can be fair (petition, `questions-presented.txt`).

## Why the alleged split is real but has not moved the Court

The petition documents a genuine, long-standing disagreement over how to apply
Justice O'Connor's *Smith v. Phillips* concurrence (455 U.S. 209, 222 (1982))
to same-crime-victim jurors: the Third, Seventh, Ninth, Tenth, and D.C.
Circuits have found implied bias on close facts; the First, Sixth, and Eighth
have rejected it; the Fifth is internally inconsistent (*Solis v. Cockrell* vs.
*United States v. Buckner*). That is a colorable Rule 10(c) presentation, and
the petition is competently drafted.

But the split is 40+ years old, rests on a concurrence rather than a holding,
and the Court has let it sit through many prior petitions — the petition itself
concedes the Court "has not revisited the implied bias doctrine since *Smith*
… in 1982." A split the Court has tolerated for decades, framed at this level
of fact-specificity ("extreme circumstances"), is weak grant fuel without a
strong vehicle.

## Vehicle problems (decisive here)

1. **AEDPA posture.** Relief requires that the state court unreasonably applied
   *clearly established* Federal law as determined by this Court's *holdings*
   (§ 2254(d)(1)). The implied-bias doctrine's modern footing is an O'Connor
   *concurrence*; the *Smith* majority never adopted it (the Sixth Circuit has
   squarely questioned the doctrine's viability for exactly this reason, as the
   petition's own footnote 3 notes). The Court cannot cleanly announce a
   uniform implied-bias test in a case where the dispositive question is
   whether existing law was *clearly established* — the ideal vehicle for this
   QP is a federal direct appeal, not state-prisoner habeas.
2. **Double deference.** The implied-bias question arrives nested inside
   *Strickland* prejudice, itself reviewed through § 2254(d). Layers of
   deference between the QP and the judgment make this a poor vehicle even for
   Justices interested in the doctrine.
3. **Weak facts under even the favorable circuits.** The petitioner-friendly
   cases (Dyer, Burton, Gonzalez, De Vita) involve concealment or lies. Juror
   27 *voluntarily disclosed* her history and affirmed (equivocally) that she
   thought she could be fair. The petition must distinguish its own best
   authority, and the Fifth Circuit's "not extreme" holding is defensible under
   any circuit's test — reducing both the certworthiness and any summary-
   reversal appeal.
4. **Unpublished, non-precedential decision below**, which the Court rarely
   reviews absent a strong signal.

## Docket signals (snapshot 2026-07-18)

- Paid, counseled petition (solo Houston practitioner — not a repeat SCOTUS
  practice), docketed May 28, 2026, Term 2025, non-capital.
- Response was due June 29, 2026; the docket shows no brief in opposition and
  no record of the Court calling for a response. Distribution on July 15 for
  the September 28, 2026 long conference is consistent with a state waiver.
  The Court essentially never grants without first calling for a response, so
  even in an optimistic branch the near-term path is CFR → relist → grant —
  a low-probability chain with no first step yet visible.
- No amici, no CVSG, zero relists (first distribution, long conference — where
  the overwhelming majority of petitions are denied).

## Base rates and adjustment

From `metrics/statpack.md` (live/historical slice, denial-reweighted): Term
2025 grant rate 2.5%; CA5-originating modern cert petitions grant 4.8%;
relist-0 petitions grant 0.8%; no-CVSG petitions grant 3.0%. The statpack in
this repo carries no salience-band table, so I anchored on these cuts. Within
the salience-selected pool this cell was drawn from (2020s ingested slice
grants ≈ 17%), this petition sits far below the pool average: the granted
priors returned by `fedcourts query` (see `retrieval.md`) are dominated by
elite counsel, amici blocs, CVSGs, and multi-relist dockets — none of which
this case has.

Starting from the ~3–5% paid/CA5 prior, the AEDPA vehicle defects, weak facts
relative to the split's favorable cases, the unpublished decision below, the
absence of any called-for response, and the Court's demonstrated tolerance of
this split push downward; the genuine split allegation and competent counseled
presentation push modestly upward. A GVR path is essentially absent (no
pending related merits case on implied bias). I land at **P(grant) = 0.03**,
predicted disposition **denied** — most likely after the long conference or a
short relist.

## Big-case score

0.25 — a decided case announcing a uniform implied-bias standard would matter
across criminal trials nationwide, but the question is technical criminal
procedure with no public salience, prominent parties, or amicus interest.
