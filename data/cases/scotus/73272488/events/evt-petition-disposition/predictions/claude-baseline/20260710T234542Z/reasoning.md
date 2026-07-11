# Abrams v. United States, No. 25-1236 — cert disposition

**Prediction: granted, P(granted) = 0.55.**

## The legal question

The petition presents a single, pure question of federal criminal procedure:
whether a defendant's *general* motion for judgment of acquittal under Fed. R.
Crim. P. 29 preserves de novo appellate review of evidence-sufficiency
challenges, or whether the defendant must articulate each specific deficiency
to avoid plain-error review. Below, the Third Circuit (165 F.4th 784, Smith,
J., joined by Bibas and Scirica) expressly "decline[d] to follow" the "well
accepted" majority rule of seven circuits (1st, 2d, 6th, 7th, 9th, 10th, DC)
and joined the minority camp (8th, 11th, and as a practical matter the 5th),
holding petitioner's motion — "I move for judgment of acquittal on Rule 29(a).
I waive argument." — preserved nothing, and affirming his 48-count fraud
conviction under plain-error review.

## The governing standard

Cert is discretionary (Sup. Ct. R. 10); the dominant grant driver is a mature,
outcome-determinative circuit split on a recurring federal question in a clean
vehicle. Base rates are brutal: the corpus statpack's overall SCOTUS resolved
mix shows granted ≈ 1.4%, and per the task prompt the modern discretionary-cert
grant rate is a few percent. Any grant prediction therefore has to be carried
by strong case-specific signals. This docket has an unusual accumulation of
them.

## Facts from the snapshot and provisioned documents that drive the outcome

1. **A mature, acknowledged, outcome-determinative split.** Eleven circuits
   have weighed in, 7–4. The decision below is precedential, squarely reasoned,
   and openly breaks with the majority — the strongest split posture a petition
   can have. The competing rules also interact perversely (in majority circuits
   a *specific* motion waives unstated grounds; in minority circuits a *general*
   motion forfeits everything), so identical trial conduct produces opposite
   preservation results in adjacent districts. Percolation is complete.
2. **The government itself has flagged the question as cert-worthy.** In its
   Third Circuit brief the government called this appeal "an opportunity for
   the Court to resolve th[is] open question," and in its April 7, 2026 brief
   in *Tovar v. United States*, No. 25-6344 (a pending petition on the same
   question), the SG acknowledged the circuit split and suggested the Court
   could resolve it "with the appropriate vehicle" while identifying vehicle
   problems in *Tovar*. Abrams is expressly pitched as that vehicle. A
   respondent-side acknowledgment of a real split is one of the strongest
   grant predictors there is.
3. **The Court called for a response.** The United States waived (May 21);
   the petition was distributed for the June 18 conference; on June 9 the
   Court requested a response (a CFR), and the SG then obtained an extension
   to August 10. A CFR after waiver means at least one chambers is actively
   interested — empirically it lifts grant odds by roughly an order of
   magnitude over the paid-petition baseline.
4. **Petition-stage amicus support.** NACDL and a group of Former Judges filed
   amicus briefs on June 1 — another well-documented grant correlate for paid
   petitions.
5. **Vehicle quality.** The record is undisputed (the Rule 29 colloquy is
   quoted verbatim), the question was pressed by the government, fully
   briefed, decided as a threshold holding, and was the basis for applying
   plain-error review. Elite counsel (Debevoise; David O'Neil as counsel of
   record) on a paid petition.

## Countervailing considerations (why not higher)

- **The BIO is unwritten.** The SG's response (due Aug. 10) may argue the
  evidence was sufficient under *any* standard — plausible here, since the
  trial record (forged teaming agreements, fabricated tax returns, doctored
  Navy contracts) looks overwhelming — making the standard-of-review question
  arguably immaterial to the judgment. That is the classic vehicle attack on
  preservation/standard-of-review petitions, though the Court granted through
  a similar posture in *Holguin-Hernandez v. United States* (2020).
- **Rules-committee alternative.** The Court sometimes leaves splits over the
  Federal Rules to the Rules Enabling Act process rather than certiorari.
- **Base rate discipline.** Even CFR'd, amicus-supported paid petitions are
  denied more often than not in the aggregate; the Court takes ~60–70 cases a
  Term.
- **Small alternative paths:** the Court could instead grant *Tovar* (unlikely
  given the SG's stated vehicle concerns there) or GVR/hold this petition.

## Probability

Chaining the uplifts: a few-percent paid baseline → ~10% with a CFR →
substantially higher with an entrenched 7–4 split the government concedes,
petition-stage amici, and a self-consciously clean vehicle. Conditional on the
SG acquiescing or only nominally opposing (which its *Tovar* brief makes
plausible), a grant is very likely; conditional on a full-throated
sufficiency-either-way opposition, the odds fall to perhaps a third. Weighing
those branches roughly evenly yields **P(granted) ≈ 0.55**, predicted
disposition **granted** (most plausibly at or shortly after the late-September
2026 long conference, with *Tovar* held). This is a genuinely close call that
sits just above 50% only because of the rare combination of a CFR, a conceded
split, and the government's own vehicle framing.

## Inputs used

- Snapshot `record/snapshots/2026-07-10.json` (docket 25-1236, Term 2025, paid;
  proceedings through the July 6 extension grant).
- Provisioned `record/documents/questions-presented.txt` and `petition.txt`
  (QP, split analysis, vehicle section, and the appended Third Circuit
  opinion's opening). No brief-in-opposition exists yet — the response is due
  August 10, 2026.
- `metrics/statpack.md` base rates; `fedcourts query` corpus priors (see
  `retrieval.md`).
- Mode: `forward` (pending case — no outcome exists; nothing here is leakage).

Degradations: the CourtListener MCP server failed on every call in this cell
(`REDIS_URL is not set; cannot access session store`), so I could not check the
live status of the companion *Tovar* petition; and the committed statpack lacks
the "Modern discretionary-cert petitions by disposition" section the task
prompt anchors on (both noted in `flags.json`). Neither blocks the prediction;
both slightly widen its error bars.
