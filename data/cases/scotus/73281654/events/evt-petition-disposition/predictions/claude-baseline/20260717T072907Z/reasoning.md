# Winnemucca Indian Colony v. United States, No. 25-1170 — cert prediction

**Prediction: deny. P(grant, GVR included) = 0.07.**

## The case

The Winnemucca Indian Colony, a small federally recognized tribe in
north-central Nevada, sued the United States in the Court of Federal Claims
under the Indian Tucker Act for money damages, alleging (Count Three, "Breach
of Trust – Water") that the BIA breached fiduciary duties by allowing
third-party developers to divert White's Creek — the Colony's only water
source — leaving its 320-acre trust parcel without water. The CFC dismissed,
applying *Arizona v. Navajo Nation*, 599 U.S. 555 (2023): neither the
Executive Orders creating the Colony, the Winters doctrine, nor 25 C.F.R.
§ 152.22 imposes a specific, money-mandating duty on the government to
protect the Colony's water from third-party interference. The Federal Circuit
affirmed (156 F.4th 1339, Oct. 16, 2025), holding Winters is a common-law
doctrine that does not itself create a trust obligation, and that § 152.22 —
a land-conveyance-approval regulation — "does not mention water rights."
Rehearing and rehearing en banc were denied January 8, 2026.

The petition (filed April 8, 2026, paid docket, Term 2025) argues the Federal
Circuit over-read *Navajo Nation*, which involved a demand for affirmative
steps to secure **new** water, not a failure to protect **existing** water
from third-party diversion — a distinction the petition says *Navajo Nation*
itself repeatedly drew, that *Hopi Tribe v. United States* (Fed. Cir. 2015)
preserved, and that the Federal Circuit's own *Ute Indian Tribe* (2024)
honored by letting existing-water mismanagement claims proceed while
dismissing new-water claims.

## The governing standard

Cert is discretionary (Rule 10): the Court looks for circuit splits,
important federal questions, and conflict with its own precedents. Because
Indian Tucker Act damages claims funnel exclusively through the Federal
Circuit, no true circuit split can develop — a structural handicap for this
petition class, partially offset when a petition presents a clean, important
question about the scope of a recent Supreme Court decision.

## Signals from the docket (snapshot 2026-07-17)

- **Call for response (the key upgrade signal).** The United States waived
  its response (May 7); the petition was distributed for the May 28
  conference; on May 27 the Court **requested a response** — meaning at least
  one Justice's chambers found it worth forcing the SG to engage. The SG then
  obtained an extension to July 27, 2026, so the disposition is realistically
  a fall-2026 conference item. CFR'd paid petitions grant at roughly an order
  of magnitude above the base rate, but the large majority are still denied.
- **Paid, counseled petition** from the Federal Circuit; no cert-stage amici
  as of the snapshot; zero relists so far (the CFR pre-empted the first
  conference).

## Base rates and adjustments

From the committed statpack (live/historical slice, denial-reweighted):
modern discretionary-cert petitions grant at ~2.5–3.3% per recent Term
(Term 2025: 2.5%; 2024: 3.0%; 2023: 3.3%). Federal Circuit originators run
near the average (granted ~3.0% on the reweighted cut). Zero-relist petitions
grant at 0.8%, but that cut does not condition on a CFR, which is this
docket's dominant live signal. (The statpack's salience-band table referenced
in the prompt is not present in the committed statpack, so I could not anchor
on a band rate; I approximated the CFR-conditioned rate from the historical
convention that a call for response lifts a paid petition into roughly the
8–12% range.)

Adjusting from a ~10% CFR-conditioned anchor:

**Down:**
- No circuit split is possible (Federal Circuit exclusivity), and the
  petition alleges none — it argues the Federal Circuit misapplied *Navajo
  Nation* and misread its own *Ute* decision. That is error-correction
  framing; QP2 literally asks whether the Federal Circuit "err[ed]."
- The Court decided *Navajo Nation* only three Terms ago, 5–4, against the
  tribe; taking this case would mean policing the decision's boundary almost
  immediately, on facts the lower courts found analogous.
- The petition is short and unpolished (typos, a miscited judgment date,
  no dedicated "reasons for granting" section keyed to Rule 10), filed by
  non-Supreme-Court-specialist counsel, with no amicus support — weak
  certworthiness packaging for a doctrinal-boundary question.
- The existing/new-water distinction, while real in *Navajo Nation*'s dicta,
  is entangled here with a fact-bound vehicle (a decades-long tribal
  governance dispute, an unquantified diversion record at the 12(b) stage).

**Up:**
- The CFR itself — some chambers (plausibly Justice Gorsuch, the *Navajo
  Nation* dissenter and the Court's most engaged Indian-law voice) wants the
  SG on record. Post-*Navajo Nation* boundary questions about
  third-party-interference trust claims are a genuine open issue the Court
  flagged: the *Navajo Nation* majority expressly noted the Navajos were
  *not* claiming interference with their water access.
- The intra-Federal-Circuit tension with *Ute* Part I.B (existing-water
  claims allowed to proceed) gives a doctrinal hook beyond pure error
  correction.

**Not a GVR candidate:** there is no intervening Supreme Court decision to
GVR in light of, and no mootness event; the realistic outcomes are deny
(possibly with a dissent or statement respecting denial) or a plenary grant.

## Bottom line

The CFR moves this well above the ~2.5% modern base rate, but the
error-correction posture, the absence of any split, the freshness of the
adverse *Navajo Nation* precedent, and the weak petition packaging cap it
below the raw CFR-conditioned rate. I estimate **P(grant) ≈ 0.07** and
predict **denied** — most likely after the BIO lands (due July 27, 2026) and
one or more fall-2026 conferences, with a realistic chance of a relist and a
dissent from denial if it goes as I expect.

## Inputs used

- Provisioned snapshot `record/snapshots/2026-07-17.json` (docket
  proceedings, parties, fee class, Term).
- Provisioned `record/documents/questions-presented.txt` and
  `record/documents/petition.txt` (full 32-page petition text; no
  brief-in-opposition exists yet — the SG's response is due July 27, 2026).
- Committed `metrics/statpack.md` base rates.
- One CourtListener search confirming the Federal Circuit opinion
  (No. 24-1108, decided 2025-10-16); corpus `fedcourts query` returned no
  matching priors (see `retrieval.md`).

Mode is `forward`; the petition is genuinely pending and no outcome exists
to leak.
