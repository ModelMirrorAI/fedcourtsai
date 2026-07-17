# James P. Abrams v. United States, No. 25-1236 — cert disposition

**Prediction: grant — P(grant, GVR included) = 0.55.**

## The legal question

Whether a general motion for judgment of acquittal under Fed. R. Crim. P. 29
preserves de novo appellate review of the sufficiency of the evidence, or
whether the defendant must articulate each specific evidentiary deficiency to
avoid plain-error review. The Third Circuit (Smith, J., joined by Bibas and
Scirica) expressly "decline[d] to follow" the "well accepted" rule of seven
sister circuits and held that a general Rule 29 motion does not preserve
sufficiency arguments, affirming Abrams's 48-count fraud conviction under
plain-error review. 165 F.4th 784 (3d Cir. Jan. 30, 2026).

## Governing standard for the prediction

Cert is discretionary; the operative question is whether this petition clears
the Rule 10 bar — a real, outcome-determinative conflict among the circuits on
an important, recurring federal question, presented in a clean vehicle. The
base rate for a paid petition is low (statpack: paid-petition grant rates of
5.4% / 6.9% / 8.0% for Terms 2025 / 2024 / 2023), so the burden is on the
signals to move the estimate far from that anchor.

## Facts from the snapshot and provisioned documents that drive the call

Strongly pro-grant:

1. **Call for response after waiver (June 9, 2026).** The United States waived
   its response (May 21); the petition was distributed for the June 18
   conference; the Court then requested a response — a deliberate act by at
   least one chamber, and empirically among the strongest single pre-grant
   signals for a paid petition. The Court then granted the SG an extension to
   August 10, 2026, so the petition is live and being taken seriously. The
   committed statpack has no CFR cut, but its adjacent signal cuts calibrate
   the magnitude: 2 relists → 33.6% grant, 3+ relists → 21.8%, CVSG → 27.1%,
   against a 0.8% rate for zero-signal petitions.
2. **A mature, explicitly acknowledged circuit split.** The petition counts
   7 circuits (CA1, CA2, CA6, CA7, CA9, CA10, CADC) holding a general Rule 29
   motion preserves de novo review, against 4 (CA3, CA5, CA8, CA11) requiring
   specificity. The decision below *itself* frames the disagreement — the
   panel expressly declined to follow the majority rule — which removes any
   "split is illusory" argument.
3. **The government has conceded the split and invited resolution.** Below,
   the government's brief told the Third Circuit "this appeal presents an
   opportunity for the Court to resolve th[is] open question," and its April
   7, 2026 brief in Tovar v. United States, No. 25-6344, recognized the
   circuit split and suggested this Court could resolve it with an appropriate
   vehicle — while flagging Tovar's vehicle problems. That posture makes a
   BIO that denies the split's existence unlikely.
4. **Ideal-vehicle characteristics.** A pure question of law; the motion below
   was "as general as they come" (a one-sentence Rule 29(a) motion, argument
   waived); the standard-of-review holding was squarely decided as a
   "threshold question" the court said it "must resolve"; and the plain-error
   standard was outcome-determinative in form (the court affirmed under the
   "devoid of evidence / shocking" plain-error bar without a de novo pass).
5. **Cert-stage amicus support and elite counsel.** NACDL and a Former Judges
   group filed amicus briefs at the petition stage (both distributed);
   petitioner is represented by Debevoise (David O'Neil, former DOJ). Paid
   petition.
6. **Practical importance.** Rule 29 motions occur in nearly every federal
   criminal trial; per the petition, over 40% of federal criminal trials now
   occur in minority-rule circuits, and the majority-side waiver trap (a
   specific motion waives unlisted grounds) makes the conflict affirmatively
   dangerous for defense counsel.
7. **A companion petition is being held.** CourtListener shows Tovar
   (25-6344, CA11, IFP, filed Dec. 11, 2025) still pending with no grant or
   denial — consistent with the Court holding it while this cleaner paid
   vehicle ripens, exactly the pattern the petition urges (grant Abrams, hold
   Tovar).

Against a grant:

1. **The BIO is not yet filed.** The SG's brief (due Aug. 10) is the largest
   unresolved variable. The government prevailed below on a rule it advocated;
   its most probable BIO argues the evidence was sufficient under *any*
   standard of review, making the preservation question non-outcome-
   determinative in this record. The Third Circuit never performed a de novo
   sufficiency pass, so the argument is contestable, but harmlessness-type
   vehicle attacks defeat many otherwise-grantable petitions.
2. **The Court denies most split cases.** Even acknowledged splits often
   percolate for years; a standard-of-review/preservation question is
   important to practitioners but not the kind of question the Court is ever
   *forced* to take, and it could prefer a vehicle where the standard clearly
   changes the outcome.
3. **No relists yet, no CVSG** — the classic terminal pre-grant signals have
   not yet had the chance to accrue; the CFR is the strongest signal available
   this early in the petition's life.

## From base rate to 0.55

Anchor at ~6% (paid petition, recent Terms). The CFR alone historically moves
a paid petition into roughly the 25–40% range (the statpack's 2-relist and
CVSG buckets, 33.6% and 27.1%, are the closest committed analogues). On top of
that, this petition stacks nearly every other positive covariate at once: an
explicit, mature split framed by the decision below; the government's own
on-record acknowledgment of the split and of this case as a resolution
opportunity; two cert-stage amici; an apparently clean pure-law vehicle; and a
held companion case whose vehicle defects the SG itself identified while
pointing to "an appropriate vehicle." Cases carrying the full stack are the
ones that populate the top salience tier, whose conditional grant rate runs
well above any single-signal bucket.

The main haircut is the unfiled BIO and the general reluctance of the Court to
take even good split cases: I put roughly 45% on a plenary grant of this
petition, ~5% on the Court taking the issue through another vehicle in a way
that still produces a grant-side disposition here (hold followed by GVR if the
petitioner side prevails), and ~50% on denial (the Court denies both petitions
or the BIO's vehicle attack lands). Net: **P(grant incl. GVR) ≈ 0.55**, with
`predicted_disposition = granted` (a plenary grant, not a GVR, is the modal
grant-side outcome — there is no intervening decision to GVR against, unless
Tovar were granted first and decided favorably).

Timing expectation (not scored): BIO Aug. 10, 2026 → distribution for the
late-September 2026 long conference → disposition in early OT2026, plausibly
with one or more relists first.

## Leakage note

Forward-mode cell; the petition is genuinely undecided (response due Aug. 10,
2026). No search touched this case's own disposition — the only external
lookups were the corpus statpack/priors and the *companion* Tovar docket's
status, which is legitimate pre-decision forward signal. No `flags.json` is
warranted: no data-quality, scope, or blocking issue arose.
