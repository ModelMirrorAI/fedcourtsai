# Petróleos de Venezuela, S.A. v. Helmerich & Payne International Drilling Co., No. 25-1256

**Prediction: P(grant, GVR included) = 0.35; modal disposition = denied.**

## The legal question

Whether the Second Hickenlooper Amendment, 22 U.S.C. § 2370(e)(2) — Congress's
response to *Banco Nacional de Cuba v. Sabbatino*, 376 U.S. 398 (1964) — displaces
the act-of-state doctrine in a damages suit over a foreign taking where neither the
expropriated property nor any property exchanged for it ever entered the United
States. The D.C. Circuit (153 F.4th 1316, Oct. 3, 2025) held the Amendment contains
no "domestic-nexus requirement," expressly rejecting the contrary readings of the
Second Circuit (*Banco Nacional*, 431 F.2d 394 (2d Cir. 1970); *Empresa Cubana*,
652 F.2d 231 (2d Cir. 1981)), the Fifth Circuit (*Compania de Gas*, 686 F.2d 322
(5th Cir. 1982)), and the New York and Texas high courts (*Perez*, 463 N.E.2d 5
(N.Y. 1984); *Ashley*, 556 S.W.2d 784 (Tex. 1977)). It was undisputed below that if
the act-of-state doctrine applies, it defeats H&P-IDC's expropriation claim — so
the question is dispositive.

## Posture and record facts driving the call

From the 2026-07-17 snapshot and the provisioned petition text:

- **Paid petition, elite counsel on both sides** (Vinson & Elkins for PDVSA;
  Gibson Dunn for H&P), docketed May 6, 2026 off a D.C. Circuit collateral-order
  appeal (rehearing en banc denied Dec. 3, 2025, with no dissent noted in the
  petition or its appendix description).
- **The Court called for a response.** Respondent waived (May 22); the petition was
  distributed for the June 18 conference; on June 8 the Court requested a response
  — i.e., it was pulled before conference on a sua sponte CFR. The BIO deadline was
  extended to August 7, 2026. A CFR after waiver is the classic signal that at
  least one chambers finds the petition non-frivolous; most CFR'd petitions are
  still denied, but the grant rate conditional on a CFR is several times the paid
  baseline.
- **This litigation has been to the Court before, and it granted.** *Bolivarian
  Republic of Venezuela v. Helmerich & Payne*, 581 U.S. 170 (2017), unanimously
  vacated the D.C. Circuit's permissive FSIA jurisdictional standard in this very
  case. The petition leans on that: "This Court has already intervened once in this
  case to correct a decision that erroneously expanded the judiciary's authority."
- **The subject matter is squarely in the Court's recent wheelhouse.** The Court
  has repeatedly granted FSIA-expropriation cases at interlocutory posture
  (*Helmerich* 2017; *Philipp*, 592 U.S. 169 (2021); *Simon*, 604 U.S. 115 (2025)),
  and *Simon* itself discussed the Hickenlooper Amendment's textual and historical
  link to § 1605(a)(3) — the very linkage the D.C. Circuit used to take pendent
  jurisdiction over the act-of-state ruling.
- **Split quality.** The conflict is real and acknowledged — the district court
  said it was "breaking ranks," and the D.C. Circuit expressly found the other
  courts' domestic-nexus reading "not persuasive." It is also *asymmetric in
  practical importance*: FSIA expropriation suits concentrate in the D.C. Circuit
  (the FSIA venue of default for foreign states), so the outlier circuit is the one
  that will hear most future cases — a point that cuts in favor of review because
  percolation cannot correct it. The weakness respondent will press: the other side
  of the split is old (1970–1984), the Second Circuit's *Banco Nacional* was
  vacated on other grounds, and no modern circuit has reaffirmed the
  domestic-nexus reading.

## Base rates and adjustment

From the committed statpack (live/historical slice, denial-reweighted):

- Modern discretionary cert petitions: grant ≈ 2.5–3.3% per Term overall; **paid**
  petitions ≈ 5.4–6.9% (Terms 2024–2025).
- **Originating court D.C. Circuit**: granted 11.8% (modern cert cut) — the highest
  of any circuit, consistent with the federal-government/foreign-sovereign docket
  it feeds.
- Relist and CVSG cuts (relist 2+ → 22–34% grant; CVSG → 27%) do not yet apply —
  the petition has not reached conference — but both are live upside paths here:
  this is a plausible CVSG candidate (foreign-policy sensitive, the United States
  filed at the merits stage in 2017), and CVSG'd foreign-sovereign petitions grant
  at ~27%.

Starting from the paid + CADC-origin neighborhood (~10%), the CFR-after-waiver
roughly doubles-to-triples the conditional odds, and the case-specific factors —
dispositive, cleanly presented question; acknowledged split; prior plenary grant in
the same litigation; the Court's demonstrated appetite for FSIA/act-of-state
boundary questions post-*Simon*; sovereign-dignity and reciprocity stakes that
mirror the concerns that drove *Helmerich* 2017 and *Philipp* — push well above
that. Against: the staleness of the split's other side gives the BIO a credible
"no live conflict" argument; the interlocutory posture, while not disqualifying in
FSIA cases, gives a deny-and-wait offramp; and even strong CFR'd petitions are
denied more often than granted.

I land at **P(grant) ≈ 0.35** — several times the salient-petition baseline, short
of even odds. Since 0.35 < 0.5, the modal single disposition is **denied**
(`granted = 0`), with the probability field carrying the substantial grant risk. A
plain GVR path is unlikely (no obviously controlling intervening decision — *Simon*
predates the D.C. Circuit's ruling and was applied by it), so the grant mass is
essentially plenary review.

## Timing

BIO due August 7, 2026 → distribution for the late-September 2026 long conference
at the earliest. Meaningful chance the first action is a CVSG rather than a
disposition, which would push resolution deep into OT2026 or beyond.

## Inputs used

- Provisioned snapshot `record/snapshots/2026-07-17.json` (docket entries through
  June 23, 2026).
- Provisioned `record/documents/questions-presented.txt` and `petition.txt` (51 pp.,
  full text) — the QP, the split argument (Part I), the vehicle argument (Part III),
  and the procedural history were all taken from these. No BIO exists yet
  (`brief-in-opposition.txt` not provisioned; response due Aug. 7, 2026).
- Committed `metrics/statpack.md` + `statpack.json` (per-fee-class Term rates).
- One successful `fedcourts query` for 2020s granted SCOTUS priors (context only);
  CourtListener MCP used to confirm the D.C. Circuit opinion below (filed
  2025-10-03, published, No. 24-7161). Details in `retrieval.md`.

Mode is `forward`; the petition is genuinely pending (no disposition entries in the
snapshot; nothing outcome-revealing surfaced in retrieval).
