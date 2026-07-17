# Francis v. Allstate Insurance Co., No. 25-1218 — petition disposition

**Prediction: denied. P(grant, GVR included) = 0.002.**

## The case

Andron Miguel Francis, proceeding pro se (he is listed as his own counsel of
record, with a residential Conyers, Georgia address), petitions from the Court
of Appeals of Georgia's May 5, 2025 ruling in case A25D0341 — a "D"-prefix
docket, i.e. a *discretionary application* that the Georgia intermediate court
declined, in litigation against Allstate Insurance Company. A CourtListener
search shows this is Francis's second discretionary application against
Allstate in the same dispute (A25D0089, October 24, 2024, preceded it). The
snapshot's "DiscretionaryCourtDecision" date of September 30, 2025 indicates
the Supreme Court of Georgia thereafter denied review. The petition was filed
October 14, 2025 and docketed April 24, 2026 as a paid case.

The petition PDF itself is a scanned filing with no extractable text layer
(`documents.json` marks it `empty_text: true`), so the questions presented
could not be read; this analysis rests on the docket record and the lower-court
posture. That gap is flagged in `flags.json`. Nothing in the record suggests it
changes the outcome: every structural signal points the same way.

## The signals, none favorable

1. **Posture.** The case arrives from a state *intermediate* court's refusal of
   a discretionary application, after the state supreme court denied cert — a
   posture where there is rarely a reasoned decision on any federal question at
   all, and where independent-and-adequate state procedural grounds typically
   bar review. Insurance-coverage disputes between a policyholder and an
   insurer are quintessentially state-law matters; nothing on the docket hints
   at a substantial federal question, and certiorari review is limited to
   federal questions properly raised below (28 U.S.C. § 1257).
2. **Pro se petitioner.** Even in the paid pipeline, pro se petitions are
   granted at rates far below the already-low paid base rate; plenary grants
   are practically nonexistent absent an extraordinary vehicle.
3. **Respondent waived.** Allstate filed a waiver of its right to respond on
   June 22, 2026, and the Court distributed the petition two days later for the
   September 28, 2026 long conference *without calling for a response*. The
   Court does not grant certiorari without first requesting a response; as of
   this snapshot there is no CFR, no amicus support, and no relist.
4. **Base rates.** The corpus statpack's modern discretionary-cert anchor puts
   the overall grant rate at ~2.5–3% per recent Term (denial-reweighted), and
   the 0-relist bucket — where this petition currently sits — grants at ~0.8%.
   State-court-originated petitions in the corpus grant more rarely still
   (the Georgia intermediate-court rows show no grants). A corpus pull of
   recent granted petitions (2020s era) returned cases with clear federal
   questions — Second Amendment challenges, federal criminal cases, preemption
   disputes with represented parties — nothing resembling this profile.
5. **No GVR path.** A GVR requires an intervening decision plausibly bearing on
   a preserved federal claim; no companion or pending merits case is apparent
   that could supply one for a state-law insurance dispute.

## Probability

Starting from the ~0.8% zero-relist base rate and adjusting sharply downward
for the pro se posture, the state intermediate-court discretionary-denial
vehicle, the absence of any visible federal question, and the waived response
with no CFR, I set P(grant) at **0.002**. The residual mass covers the remote
chain of a CFR followed by relists and the small chance of a procedural
dismissal being recorded grant-side. Likeliest concrete outcome: denial on the
order list following the September 28, 2026 long conference (early October
2026).

**Predicted disposition:** denied (granted = 0). Confidence 0.92 — the small
uncertainty is about the disposition *label* (a dismissal is possible if a
procedural defect surfaces), not about the petition failing.

## Big-case score

0.02. A one-party insurance dispute with no doctrinal stakes, no public
attention, and no downstream effect beyond the parties.
