# Rationale — P(disturbed) = 0.88, judgment `reversed`

**Inputs used.** I read the snapshot `record/snapshots/2026-10-22.json` (date cut at 2026-10-22, forward mode) and the staged documents: the questions presented, the petition, the BIO, the cert reply, the petitioners' merits brief (Aug 28, 2026), the respondents' corrected merits brief (filed Oct 21, 2026), and the United States' merits amicus brief (Sept 4, 2026). I also read the related docket snapshot `record/related/25-566.json`. No argument transcript exists at this moment: argument is set for Dec 2, 2026. I did not retrieve anything about later events.

**Anchor.** I used the statpack merits section, which publishes an `excluded` column. The grant order is dated Jun 30, 2026, so the grant Term is OT2025. The pool is the ten grant Terms OT2015–OT2024. The table shows OT2017–OT2024; OT2015 and OT2016 have no parsed judgments and do not appear. Pooled disturbed/parsed = 375/533 ≈ **70.4%**, well above the 30-judgment floor. Coverage in those Terms is high (for example OT2024: 76 parsed of 79 granted).

**Adjustments upward, to 0.88.**
- *Relist history.* The petition was distributed for 22 conferences before the grant. That pattern fits a Court waiting for the right vehicle on an issue the conservative majority wanted to take. Kavanaugh's statement in *Snope v. Brown* (2025) said the Court should take up AR-15 bans "in the next Term or two." Petitioners and the United States both cite it.
- *The United States supports reversal.* The SG's amicus brief backs petitioners on the common-use test and asked for divided argument.
- *Recent doctrine.* Both sides cite *Wolford v. Lopez*, 146 S. Ct. 2032 (2026), including a Barrett concurrence that criticizes limiting "Arms" at the textual step. That undercuts the Seventh Circuit's *Bevis* reasoning, which is the ground of the judgment here.
- *Weak defense.* Cook County's brief defends the ban mainly through an "exceptionally dangerous weapons" tradition (launcegays, trap guns, Bowie knives) and attacks the common-use evidence. That is the theory the Kavanaugh, Thomas and Alito separate writings have already rejected.

**Why not higher.** Roberts and Barrett have not committed on AR-15 bans specifically. A narrower majority is possible: for example, a holding that the rifles are "Arms," with a vacatur and remand for the history step. That outcome would still count as disturbed, so it barely affects the number. The real downside cases are an affirmance (a majority accepting the dangerousness tradition) and a DIG. I put both together at about 12%. A DIG is especially unlikely after 22 relists and a consolidation.

**Judgment label.** Petitioners ask for reversal with instructions to enter judgment. The Seventh Circuit decided a final judgment on the pleadings. I chose `reversed` over `vacated`, but a vacate-and-remand for the Seventh Circuit to apply the standard is a real alternative (~25% of the disturbed mass).

**Votes.** The per-Justice disturb rates for OT2020–OT2024 (Terms before the grant Term) run roughly 54–77% for every Justice. They are generic and do not separate Justices on this issue, so the lineup rests on the Justices' Second Amendment records: *Bruen* and *Rahimi*, and the *Snope* and *Harrel* separate writings. I used the per-Justice votes table only as a sanity check.

**Authorship.** The author distribution is spread across the majority, with Kavanaugh and Thomas modestly ahead. I am not reading sitting assignments, since the December sitting has not happened. I do not know who wrote *Wolford*, so I did not use it to discount any Justice.

**Uncertainty and discounts.** I recognize this case from general knowledge of the post-*Bruen* AR-15 litigation. I have no knowledge of its outcome, and my training data predates the grant. The corpus query gave no topical priors (see `retrieval.md`).
