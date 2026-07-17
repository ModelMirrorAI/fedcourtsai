# Nexstar Media Group, Inc. v. DirecTV, LLC — No. 25-1243 (cert petition disposition)

**Prediction: denied is the modal outcome; P(grant, GVR included) = 0.22.**

## The legal question

Whether a plaintiff has antitrust standing to recover downstream losses flowing
from its decision *not* to purchase an allegedly price-fixed product. The
Second Circuit (24-981, published Dec. 16, 2025, divided panel) reversed a
S.D.N.Y. dismissal and held that DirecTV — which walked away from
retransmission-consent negotiations with Mission and White Knight, took the
blackout, and claims lost subscriber revenue — pleaded antitrust injury
(reframed as "reduced output") and qualifies as an efficient enforcer under
*Associated General Contractors*. Judge Sullivan dissented, calling the
injury indirect and speculative and noting that before this decision "no
circuit had held that a priced-out non-purchaser plausibly alleged antitrust
standing." Rehearing en banc was denied Jan. 28, 2026.

## Governing standard for the prediction

Cert is discretionary; the operative question is whether four Justices see a
split worth resolving in a clean vehicle. The petition's cert case: a claimed
square 2–1 split with the Ninth Circuit (*City of Oakland v. Oakland Raiders*,
20 F.4th 441 (2021)) and Tenth Circuit (*Montreal Trading v. Amax*, 661 F.2d
864 (1981)), a published dissent below expressly framing the conflict, a
threshold question the Court has not substantively revisited since *AGC*
(1983), and a pleading-stage posture with no alternative grounds.

## Docket facts that drive the estimate (snapshot 2026-07-17)

1. **Paid petition, elite counsel** (Covington counsel of record; Wiley Rein
   and Venable for co-petitioners; King & Spalding for respondent). Paid
   petitions granted at ~5.4% in Term 2025 per the statpack's per-fee-class
   detail (~6.9% Term 2024).
2. **Call for response.** DirecTV waived (June 1); the petition was
   distributed for the June 25 conference; on June 23 the Court **requested a
   response** (due July 23, since extended to Aug. 21). A CFR after a waiver
   is the single strongest pre-BIO grant signal on this docket: it means at
   least one chambers pulled the case out of the deny pile. Conditional grant
   rates for called-for-response paid petitions run several multiples of the
   paid base rate (roughly 8–15% in published studies), and this petition is
   above the average CFR case on the other observables below.
3. **Split quality: real but contestable.** *City of Oakland* is recent,
   published, and framed in the same terms (priced-out nonpurchaser, prior
   course of dealing, speculative chain), so the dissent's framing is
   colorable. But the BIO has material to work with: *Montreal Trading*
   predates *AGC*; *City of Oakland* involved a municipality's derivative
   tax/investment injuries with more causal links; and the CA2 majority
   distinguished both on DirecTV's direct prior course of dealing. The Court
   could plausibly deny for percolation given the split is 2–1 and newly
   minted (Dec. 2025).
4. **Vehicle.** Clean in one sense — antitrust standing was the sole basis of
   decision, at the pleading stage, outcome-determinative — and the Court has
   repeatedly taken antitrust pleading-gate cases in exactly this
   interlocutory posture (*AGC*, *Twombly*, *linkLine*). Interlocutory
   posture still costs something at the margin, and the parties are in
   active multi-front litigation (the petition's own disclosure notes the
   contested Nexstar–TEGNA merger injunction now on appeal in the Ninth
   Circuit, DirecTV as plaintiff), so a global settlement mooting the
   petition is a nonzero path to `dismissed`.
5. **No relists yet and no CVSG** — the relist cut (2 relists → ~34% grant in
   the statpack) is not yet observable because the BIO isn't in; the first
   informative conference will be the late-September 2026 long conference at
   the earliest. No cert-stage amici appear on the docket, but the CFR
   restarted the Rule 37.2 amicus window, so that absence is weak evidence.

## Weighing

Anchor on the paid-petition rate (~5–6%), not the whole-docket rate. The CFR
multiplies that anchor severalfold; the square-split framing with a published
dissent, 40-year doctrinal gap, Second Circuit's outsized antitrust docket,
and top-tier counsel push above the average CFR case; the contestable split,
interlocutory posture, percolation option, and settlement risk pull back
down. I land at **P(grant incl. GVR) = 0.22**. A plain GVR is implausible (no
intervening SCOTUS decision on point), so the grant mass is a plenary grant;
the modal single disposition remains **denied** (~0.74), with a small
`dismissed` tail (~0.04) for settlement/withdrawal given the parties' broader
commercial entanglement.

`granted = 0` states the modal binary call; `probability = 0.22` carries the
forecast.

## Big-case score

0.55 — a grant would produce the first substantive antitrust-standing
decision since *AGC* (1983), a threshold rule for every private treble-damages
suit, with immediate stakes for retransmission-consent bargaining across the
broadcast/MVPD industry. High significance for the business and antitrust
bar; limited general-public salience. Scored on the QP, posture, and parties
only.

## Inputs used

- Provisioned snapshot `record/snapshots/2026-07-17.json` (docket through
  June 26, 2026: waiver, distribution, response request, BIO extension).
- Provisioned `record/documents/questions-presented.txt` and `petition.txt`
  (full petition; anchored on the QP, the split argument at Part I, and the
  vehicle argument at Part III). No BIO exists yet — the weighing above
  discounts the petition's characterizations where a BIO would predictably
  contest them (split squareness, course-of-dealing distinction).
- Committed `metrics/statpack.md` + `statpack.json` per-fee-class Term detail
  (base rates, relist/CVSG/circuit cuts). The statpack build carries no
  salience-band table, so the paid-fee-class Term rate is the anchor used.
- One CourtListener MCP opinion search confirming the CA2 decision below
  (24-981, filed 2025-12-16, published) — mode is `forward`, retrieval
  unrestricted; no information about this petition's disposition exists (it
  is pending), and none was sought.
