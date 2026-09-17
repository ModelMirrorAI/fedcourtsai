# Rationale for the numbers

**P(grant) = 0.09; predicted disposition denied.**

## Anchor

`context.json` freezes `band: baseline` under `sal-v4`, Term 2025, `distribution_count: 1`, no CVSG, mode `forward`. The statpack's "Segment base rate by salience band (sal-v4)" table gives the baseline band's bracketed `reached` rate for Terms strictly before 2025 (2017–2024) as 4.7%, 4.6%, 4.6%, 4.5%, 5.6%, 5.8%, 5.9%, 5.7% on n = 1643, 1524, 1399, 1739, 1500, 1192, 1312, 1271. Pooled over those eight rows the anchor is about **5.1%** (≈593 / 11580). Petitioner is a private party (a former CBP officer prosecuted by the United States), so the baseline floor is the right class.

## Adjustments up

- **The Court called for a response after the Solicitor General waived** (Jun 30 waiver; Jul 27 "Response Requested"). This is the dominant signal in the record, and the salience band does not encode it: the band is built from distributions and CVSG status, and this petition sits at one distribution with no CVSG. A call for a response means at least one chambers wanted the government's view before voting; petitions in that position are granted at several times the undistinguished paid rate, although the large majority are still denied. This is what moves the number from ~5% to ~9%.
- **Publication and posture.** The Fifth Circuit opinion (168 F.4th 752, Smith, J., joined by Elrod, C.J., and Wilson, J.) is published, and the petition arrives with a clean § 1254(1) posture from a final criminal judgment.
- **QP 2 has some doctrinal substance.** The petition (read in full from `record/documents/petition.txt`; QPs from `questions-presented.txt`) frames a circuit tension over Screws's willfulness element, citing Walsh (2d Cir.) and Epley (6th Cir.) against Reese (9th Cir.), Pagan-Ferrer (1st), Bradley (7th), Thao (8th), Buntyn (10th), and Brown (11th). Mens rea in federal criminal statutes is an area where several Justices have shown interest.

## Adjustments down

- **The vehicle is poor.** I read the Fifth Circuit opinion via CourtListener. It is a sufficiency-of-the-evidence affirmance after a three-day bench trial at which the defendant presented no evidence. The willfulness holding rests on three grounds, one of which is concealment (a false verbal account and a false written report). Concealment is classic subjective-intent evidence, so the case does not cleanly present the "objective evidence only" question QP 2 poses. The Solicitor General will say the panel applied Screws's own "open defiance or reckless disregard" language, quoted from circuit precedent (Brugman), and that the asserted split is a difference in how circumstantial evidence is described, not in the legal standard.
- **QP 1 is weak.** Barnes v. Felix rejected a temporally narrow analysis that favored officers; here the broader context (Delgado instigating and escalating both encounters, opening a locked door to summon a man he claimed to fear) hurts the petitioner. The panel did not cite Barnes, but the petition's argument that it "silently reinstated" the moment-of-threat rule is a characterization the Court is unlikely to credit on these facts.
- **QP 3 fails on its facts.** A nose laceration with bleeding, and dizziness, confusion, and tinnitus, exceed even the Second Circuit's greater-than-de-minimis threshold, so the three-way "bodily injury" split the petition describes would not change the outcome.
- **The respondent is the United States, opposing.** The Court rarely grants a fact-bound criminal petition over the Solicitor General's opposition absent a crisp, acknowledged split; the opposition here will be filed because the Court asked, not because the government sees a problem.
- **Counsel and framing.** Counsel of record is a Texas practitioner rather than a Supreme Court specialist, and the petition presents four overlapping, heavily fact-dependent questions where one sharp question would have served better. The statpack's originating-circuit cut for ca5 (granted 1.6%, gvr 2.1%) is unremarkable relative to the modern-cert average.

Net: roughly double the anchor for the call for a response, then held below the ~13–18% "elevated"-band range because the vehicle and the government's position argue against a grant even where a Justice is curious.

## Other claims

- **relist-increment 0.95.** The response was requested after the only distribution; the BIO is due Sep 25, so the September 28 conference cannot consider the petition and a redistribution entry is all but certain. The residual is withdrawal or dismissal before redistribution, or a parse that does not record the new entry.
- **cvsg-increment 0.01.** The United States is a party.
- **summary-disposition-route 0.2 (conditional on grant).** No intervening decision supports a GVR; the only summary path is a government-identified error in the compelled response.
- **dissent-from-denial 0.08 (conditional on denial).** Separate writings on denials of fact-bound criminal petitions are uncommon; the call for a response raises the chance a chambers cares enough to write, but a statement is more likely than a dissent.
- **big_case_score 0.35.** A § 242 prosecution of a federal border officer with a live mens-rea question is meaningful to police-accountability prosecutions but narrow in reach and unlikely to draw broad attention.

## Uncertainty and where to discount me

- I have no published base rate for "call for response after waiver" in the statpack, so the size of that adjustment is my own estimate rather than a committed figure. If the true conditional grant rate for such petitions against the SG is closer to 5%, this number is too high; if closer to 15%, too low.
- I do not know which chambers requested the response or why. A request driven by interest in the Screws question could produce a grant on a better-framed reformulation than I credit here.
- No brief in opposition was provisioned (none has been filed; `documents.json` lists only the petition and QP file, both with text extracted), so my read of the government's likely position is inference from the record and the opinion, not from its filing.
- The CourtListener mirror of docket 73500250 carries no entries; the provisioned snapshot (created 09/16/2026) is the freshest docket source I had, and I found no indication the petition has been decided.
