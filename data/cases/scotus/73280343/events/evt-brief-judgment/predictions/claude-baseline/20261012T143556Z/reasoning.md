# Why P(disturbed) = 0.42

**Inputs read:**

- the snapshot `2026-10-03.json` (granted June 29, 2026; argument November 30, 2026;
  three amicus briefs for petitioners, all from immigration-advocacy or academic
  sources)
- `questions-presented.txt`
- the petition
- the SG's brief in opposition, which says the decision below is correct but
  **acquiesces** in cert because of the 2d/4th vs. 5th Circuit split, and calls this a
  suitable vehicle
- both merits briefs: petitioners' (Aug 24) and the SG's respondent brief (Oct 2)
- the cert reply, which is `empty_text: true`. I could not read it and inferred
  nothing from it.

I read only each merits brief's summary of argument and skimmed the BIO's discussion.
I did not read the full argument sections, and I did not read the appendix, which
holds the Second Circuit opinion with Judge Robinson's dissent.

**Anchor.** The statpack's merits section publishes an `excluded` count, so its rate
is quotable. Grant date June 29, 2026 puts this in grant Term OT2025. The ten-Term
window is OT2015–2024, but rows exist only for 2017–2024. Pooled, that is 360
disturbed of 516 parsed, or **69.8%**. Coverage is close to full in those Terms:
parsed is 52–75 per Term against 55–79 granted. The pool clears the 30-judgment
floor. This rate is the bar I am scored against.

**Adjustments down from 70%:**

1. **Government-acquiescence split grants.** The petitioner lost below, and the SG
   defends the judgment while agreeing to review. The usual reversal premium comes
   partly from the Court picking cases it wants to fix. When the Court grants
   because the SG says "we're right, but resolve the split," that selection signal
   is much weaker, and these cases run closer to a coin flip.
2. **Two circuits for the government, one against.** The lone contrary circuit is
   *Siwe*, decided without the government briefing the statutory question and
   before the BIA's *T-C-A-*. The two circuits ruling for the government, including
   the Second Circuit here, faced the full arguments.
3. **The 1990 note is the strongest single textual point in either brief.** Congress
   expressly let certain former asylees adjust "regardless of whether or not such
   asylum has been terminated." That is natural negative-implication material for
   this Court. The 1158(c)(1) parallel use of "alien granted asylum" also helps the
   government.
4. **This Court's record in contested INA statutory cases is mixed.** Pugin and Patel
   went to the government; Niz-Chavez, Santos-Zacaria and Wilkinson to the noncitizen.
   Textualist cross-over (Gorsuch, sometimes Barrett) is real. Petitioners' structural
   point about express continuing conditions in 1159(a) and (b)(3) is genuinely
   strong, and a Second Circuit judge dissented.

**Net.** Roughly 0.40–0.45, and I settled on 0.42. That sits below the 69.8% anchor,
so I am betting against the base rate. If the acquiescence-grant discount is wrong,
I lose Brier score relative to it.

**Votes.** The vote lineup is my weakest component. Gorsuch's and Barrett's votes are
near-coin-flips, and I put Gorsuch in dissent because of his immigration-lenity
writings.

**Retrieval.** None beyond the provisioned inputs and the committed statpack. The
argument has not happened yet, so no transcript exists. I did not know this case's
outcome from training, and it is undecided as of the snapshot.
