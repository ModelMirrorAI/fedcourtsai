# Rationale for P(grant) = 0.13

## Anchor

Context: `mode: forward`, `band: baseline` under `sal-v4`, `distribution_count: 1`, `cvsg_date: null`, `term: 2026`, paid docket. The statpack's *Segment base rate by salience band (sal-v4)* table matches the context's salience version, so the band is the anchor. Pooling the `baseline` band's bracketed `reached` figures over every rendered Term strictly before OT2026 (OT2017 through OT2025, nine rows) gives **5.0%** over a weighted n of about 12,700 (the most recent five Terms alone pool to 5.4%). I read the `reached` figure, not the leading terminal-band one, because this petition is at its first distribution and has not ended anywhere.

For shape only: the relist-count cut says a petition that ends at zero relists is granted or GVR'd about 1.7% of the time while one relist lifts the grant family to about 13%; the CVSG cut is irrelevant here because the federal government is the respondent; the CA5 cut (grant family about 3.7%) sits near the segment-wide figure.

## What pushes up from 5%

- The question is one this Court itself flagged as open in *Axon* (2023): whether Congress may *expressly* strip district-court jurisdiction over structural constitutional challenges. The current Court has been receptive to structural separation-of-powers petitions (Axon, Jarkesy, Lucia, and, per the petition, *Trump v. Slaughter*, decided June 29, 2026).
- Professional cert-stage presentation: Pacific Legal Foundation as counsel, an NCLA amicus brief at the petition stage, a published Fifth Circuit opinion (153 F.4th 449), a clean jurisdictional posture with the agency proceeding stayed by agreement.
- The Solicitor General filed a 16-page brief in opposition rather than waiving, and devoted a section to opposing a hold, which signals the government saw the hold request as live.
- The petition's fallback request to hold for *Johnson v. United States Congress*, No. 25-735, creates a GVR path that an ordinary private petition lacks. *Johnson* concerns whether the Veterans' Judicial Review Act's express preclusion clause reaches constitutional challenges, so a decision there on clear-statement principles could bear on QP 1 even though, as the SG says, it involves no structural claim.

## What pushes down

- **No circuit split, conceded.** The BIO states and the petition acknowledges that the only other appellate decisions on express preclusion of structural claims (*Bohon v. FERC*, D.C. Cir.; *Azimov*, 9th Cir., unpublished) agree with the Fifth Circuit. The Court denied cert in *Bohon* in 2024 on the same question with NCLA-style framing. That is close to a direct prior denial.
- **MCorp.** The Court in 1991 applied the materially identical 12 U.S.C. 1818(i)(1) by its plain terms. The Fifth Circuit's companion decision in *Burgess v. Whang* (same panel, same day) rests on that provision. A grant would require narrowing MCorp.
- The Fifth Circuit was unanimous and denied rehearing en banc with no judge requesting a vote, in a circuit otherwise sympathetic to structural claims.
- QP 2's Article III theory has no lower-court support and the BIO's answer (channeling is not foreclosure; *Elgin*, *Jarkesy* itself arose on a petition for review) is conventional.
- The underlying allegations (self-directed transfers, unapproved payments) make this a less attractive vehicle than a regulated business challenging an agency's structure.

## Decomposition

I price the grant family as roughly 0.05 plenary grant plus roughly 0.08 GVR via a hold for *Johnson*: P(hold) about 0.25, and conditional on a hold, P(*Johnson* comes out in a way that produces a GVR rather than a later denial) about 0.4 to 0.45. Summing gives 0.13. The summary-disposition-route claim (0.65) is the GVR share of that family.

The relist-increment claim (0.40) combines the hold path (a held petition is redistributed after the lead case is decided, which I count as a further distribution) with an ordinary one-or-two-relist path of about 0.25 given no hold; both are above the segment-wide roughly 25% ever-relisted share because of the hold request.

## Uncertainties and where to discount me

- **Burgess.** The companion *Burgess v. Whang* decision may have its own petition pending; if so the two would travel together and the Court's treatment of Burgess would dominate. I could not check this (see retrieval degradation below).
- **Johnson's scope.** My hold probability is the softest number here. I could not read the *Johnson* QP or briefs; I rely on the petition's and the BIO's characterizations of it.
- **Snapshot vintage.** `context.json` names snapshot `2026-10-04.json`, which I read; `documents.json` records the petition, BIO, and QP all fetched 2026-10-04 with `empty_text: false` and no truncation. The conference is Oct 9, five days after the snapshot, so no disposition exists yet; nothing I saw revealed one.
- **Retrieval degraded.** All three CourtListener MCP calls (the Fifth Circuit opinion, the *Johnson* docket, a post-Axon express-preclusion opinion search) returned HTTP 429 rate-limit errors with about 19 minutes until capacity returned, so I made no further MCP attempts and worked from the provisioned filings, the statpack, and two `fedcourts query` calls. The query surface is weak for this purpose: the citation filter reported the corpus holds reporter cites on only about 200 SCOTUS rows, and the disposition/era query returned recent grants with no topical relation. The legal-landscape claims above (MCorp, Bohon's 2024 denial, Azimov) are drawn from the parties' own filings and general knowledge, not from a live check.
- I did not read anything under `data/qp-topics/`.
