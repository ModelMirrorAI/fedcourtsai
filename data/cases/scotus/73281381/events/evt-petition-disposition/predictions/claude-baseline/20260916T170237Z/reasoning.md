# Why 0.16

## What I read

Provisioned inputs: `record/snapshots/2026-09-15.json` (the baseline named by `context.json`),
`record/context.json` (forward mode, band `elevated` under `sal-v4`, `distribution_count` 2, no CVSG,
Term 2025, paid), `record/documents/questions-presented.txt`, `petition.txt` (35 pp., full text) and
`brief-in-opposition.txt` (34 pp., full text; `documents.json` shows neither truncated nor
`empty_text`). Beyond those: the Seventh Circuit opinion via CourtListener, the supremecourt.gov
dockets of the two companion petitions the BIO names, one corpus `query` for recent priors, and one
web search on *Pung v. Isabella County* (a decided, unrelated tax-sale case the BIO cites). See
`retrieval.md`. I did not search for this case's own disposition; the conference is September 28,
2026, twelve days after this run, so the outcome does not exist.

## Anchor

Cert-stage, `moment: distribution` cell, band `elevated`, version matches the statpack's
"Segment base rate by salience band (sal-v4)" table. Pooling the bracketed `reached` figure over the
Terms strictly before OT2025 that the table renders (OT2017–OT2024, n = 336+354+300+342+397+334+347+400
= 2,810 weighted) gives roughly **17%** (≈484/2,810). Cross-checks from the paid scored-segment cuts:
relist bucket 1 (the state a `distribution_count` of 2 reads as) is granted 8.2% + gvr 5.1% ≈ 13% grant
family; CVSG `none` is 4.0% + 2.3%; CA7 origin is 1.1% granted + 1.4% gvr, below the docket average.
My number, 0.16, sits essentially on the band anchor. The case-specific adjustments below pull in
opposite directions and roughly cancel.

## Adjustments down (the petition itself is weak)

- **Facial-only challenge.** The BIO's strongest point, and the Seventh Circuit's actual ground: under
  *Keystone Bituminous* petitioners must show the "mere enactment" of MCC §9-100-120 is a taking, and
  the ordinance permits release, indefinite storage, or scrap-value sales yielding no surplus. The
  petition never engages the facial standard. That is the kind of vehicle defect the Court treats as
  disqualifying for plenary review.
- **No split.** Petitioners concede the circuits agree (CA7 here, *Tate v. D.C.*, CADC 2010, and a
  Ninth Circuit unpublished affirmance) and argue agreement makes review more important. The
  *Bennis* "punitive and remedial jurisprudence" line is settled and the Court has, in *Culley* and
  elsewhere, been reluctant to reopen forfeiture doctrine on constitutional grounds outside the Eighth
  Amendment.
- **Tyler is distinguishable on its own terms.** *Tyler* rested on the taxing power and the government
  there disclaimed any punitive purpose. *Pung* (June 2026) stays inside that tax-sale frame. The
  petition's Magna Carta / common-law surplus argument is attractive but unlikely to move the Court
  in a facial posture with no record of what proceeds the City actually kept.
- **Counsel and presentation.** A small Chicago plaintiffs' firm, the petition mis-cites the appellate
  record ("CA5 ECF") and, as the BIO notes, does not cite *Hadley*, the very case the decision below
  applies. Not decisive, but the Court's clerks notice.

## Adjustments up (the Court is already looking at the question)

- **Response requested after both respondents waived** (April 30, 2026). That is an affirmative act:
  someone in chambers pulled this petition off the May 14 conference to see the City's answer. The
  timing — three weeks after *Hadley* (No. 25-1158) and *Pena* (No. 25-1163) were docketed on April
  6–9 raising the police-power exception to the Takings Clause — makes the most likely explanation
  that the petition was flagged as a companion to those, not that it was found independently
  grant-worthy. This is the reason the band is `elevated` rather than `baseline`, and I read it as
  real but derivative signal.
- **Companion petitions on the same conference.** Both *Hadley* and *Pena* were distributed on June 24
  for the September 28, 2026 conference, each with five amicus briefs (Pacific Legal Foundation,
  Professor Ely et al., Leo Lech et al., Small Property Owners of San Francisco, Chief Tiderington).
  Two Justices (Sotomayor and Gorsuch, *Baker v. City of McKinney*, 2024) have already said the
  question deserves the Court's attention once percolated. I put P(the Court grants plenary review in
  Hadley and/or Pena) near 0.35 — real interest, but the Court denied *Lech* (2020) and *Baker* (2024)
  on the same question and both circuits here reached the same bottom line.
- **This case would ride that grant as a hold.** The Seventh Circuit's opinion applies *Hadley*'s
  "classic example" principle expressly, and QP 2 is verbatim the Hadley/Pena question. A hold is the
  natural treatment; if the Court then cuts back the police-power exception, a GVR follows.

## The arithmetic behind 0.16

- Independent plenary grant of this petition (alone or consolidated): ≈ 0.03.
- Hold-and-GVR: P(Hadley or Pena granted) 0.35 × P(this petition is held rather than denied
  outright when that happens) 0.7 × P(the merits decision disturbs the police-power exception in a
  way that reaches a forfeiture case) ≈ 0.55 ≈ 0.13.
- Total ≈ 0.16. Since `gvr` counts as a grant on the binary axis, `probability` covers both branches;
  `predicted_disposition` is `denied` because that remains the single most likely label (≈ 0.84).

The claims block follows: `disposition` 0.16 restates this; `summary-disposition-route` 0.8 is the
GVR share of the grant mass (0.13/0.16); `relist-increment` 0.6 reflects that a relist or hold of the
companion trio is more likely than a clean October 5 denial of all three; `cvsg-increment` 0.03
because a CVSG on a municipal ordinance would go to the lead vehicles, not here; `dissent-from-denial`
0.10 because any writing attaches to *Hadley*/*Pena*.

## Where to discount me

- The whole upside rests on my read of Hadley/Pena, which I could not observe beyond their dockets.
  If a reader knows the Court's appetite for the police-power exception is lower than I think (two
  prior denials say it might be), the number should be nearer 0.06–0.08. If the Court is ready to
  take Hadley, 0.20–0.25 is defensible.
- The `elevated` band here is produced by the response-request redistribution, not by a true relist.
  The statpack's relist-count cut notes its count is an upper bound for exactly this reason, so the
  band anchor may slightly overstate the population this petition actually belongs to.
- I have not read the district court order or the Hadley/Pena petitions and BIOs themselves; my
  characterization of those cases comes from the BIO here, the CA7 opinion, and their docket sheets.
- `big_case_score` 0.5: a merits decision on police-power forfeiture of vehicles for civil-fine debt
  would be nationally significant and has drawn ProPublica-level coverage of Chicago's program, but
  the realistic grant form is a GVR, which decides nothing. The score is stakes-if-decided, per the
  contract, not the odds.
