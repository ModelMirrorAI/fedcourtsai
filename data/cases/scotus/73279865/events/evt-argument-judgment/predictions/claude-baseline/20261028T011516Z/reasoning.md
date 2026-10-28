# Reasoning for my numbers — scotus/73279865, evt-argument-judgment (argued moment)

**Inputs read.** Snapshot `2026-10-06.json` (forward mode, cutoff 2026-10-06, date cut).
Provisioned documents: questions presented, petition, appendix (Eleventh Circuit opinion), BIO,
petitioner's and respondent's merits briefs (respondent's mainly its summary of argument),
petitioner's merits reply (not read in detail), and the full argument transcript of
2026-10-05. I checked `argument-features.json` against my own reading (coverage: 178 Justice turns, 177 attributed,
3/3 segments attributed, no unresolved labels). No United States amicus brief exists because the
United States, defending for Congress, is the respondent. No MCP, web, or corpus retrieval was
used.

**Anchor.** Grant date is 2026-04-06, so the grant Term is OT2025. The statpack merits section
publishes an `excluded` count, so it can be quoted. Pooled over grant Terms 2015–2024 (rows
present only for 2017–2024): 378 disturbed / 537 parsed = **70.4%**, well above the 30-judgment
floor. Coverage is near-complete for those Terms (parsed/granted e.g. 76/79 in 2024, 56/56 in
2023). That 0.704 is the bar.

**Adjustment from the argument (down to 0.64).** The argument leans toward petitioner in tone,
but the textual case clearly favors the government, so I end slightly *below* the base rate rather
than above it. A question from the bench is not a vote, and I read these as leans only:
- For petitioner: Gorsuch, strongly. He pressed the original meaning in 1988 and the government's
  reversal from its position in Pereida, and called the BVA-decides-constitutional-questions
  scheme a "rabbit hole". Sotomayor, strongly: government cannot appeal BVA, House report was about
  a different bill. Jackson, fairly clearly: she helped build petitioner's "under a law takes the
  law as given" reading and called the government's position "a big deal". Kavanaugh, moderately:
  "if it's a close call … why upset the longstanding practice?" and "what's the harm?". He had
  also suggested the Federal Circuit cured Robison's concern, though.
- For the government: Kagan said 511(a) "as it exists seems to me to favor the government" and
  read the House report. Late in the argument she also called it "very strange" for a Congress set on
  reversing Robison to do it this way, so she is not firmly committed. Alito opened hostile to
  petitioner's text, but asked the government a "damage-control" question about writing a
  narrow opinion for petitioner. His Elgin dissent favored district-court review of facial
  claims, so I count him as a lean toward petitioner on a narrow rule. Barrett stressed that
  petitioner "has a route", but also pressed the government on its claimed litigation burden.
- Roberts and Thomas said almost nothing on the merits (argument-features: Roberts 58 words, mostly
  presiding; Thomas 37), so I place them by priors.
On the count I lean 5–7 votes for petitioner, with real risk that the textual reading wins. That
is roughly a 0.6–0.7 chance of reversal, consistent with the base rate. I shade to 0.64 because the
government's textual argument (the 1988 rewording, 7292(c)) is strong and Kagan endorsed it.

**Votes and writers.** These have lower confidence than the binary. Thomas and Roberts are the
most uncertain placements. Majority-author spreads around the bench-share baseline, tilted to
Gorsuch for engagement and fit, and to Kavanaugh and Alito. I have no October-sitting assignment
data to condition on.

**Where to discount me.** I read the respondent's merits brief only for its summary of argument.
Argument tone at this Court is a noisy predictor, and Kagan's and Alito's positions are especially
hard to read. If the government wins, the judgment is "affirmed". The posture on remand
(sovereign immunity, the Eleventh Circuit's vacatur) makes "vacated" vs "reversed" a coin-flip
within the disturbed class.
