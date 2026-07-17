# Khatibi v. Lawson, No. 25-1240 — cert petition disposition

**Prediction: denied is the single most likely disposition, but this is a
genuinely strong petition — P(any grant, GVR included) = 0.32.**

## The legal question

Whether private instruction in courses required for state licensure
constitutes government speech. California (Bus. & Prof. Code § 2190.1(d)(1))
requires every accredited CME course to include implicit-bias curriculum.
Petitioners — an ophthalmologist CME instructor and Do No Harm, Inc.,
represented by Pacific Legal Foundation and Consovoy McCarthy — challenged the
mandate as compelled speech. The district court dismissed on the pleadings;
a Ninth Circuit panel affirmed (145 F.4th 1139), holding CME courses are
*government speech* under the Shurtleff three-factor inquiry even though the
State does not create, review, or edit course content. Rehearing en banc was
denied (164 F.4th 1105) over two three-judge dissents (VanDyke, joined by
Bumatay and Tung; Tung, joined by Bumatay and VanDyke).

## Docket posture as of the 2026-07-17 snapshot

- Petition filed April 28, 2026 (paid, Term 2025 docket), after a Kagan-granted
  extension.
- Respondents (California DOJ, for Medical Board officials) **waived** the
  right to respond on May 18.
- **Six cert-stage amicus briefs** supporting the petition: Cato Institute,
  Association of American Physicians and Surgeons, Center for Equal
  Opportunity/Manhattan Institute, Judicial Watch, The Buckeye Institute, and
  **Montana et al.** (a multistate brief).
- Distributed for the June 25, 2026 conference; on **June 11 the Court called
  for a response** (CFR), mooting that conference. The BIO deadline was
  extended to **August 12, 2026**, so the petition will likely be distributed
  for the late-September 2026 long conference and resolved in October–November
  2026.

## Base rate and adjustments

Anchor (committed statpack, per-Term fee-class detail): **paid Term-2025
petitions grant at ~5.4%** (IFP ~1.1%; the modern discretionary-cert pool
overall is ~2.5–3.3%). The statpack's salience-band table described in the
prompt is not present in the committed statpack, so I anchored on the paid
fee-class rate and adjusted qualitatively.

Upward signals, roughly in order of weight:

1. **Call for response after waiver.** The Court does not CFR petitions it
   intends to deny routinely; at least one Justice's chambers wants the case
   briefed. Empirically a CFR raises paid-petition grant odds several-fold
   over the anchor.
2. **Three-judge dissental.** Dissents from denial of rehearing en banc are
   among the strongest observable cert predictors, and VanDyke's opinion
   expressly frames the panel as "out of step with Supreme Court precedent
   and sister circuits" — an invitation to review.
3. **Asserted circuit conflict.** The petition claims the 2d, 4th, 5th, 6th,
   8th, and 10th Circuits treat regulation alone as insufficient for
   government speech absent government control of the *message*, while the
   Ninth Circuit treated pervasive regulation as sufficient. The conflict is
   methodological rather than a square same-facts split (comparators involve
   flags, ballot summaries, library curation), which tempers its force — the
   BIO will attack it — but the outlier posture is credible.
4. **Heavy, ideologically resonant amicus support**, including a multistate
   brief. Cert-stage amicus volume of this size on a paid petition is a
   well-documented grant correlate.
5. **Doctrinal timeliness.** The Court has repeatedly policed the
   government-speech doctrine's boundaries (Tam 2017, Shurtleff 2022) and
   professional-speech compelled-speech doctrine (NIFLA 2018), and on
   March 31, 2026 decided **Chiles v. Salazar** (No. 24-539, confirmed via
   CourtListener), holding a restriction on licensed counselors' speech
   restricts *private* speech. The Ninth Circuit's panel and en banc rulings
   predate Chiles, so a **GVR in light of Chiles** is a live alternative to
   plenary review — and a GVR counts as a grant on the binary axis.
6. **Clean vehicle.** Final judgment on a pleading-stage dismissal resolving
   a pure legal question; no justiciability problems apparent.
7. **Elite repeat-player counsel** (PLF; Consovoy McCarthy).

Downward signals:

1. Even CFR'd, dissental-backed petitions are more often denied than granted;
   the modal outcome for any paid petition remains denial.
2. **No relists yet** — the classic proximate pre-grant signal (corpus
   priors: recent grants carry distribution counts of 3–22; relist-bucket
   base rates run 0.8% at zero relists vs ~22–34% at 2–3+). The case simply
   has not reached that stage, so this is neutral-to-unknown rather than
   negative, but it means the strongest confirmation is unobservable at this
   snapshot.
3. The Court may prefer **percolation post-Chiles**: deny (or GVR) and let
   the circuits apply Chiles to government-speech recharacterizations before
   taking the question.
4. California's BIO (due Aug 12) will contest the split's squareness and may
   recharacterize the mandate as curricular regulation of a state-created
   credential rather than compelled ideology.

## Quantification

Starting from the ~5.4% paid anchor: the CFR alone plausibly moves the case
to ~15–20%; the dissental, the six amici with state support, the circuit
outlier posture, the vehicle quality, and the Chiles GVR channel together
move it to roughly a one-in-three chance. I decompose approximately as:
plenary grant (or grant-in-part) ≈ 0.24, GVR in light of Chiles ≈ 0.08,
denial ≈ 0.62, dismissed/other ≈ 0.02.

- **probability (P(any grant)) = 0.32**
- **granted = 0** and **predicted_disposition = denied**, because denial
  remains the single most likely outcome at ~0.62.
- **confidence = 0.55** — the posture is unusually legible for a cert-stage
  forecast, but the decisive observables (BIO strength, relists) postdate the
  snapshot.

No per-justice votes: cert-stage vote predictions from this record would be
speculation, and the field is optional.

## Big-case score

0.7 — if decided, this would set the boundary between government speech and
compelled private speech for continuing-education mandates across every
licensed profession (medicine, law, accounting, engineering), on a politically
salient implicit-bias/DEI question, with multistate amicus interest. It is not
at the very top of the scale because the question is doctrinally contained and
the case would likely be decided on government-speech grounds rather than
producing a broad new compelled-speech rule.

## Inputs used

- Latest snapshot `record/snapshots/2026-07-17.json` (docket entries, parties,
  fee class, linked application 25A1032).
- Provisioned `record/documents/questions-presented.txt` and `petition.txt`
  (29 pp., full text) — anchored the QP and the split/precedent analysis.
  No BIO exists yet (respondents' waiver was superseded by the CFR; response
  due Aug 12), so `brief-in-opposition.txt` is legitimately absent.
- Committed `metrics/statpack.md` + `statpack.json` (per-fee-class Term rates,
  relist/CVSG cuts, circuit cut).
- One `fedcourts query` over granted 2020s SCOTUS priors (distribution-count
  calibration); one CourtListener MCP opinion search confirming Chiles v.
  Salazar (2026-03-31). Mode is `forward`; the petition is genuinely pending,
  and nothing outcome-revealing was encountered.
