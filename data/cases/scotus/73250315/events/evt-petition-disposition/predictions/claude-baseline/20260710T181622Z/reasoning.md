# Nformangum v. United States, No. 25-7259 — cert disposition

**Prediction: denied. P(granted) = 0.13.**

## The event

Petition for a writ of certiorari (IFP, but counseled) from the Fifth Circuit's
unpublished decision in *United States v. Nformangum*, 2026 WL 18900 (5th Cir.
Jan. 2, 2026). Forward-mode cell: the petition is genuinely pending, with the
government's response now due August 7, 2026.

## The legal question

The question presented: whether an indictment's failure to allege an essential
element of the offense is **structural error requiring automatic reversal**, or
is instead subject to **harmless-error review**. This is a real and
long-standing circuit split. The Fourth Circuit (*Spruill*) and Ninth Circuit
(*Du Bo*, reaffirmed in *Qazi*) treat a preserved challenge to an
element-omitting indictment as structural; the First, Second, Third, Fifth,
Sixth, Seventh, Eighth, and Eleventh Circuits apply harmless-error review. The
Court granted certiorari on this exact question in *United States v.
Resendiz-Ponce*, 549 U.S. 102 (2007), but resolved the case by finding the
indictment sufficient; only Justice Scalia reached the question, in dissent,
and would have held the error structural.

## Facts from the snapshot and provisioned documents that drive the outcome

- Petitioner was convicted under 18 U.S.C. § 875(c) (threatening voicemail to
  Senator Cruz's office) after a stipulated-evidence bench trial; sentence was
  one year of probation. The indictment did not allege the subjective mens rea
  a true-threats prosecution requires.
- The claim is **cleanly preserved**: a pretrial motion to dismiss the count
  was denied, and the Fifth Circuit **expressly held the indictment "failed to
  state an offense"** yet affirmed after asking what a "rational grand jury"
  would have done with the evidence "available" to it. The split is therefore
  outcome-determinative: in the Fourth or Ninth Circuit this preserved defect
  would have required reversal. That makes this an unusually square vehicle,
  and the petition frames the harmless-error inquiry as exactly the
  "subsequent guess" *Russell v. United States*, 369 U.S. 749, 770 (1962),
  forbids.
- **Docket signals (the most probative part of the snapshot):** the Solicitor
  General initially *waived* response (May 21). The petition was distributed
  for the June 11, 2026 conference — and on **June 8 the Court called for a
  response** (CFR). The SG then sought and received an extension to August 7,
  2026. A CFR issued out of conference after a waiver means at least one
  chambers found the petition worth a closer look; it is the strongest
  pre-BIO grant signal a docket can show.
- No brief in opposition exists yet (waiver, then extension), so this
  prediction necessarily weighs the petition without a BIO. `documents.json`
  confirms only the petition and its questions-presented section were
  provisioned.

## Weighing

**Toward grant:** an acknowledged, recurring, two-decade split the Court once
granted on and left unresolved; clean preservation; a court of appeals
concession that the indictment failed to state an offense; and a CFR.
Empirically, a call for response lifts a petition's grant probability from the
sub-2% modern discretionary-cert baseline into roughly the 5–15% range, and
counseled petitions presenting genuine splits sit at the top of that range.

**Toward denial:** the base rate is unforgiving — the corpus statpack shows
granted at 1.4% of resolved SCOTUS petitions (and the modern discretionary
grant rate is a few percent at best); corpus retrieval of similar modern SCOTUS
priors returned seven denials against one grant. The Court has tolerated this
split since 2007 and has denied repeated petitions raising it. The vehicle has
real wrinkles the SG will press: the trial was on stipulated facts in which
petitioner admitted leaving the voicemail and described his own conduct as
"reckless," so the omitted mens rea element was effectively conceded — making
harmlessness vivid and the equities unsympathetic; the decision below is
unpublished; the one-year probation sentence has likely expired, lowering the
practical stakes (though collateral consequences keep the case live); and the
government can argue the split is narrower than pleaded because several
harmless-error circuits ruled in plain-error postures rather than on preserved
challenges.

**Net:** the CFR moves this petition well above the baseline, but most CFR'd
petitions are still denied, and this Court has repeatedly declined this
particular invitation. I put P(granted) at **0.13** and predict **denied**,
with moderate confidence (0.6). If denial comes, expect it at or shortly after
the late-September 2026 long conference; a relist would be the signal to
revise upward.

## Retrieval caveats

The cell's configured CourtListener MCP server never became available
(tool search surfaced no CourtListener tools), so retrieval was limited to the
corpus CLI, the committed statpack, and one web search confirming the petition
is pending — a degraded but non-blocking upstream, per the contract. The
committed `metrics/statpack.md` also lacks the "Modern discretionary-cert
petitions by disposition" section the predict prompt anchors on; I fell back
to the overall SCOTUS resolved rates plus general knowledge of the modern cert
grant rate. Both are flagged in `flags.json`. I do not know this case's
outcome — none exists; it is pending.
