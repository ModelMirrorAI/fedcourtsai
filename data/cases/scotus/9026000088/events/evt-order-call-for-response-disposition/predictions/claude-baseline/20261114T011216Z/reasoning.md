# Reasoning — Alaska Policy Forum v. Alaska Public Offices Commission (No. 26-88)

**P(grant) = 0.16; call: denied.**

## What I read

- Snapshot `2026-09-01.json` (truncated provenance, cut at 2026-09-01): petition filed July 13, 2026 from the Alaska Supreme Court (583 P.3d 701, Feb. 13, 2026); all three respondents (the Commission, Yes on 2, Protect My Ballot) waived; 13 cert-stage amicus briefs filed Aug. 7–20; distributed Aug. 26 for the Sept. 28 conference; **response requested Aug. 31** (due Sept. 30).
- `questions-presented.txt` and the body of `petition.txt` (truncated around the appendix; I read the petition's own argument, not the Alaska opinion itself). No BIO exists at this moment, and I do not infer what it will say.
- `same-question.json`: empty list — no similar pending or granted petition was matched, so no hold theory.
- `context.json`: forward mode, band `baseline` (sal-v8), `cert_anchor.rate` = 0.0517.
- Forward-mode check of the Court's live docket (Nov. 14, 2026): the response deadline was extended to Nov. 30, 2026 for all respondents, and four more amicus briefs were filed Sept. 30. The petition is still pending; nothing there claims a disposition.

## Anchor and adjustments

- Anchor: the frozen baseline-band reached rate, ~5.2%. The statpack's whole-docket modern rate is lower still (grant family ~3%).
- **Call for response (up, modestly).** No committed table conditions on a called-for response. My judgement is that a CFR after waiver takes a paid petition out of the dead-list pool and roughly into the high single digits to ~10% on its own; most such petitions are still denied. This is my own estimate, not a pack figure.
- **Amicus volume (up, materially).** Thirteen amicus briefs before the cutoff (17 by now) is extreme for the cert stage. The statpack's amicus cut puts the `2+` bucket at ~22.6% grant family (n≈1451 resolved) against 3.7% at zero. That cut is marginal and read at disposition, and these amici are an ideologically aligned coalition organised by repeat players, so I do not stack it fully on top of the CFR — the two signals overlap (the amici probably helped draw the CFR).
- **Subject matter (mixed).** Donor disclosure and associational privacy is an area where the Court has acted (AFP v. Bonta), and the fact pattern — a 501(c)(3) regulated for issue speech that never mentions the ballot measure — is sympathetic to several Justices. Against that, the Court has repeatedly denied campaign-finance disclosure petitions since Citizens United upheld disclosure 8–1; the corpus shows Gaspee Project v. Mederos (21-890) denied after three distributions, and No on E v. Chiu (23-926), an on-communication donor-disclaimer case raising nearly the petition's third question, was also turned away.
- **Vehicle (down).** The petition's "splits" are soft: the first question is mostly framed as conflict with WRTL II, and the lower-court disagreement it cites is diffuse. Three questions, one of them a vagueness challenge to a state-law test as applied to specific communications, read fact-bound. The decision is from a state court of last resort construing state statutes; the respondents will have a full BIO to argue independent state-law framing and factual specificity.

Netting these: about three times the band anchor, 0.16. I would not go above ~0.22 without a relist after the BIO, nor below ~0.10 given the CFR plus this amicus count.

## Other claims

- `relist-increment` 0.97: the petition must be redistributed after the response; only a withdrawal/dismissal would prevent it (masked on this moment anyway).
- `cvsg-increment` 0.02: state campaign-finance law, no federal programme at stake; the Court rarely invites the SG on such questions.
- `summary-disposition-route` 0.08 (conditional on a grant): no intervening decision to GVR on that I know of; a summary reversal on WRTL II grounds is conceivable but unlikely.
- `dissent-from-denial` 0.10 (conditional on denial): Justice Thomas has long opposed compelled disclosure and Justices Alito/Gorsuch have shown interest, but noted dissents were absent in the comparable recent denials. `order-writers` is consistent with this (Thomas highest).

## Where to discount me

- I did not read the Alaska Supreme Court's opinion (cut from the staged petition text), so my vehicle assessment relies on the petitioner's characterisation.
- The CFR uplift is judgement, not a committed base rate.
- Corpus query worked; CourtListener MCP was not needed. One live-docket fetch was made (forward mode).
