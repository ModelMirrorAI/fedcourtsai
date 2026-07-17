# Hastings College Conservation Committee v. California, No. 25-1231 — cert prediction

**Prediction: deny. P(grant, GVR included) = 0.07.**

## The legal questions

Petitioners — an alumni association and descendants of Serranus Clinton Hastings —
challenge California's AB 1936 (2022), which renamed UC Hastings to "College of the
Law, San Francisco," stripped the Hastings heirs' statutory board seat, and included
legislative findings that S.C. Hastings "perpetrated genocidal acts." The petition
(from a published decision of the California Court of Appeal, First Appellate
District, 115 Cal. App. 5th 272; review denied by the California Supreme Court on
January 28, 2026) presents two questions:

1. **Contract Clause / reserved powers.** Whether the 1878 Act — which took
   Hastings's $100,000 in exchange for a college "forever" bearing his name with a
   board seat "always" reserved for his heirs — created contractual obligations the
   State cannot escape via the reserved powers doctrine; and relatedly whether
   *United States v. Winstar Corp.*, 518 U.S. 839 (1996), preserves at least a
   money-damages remedy.
2. **Bill of Attainder Clause.** Whether legislation posthumously declaring an
   individual guilty of crimes and stripping statutory benefits from him and his
   descendants is a bill of attainder.

## Base rates (committed statpack)

- Modern discretionary-cert petitions, Term 2025: **grant ≈ 2.5%** overall;
  **paid-petition grant ≈ 5.4%** (this is a paid petition, `sJsonCaseType: "Paid"`).
  The statpack in this build carries no salience-band table, so the paid fee-class
  rate is my anchor.
- Relist cut: 0-relist petitions grant at 0.8% — but that cut is uninformative here
  because this petition never reached its June 25 conference; the call for a
  response intervened.
- Originating-court cut: Court of Appeal of California, First Appellate District —
  12 resolved priors, 0 granted (83% denied, 17% dismissed). Small sample, but
  state-intermediate-court petitions grant rarely.
- No CVSG (and none plausible — no federal interest requiring the SG's views).

## Signals from the snapshot (2026-07-17)

**Positive:**
- **The Court called for a response (June 22, 2026)** after both respondents waived
  — the classic signal that at least one chambers took interest. Empirically a CFR
  raises a paid petition's grant odds several-fold over the no-CFR baseline (the
  respondents' extension to August 21 is routine and adds nothing). This is the
  dominant upward adjustment.
- Clean-ish vehicle on the first QP: demurrer sustained without leave to amend, so
  the questions arrive as pure questions of law on a final state judgment
  (28 U.S.C. § 1257(a)).
- Published lower-court opinion; competent private counsel; culturally salient
  facts (the renaming fight drew New York Times coverage) that could attract some
  Justices' interest in legislatures "adjudicating" historical guilt.

**Negative:**
- **No split.** The petition alleges no circuit or state-court conflict on either
  question; it argues error correction ("conflicts with this Court's
  jurisprudence") plus importance. *Winstar* is a plurality, and how the reserved
  powers/unmistakability doctrines apply to a college naming statute is fact-bound
  — the Court rarely grants splitless state-specific Contract Clause disputes.
- **Bill of attainder claims essentially never get granted.** The Court last
  decided one on the merits in *Selective Service System v. MPIRG* (1984), and the
  posthumous-attainder theory is novel; novelty without a conflict usually means
  denial, not a grant.
- **Vehicle problems on the damages issue.** The Winstar-damages argument was held
  waived below; petitioners must overcome an adequate-and-independent-state-ground
  hurdle (*Cruz v. Arizona*) before reaching it — an unattractive posture.
- State respondents (California AG, the College) waived initially — no respondent
  thought it cert-worthy; no amicus support appears on the docket as of the
  snapshot, unusual for a genuinely hot culture-war petition.
- Granted Term-2025 priors in the corpus typically show multiple conference
  distributions (e.g., Monsanto v. Salas, 4 distributions before its 2026-06-30
  grant); this petition has one distribution and the record now resets pending the
  BIO.

## Weighing

Start at the paid-petition anchor (~5%). The CFR is a genuine, sizeable positive
update; against it sit the absence of any alleged split, the fact-bound
reserved-powers question, the waiver/adequate-state-ground problem on the damages
theory, the near-zero historical grant rate on attainder claims, and the weak
record of California intermediate-court petitions. A CFR is also consistent with a
chambers wanting a BIO before a reasoned denial or a dissent-from-denial. Net: a
bit above the paid baseline but well below coin-flip territory — **P(grant) = 0.07**,
most likely disposition **denied** (a GVR path is implausible: no pending related
case to GVR in light of). Timing note: with the BIO due August 21, 2026, this will
likely be considered at the late-September 2026 long conference or shortly after.

## What I relied on

Provisioned snapshot (2026-07-17), the petition text and questions-presented
excerpt under `record/documents/`, the committed `metrics/statpack.md`/`.json`
(Term-2025 paid fee-class rates, relist/CVSG/originating-court cuts), two
`fedcourts query` pulls of granted 2020s SCOTUS priors, and one CourtListener
search confirming the lower-court opinions (no outcome exists to leak — the
petition is pending). No brief in opposition exists yet; per the documents
manifest, only the petition and QP were provisioned, so the respondent-side view
is unrepresented in this forecast.
