# Reasoning — why P(grant) = 0.13

## Anchor

Cell context (`record/context.json`, harness-frozen): `forward` mode, band
`baseline` under `sal-v2`, `distribution_count` 1, no CVSG, Term 2026, paid
docket. The statpack's "Segment base rate by salience band (sal-v2)" table
matches the context's salience version, so the scored anchor is the
**baseline band's bracketed `reached` rate**, pooled over every rendered Term
strictly before 2026 (2017–2025, all nine rendered rows): weighted
≈ **6.5%** (≈862 grants / 13,163 reached, from the per-Term reached rates and
denominators). That is the rate a paid petition that has reached the baseline
band actually faces, and the yardstick this cell is scored against.

## What moved me up from 6.5%

- **A divided, published D.C. Circuit decision** (In re United States, 143
  F.4th 411 (D.C. Cir. 2025)) granting the government mandamus, with a
  dissent, followed by a six-month en banc process before rehearing was denied
  (Jan. 6, 2026). The petition's appendix confirms the panel division.
- **Colorable circuit splits on both QPs.** The petition pleads a split with
  the First, Ninth, and Tenth Circuits (e.g., United States v. McVeigh, 106
  F.3d 325 (10th Cir. 1997)) on whether the All Writs Act lets a court of
  appeals give the government interlocutory review Congress withheld — a
  recurring federal-courts question squarely governed by Will v. United
  States, 389 U.S. 90 (1967) — plus a softer split on the "clear and
  indisputable" mandamus standard.
- **The government's own importance concession.** The mandamus grant below
  rested on the government's claim of "immense national importance"
  (Pet.App.57a–58a), which cuts against a vehicle-based BIO.
- **Cert-stage amicus support**: three briefs already filed (Prof. Vladeck,
  Prof. Finkelstein, and September Eleventh Families for Peaceful Tomorrows
  with 66 victim families). Cert-stage amici are among the strongest observable
  grant correlates, and victim-family support for the petitioners removes the
  easy political reading.
- **Originating court**: CADC petitions grant at the highest circuit rate in
  the statpack's modern cut (5.5% vs. 1–3% elsewhere).
- **Elite counsel** (Michel Paradis / Steptoe, ACLU, Military Commissions
  Defense Organization) and a Chief-Justice-granted 60-day extension — the
  profile of a petition filed to be granted, not to exhaust a remedy.

## What held me down

- **The Court's revealed behavior on military commissions.** It has denied
  every Guantánamo commission-related petition since Boumediene (al-Nashiri,
  al Bahlul, Baluchi) despite repeated, well-lawyered attempts. That is a long,
  consistent record of staying out.
- **The Solicitor General will oppose**, having won below, and SG opposition
  on a case the government itself litigates is a heavy negative signal.
- **Functionally interlocutory posture.** Denial lets the capital trial
  proceed; the questions can return on review of any conviction. The Court
  prefers that path, and the BIO will say so.
- **The remedy problem.** A grant aims at reinstating plea agreements both the
  Biden and current administrations tried to undo — an outcome several
  Justices will not want to force, and one reachable only by taking the case.
- **Kavanaugh's non-participation** (he took no part in the sealing motion):
  an eight-Justice conference means five votes needed for a majority at the
  merits against four to grant, which historically discourages grants.
- **The split is contestable.** Mandamus standards are fact-bound; the BIO
  will argue Cheney v. U.S. District Court, 542 U.S. 367 (2004), and the
  supervisory-mandamus line make the claimed conflict shallow.

Net: this petition's content is far stronger than its frozen band (the band is
docket-signal-driven, and the petition has not yet even been distributed on
the merits of cert — see the flag), so I sit well above the 6.5% anchor, but
the commissions-abstention record and SG opposition keep me under 1-in-5.
**P(grant) = 0.13**; modal disposition **denied**. `granted = 0` is the same
call on the binary axis.

## Claims

- `disposition` 0.13 — restates `probability`.
- `relist-increment` 0.97 — the frozen count is 1, but that distribution was
  of the sealing motion (25M91), not the petition; the BIO is due Aug. 26,
  2026, so the petition's own conference distribution is still ahead and a
  further distribution is near-certain. The residual 0.03 covers withdrawal or
  dismissal before conference.
- `cvsg-increment` 0.01 — the United States is the respondent; a CVSG is not a
  live possibility when the SG is already a party.

## Uncertainty and discounts

- I cannot read the BIO (not yet filed), so the strength of the government's
  vehicle arguments is inferred, not observed.
- The statpack's relist cut (relist-1 ≈ 8.2% grant) is a terminal-count
  bucket and does not condition on this case's pre-distribution reality; I used
  the band anchor instead, per the prompt's frozen-band rule.
- Corpus `query` retrieval returned no usable priors (the `--citation` filter
  hit the documented coverage gap; a `--disposition granted` pull surfaced
  mostly application-extension rows), so my comparables for the
  commissions-denial pattern (al-Nashiri, al Bahlul, Baluchi) come from
  general legal knowledge, not corpus rows. Discount accordingly.
- This is a famous, heavily covered case; I carry background knowledge of it
  from training, including the D.C. Circuit's decision — which is on the
  provisioned record anyway. The cert outcome does not exist yet (forward
  mode), so there is no outcome to leak, and I did not retrieve any.
- Judgment calls a reader should probe: the +6.5-point lift over the anchor
  rests mostly on the amicus/counsel/split profile; if one believes the
  Court's commissions abstention is near-absolute, 0.05–0.08 is defensible; if
  one weighs the Will question's importance to the Justices' institutional
  interests more heavily, 0.20+ is defensible.
