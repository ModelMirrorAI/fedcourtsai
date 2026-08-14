# Rationale — why 0.45

**The cell.** CVSG-moment cert cell (`moment: cvsg`), forward mode. The frozen
context carries band `high` (sal-v2), `distribution_count` 1, `cvsg_date`
2026-06-01, Term 2025. The snapshot (2026-08-14) shows a fully briefed paid
petition: filed February 5, 2026, three cert-stage amici (Grundfest,
SIFMA/Chamber, Washington Legal Foundation), BIO April 23, reply May 11,
distributed for the May 28 conference, CVSG June 1.

**Anchors.** Band is `high`, frozen at prediction, so the scored yardstick is
the bracketed *reached* rate. Pooling the statpack's "Segment base rate by
salience band (sal-v2)" high-band bracketed figures over the Terms strictly
before this case's own (2017–2024, n≈1,059 weighted) gives roughly **40%**.
The "Cert petitions by CVSG status (paid scored segment)" cut is consistent:
CVSG'd petitions resolve granted 30.1% + gvr 5.5% ≈ **36% grant family**
(denied 62%). Both cuts largely encode the same signal — the CVSG is what put
this petition in the high band — so I treat them as one anchor near 0.36–0.40,
not two independent ones.

**Adjustments up from the anchor.** (1) *Doctrinal tailwind*: the petition sits
directly downstream of Macquarie Infrastructure v. Moab Partners (2024), which
unanimously cabined pure-omissions liability under Rule 10b-5(b); the Ninth
Circuit's reading of Section 11(a)'s misleading-omissions prong pulls the other
way, and the Court has shown recent, repeated appetite in this exact space
(Macquarie; Facebook v. Amalgamated Bank, also from the Ninth Circuit).
(2) *Vehicle investment*: Jeffrey Wall (Sullivan & Cromwell) with Gibson Dunn,
Cravath, and Orrick, plus Chamber/SIFMA and WLF amici at the cert stage — the
defense bar is treating this as the vehicle. (3) *Speed*: the CVSG came at the
first conference, without a relist, which reads as genuine interest rather
than a courtesy. (4) The likely posture of the current SG/SEC is sympathetic
to petitioners on cabining private Securities Act liability, and the Court
follows the SG's cert recommendation in most CVSG'd cases.

**Adjustments down.** (1) *Interlocutory posture* — the BIO's strongest card:
the Ninth Circuit reversed a dismissal and remanded, and the BIO argues the
panel decided less than petitioners claim (no holding on materiality, duty, or
the existence of a trend), making the questions look fact-bound. An SG
recommendation to deny on vehicle grounds is a live outcome, and conditional on
it denial is very likely. (2) The Facebook DIG shows the Court's recent
willingness to walk away from Ninth Circuit securities-disclosure vehicles
that prove fact-entangled — which the SG will weigh at the cert stage.
(3) Some settlement risk while the case sits with the SG (a securities class
action with dismissal reversed), which would resolve the petition ungranted.

**Net.** A rough SG decomposition — P(SG recommends grant) ≈ 0.55, P(grant |
favorable SG) ≈ 0.75, P(grant | unfavorable SG) ≈ 0.15 — gives ≈ 0.48; the
pooled anchors say 0.36–0.40. I commit **0.45**, slightly above the band
anchor on the case-specific strength, held below the decomposition for the
posture risk. Since 0.45 < 0.5, `granted` is 0 and the modal single
disposition is `denied`; conditional on any grant I expect plenary `granted`,
not a GVR or summary reversal (no intervening decision exists to ride on).

**Claims.** `disposition` restates 0.45. `relist-increment` 0.96: the docket
shows one distribution, and redistribution after the SG's invited brief is
near-mechanical — the residual is settlement/withdrawal before the SG files.
`cvsg-increment` 0.02: a CVSG is already on the docket, so the claim is
vacuous for this cell and the harness masks it; the number is stated because
the contract requires one.

**Uncertainties and discounts.** The dominant uncertainty is the SG's
recommendation, which will not exist for months; my 0.55 on it leans on the
administration's deregulatory posture and is soft. I did not verify the
claimed circuit splits beyond the petition's and BIO's competing accounts
(the BIO contests that any circuit has adopted the contrary rule on QP1's
framing). The corpus citation lookup for Macquarie returned no rows (sparse
citation coverage), so the Macquarie characterization rests on the petition,
the BIO, and general knowledge, not a corpus-hydrated opinion text.

**Input notes.** `questions-presented.txt` is a mis-extracted
table-of-contents fragment, not the QP page (flagged, as it was in the prior
run's cell); the full QP text is in `petition.txt`, which I used instead.
`petition.txt` is marked truncated (233 pages including appendices) but the
petition body through the vehicle section is present. BIO and reply are on the
docket; the BIO text was provisioned and read.
