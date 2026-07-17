# Dittmer v. Dittmer, No. 25-1245 — petition disposition

**Prediction: denied. P(grant, GVR included) = 0.002.**

## The case

Ronald and Irene Dittmer, a married couple in their mid-sixties proceeding pro
se, petition for certiorari from the Appellate Court of Illinois, First
District (Nos. 1-24-1269 & 1-24-1274, consolidated), which affirmed two-year
plenary orders of protection entered against them under the Illinois Domestic
Violence Act (750 ILCS 60) in favor of their daughter-in-law, Katie Dittmer.
The Illinois Supreme Court denied leave to appeal on January 28, 2026. The
petition (26 pages, filed April 28, 2026, docketed May 4, 2026, paid docket)
raises four questions: (1) that the protective orders burden their First,
Second, Fifth, and Fourteenth Amendment rights (free exercise — a "prayer
walk" near the respondent's home was the triggering incident — speech, arms,
due process, equal protection); (2) that the Illinois Appellate Court wrongly
rejected their constitutional arguments as forfeited despite their counsel's
"plain error"/ineffective assistance in failing to raise them at the hearing;
(3) a facial vagueness/overbreadth challenge to the IDVA; and (4) that the
state courts ignored documented procedural irregularities (an allegedly
altered transcript, a compressed briefing schedule, witnesses not called).

## Why this petition will be denied

Every certworthiness factor points the same way; the only question is how far
below the paid-docket base rate to set the number.

1. **No split, no authority conflict.** The petition cites a single case
   (Kennedy v. Bremerton School District) and identifies no conflict among
   circuits or state high courts on any question presented. It expressly
   frames the IDVA question as one of "first impression" — an argument for
   percolation, not review.
2. **Fact-bound error correction.** The heart of the petition is a
   re-argument of the evidence (the prayer walk, a Christmas card, a
   reprimanding email) against the circuit court's preponderance finding of a
   risk of future harm. The Court does not sit to re-weigh state-court
   domestic-relations records.
3. **Vehicle defects are fatal even on the petition's own telling.** The
   Illinois Appellate Court held the constitutional claims forfeited because
   they were not raised at the merits hearing — an adequate and independent
   state procedural ground that would block review of QP 1 and 3. QP 2 tries
   to route around the forfeiture through ineffective assistance of counsel,
   but there is no federal constitutional right to effective counsel in a
   civil protective-order proceeding, so the theory states no federal claim.
   QP 4's procedural-irregularity grievances are state-law record-management
   complaints.
4. **The Second Amendment angle has no traction post-Rahimi.** United States
   v. Rahimi (2024) upheld disarmament of persons subject to
   domestic-violence protective orders. A civil, fact-bound, forfeited
   as-applied challenge by pro se petitioners is not the vehicle the Court
   would choose even if it wanted to revisit the civil-order margin.
5. **Docket posture is the quiet-denial pattern.** The respondent filed no
   brief in opposition by the June 3 deadline; the petition was distributed
   June 17 for the September 28, 2026 conference — the end-of-summer "long
   conference," where the overwhelming mass of petitions is denied without
   comment. No response was requested, there is no relist, no CVSG, no
   amicus. A grant essentially never happens from this posture without the
   Court first calling for a response.

## Base rates and adjustment

From the committed statpack (live/historical slice, denial-reweighted):

- Modern discretionary-cert petitions overall: ~3% granted; October Term 2025
  overall grant rate 2.5% (paid class 5.4%, IFP 1.1%).
- Relist count 0: denied 97.3%, granted 0.8% — this petition has no relist
  and, having been distributed straight to the long conference with no
  response, is squarely in that bucket.
- No CVSG: 95.0% denied, 3.0% granted.
- Originating court "Appellate Court of Illinois, First District": 10 of 10
  resolved petitions denied.

The paid-docket rate (~5%) is dominated by counseled petitions with real
splits; the relist-0 bucket (0.8%) is closer, and the specific features here
— pro se, intra-family civil dispute, forfeited claims, no BIO called for —
sit well below even that bucket's average. I set P(grant) at 0.002, which
also folds in the negligible GVR path (no plausibly intervening decision) and
leaves the residual mass on rare distribution artifacts. Predicted
disposition: **denied**, most likely on the order list following the
September 28, 2026 conference (October 5, 2026).

## Big-case score

0.03. A private family conflict with no institutional parties, no
circuit-level doctrine at stake, and no plausible press or market attention;
even a hypothetical grant would be a narrow, fact-specific matter.

## Inputs used

- Provisioned snapshot `record/snapshots/2026-07-17.json` (docket 25-1245:
  filing, distribution, paid status, no response).
- Provisioned `record/documents/petition.txt` (full 26-page petition text)
  and `questions-presented.txt` — read in full; the QPs and "Reasons for
  Granting" section drive points 1–4 above.
- Committed `metrics/statpack.md` base rates (no salience-band table in this
  statpack build, so I anchored on the relist/CVSG/originating-court cuts and
  the Term 2025 fee-class rates).
- One CourtListener MCP docket lookup confirming the case remains pending
  (no termination date, no cert-granted/denied date) — forward-mode check
  only; no outcome exists to leak.
- The corpus query sidecar was unreachable in this cell, so `fedcourts query`
  priors were unavailable; per the contract I degraded to the statpack and
  provisioned inputs, which are ample for this petition. This degrades
  nothing material: the statpack cuts are the relevant priors here.
