# Reasoning — P(grant) = 0.72

**Inputs read.** Snapshot `2026-10-07.json` (forward mode, cutoff
2026-10-08, band `high` under sal-v4, distribution_count 1, CVSG 2026-06-01);
provisioned documents: QP text, petition (truncated at cap), BIO, cert reply,
and the SG's invited brief (29 pp., text extracted, not truncated). No
retrieval beyond those inputs and the committed statpack.

**What the Solicitor General recommended.** Grant as to Question 1, reformulated
to add "without an *additional* inquiry" so the parties are actually adverse
(the BIO says the parties agree on QP1 as framed); deny as to Question 2
(Item 303), calling this case an unsuitable vehicle for that issue. The SG
also says the Ninth Circuit's QP1 analysis is wrong, conflicts with other
circuits, and threatens significant consequences. The SEC is on the brief.

**Anchors.**
- Band `high`, bracketed `reached` rate pooled over Terms 2017–2024 (strictly
  before the case's 2025 Term): about 35% (≈314 grants over n≈898).
- Statpack CVSG cut (paid scored segment, all Terms): granted 29.3% + GVR 5.5%
  ≈ 35% over n=164 resolved. That cut pools every recommendation; no committed
  table splits by the SG's recommendation.

**Adjustment.** The SG's recommendation is the single strongest cert signal
there is. My recollection of the literature on CVSG outcomes (not a committed
figure) is that the Court grants in roughly three-quarters or more of cases
where the SG recommends a grant, and very rarely where it recommends denial.
Because the CVSG population mixes both, an affirmative recommendation moves the
~35% anchor far up. Other supporting factors: three cert-stage amicus briefs
(SIFMA/Chamber, WLF, Prof. Grundfest), elite counsel, a divided Ninth Circuit
panel with a substantial dissent, and a recurring question about IPO and
periodic disclosure.

**Why not higher.** (1) Interlocutory posture — the Ninth Circuit reversed a
dismissal and remanded, and the BIO leans on that. The Court has nonetheless
granted many pleading-stage securities cases (Omnicare, Macquarie). (2) The
BIO says the parties don't disagree on QP1 as written; the SG's need to
reformulate makes the vehicle less clean, and the Court could balk. (3) The
Court has recently dismissed securities cases as improvidently granted when
they turned out fact-bound, which may make it cautious. (4) The SG supports
only one of the two questions, which slightly weakens the recommendation.

**Claims.**
- `relist-increment` 0.96: after a CVSG brief the petition is almost always
  distributed again for conference; only a withdrawal or settlement would stop
  that.
- `cvsg-increment` 0.01: the CVSG has already issued, so this claim is vacuous
  for this cell.
- `summary-disposition-route` 0.03 (conditional on grant): no intervening
  decision, and the SG asks for plenary review.
- `dissent-from-denial` 0.10 (conditional on denial): a denial would most
  likely rest on the interlocutory posture, which rarely draws writing, but a
  Justice could write given the SG's view that the decision is wrong.
- `order-writers`: small per-Justice probabilities, consistent with the 0.10
  conditional and a ~28% chance of denial. A grant order carries no writing.

**Uncertainty.** The main question is whether the reformulation and the
adversity concern push the Court to deny or to wait for a cleaner case. The
petition text was cut at the cap; I relied on its QP section and the SG/BIO
account of the decision below.
