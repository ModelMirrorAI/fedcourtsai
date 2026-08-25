# Rationale — P(grant) 0.92

**Anchor.** This is an arrival-moment cell with `band: federal` frozen in
`record/context.json` (sal-v3), and the committed statpack's "Segment base
rate by salience band (sal-v3)" table carries a `federal` column, so the
class's published anchor exists. Pooling the federal band's bracketed
`reached` rates over the Terms strictly before this petition's (OT2017–OT2025
as rendered: n = 21+15+29+19+11+40+26+23+17 = 201, implied grants ≈ 143) gives
a pooled grant-family rate of **≈ 71%**. The federal band is the strongest
band (its leading and bracketed figures coincide), so this is the risk-set
rate an arriving federal-petitioner petition actually faces, unconditional on
any trajectory — the right anchor for a zero-distribution record. The
aggregate federal-band cut says the same thing (granted 48.8% + gvr 22.4% ≈
71.2% of n=201).

**Adjustments up from 0.71 to 0.92.** The federal band pools every
SG-petitioner filing, including routine criminal and statutory cases where the
government seeks error correction. This petition sits at the extreme
grant-likely end of that pool on every observable margin:

- The court below entered a **final judgment invalidating the flagship policy
  of the administration** — Proclamation 10,888's entry suspension and asylum
  preclusion, which the government credits with a 93% drop in border
  encounters. The Court has taken every recent case in this class (Trump v.
  Hawaii; Biden v. Texas; DHS v. Regents; Trump v. CASA), split or no split.
- The **D.C. Circuit stayed its own mandate** pending certiorari — a signal
  the court of appeals itself expects review, and one that keeps the policy
  operative only so long as the case is headed here.
- **No percolation is possible**: the petition argues, plausibly, that the
  universal class forecloses any parallel challenge, so a denial gives the
  D.C. Circuit the last word on a question of this magnitude — the situation
  the Court most reliably corrects.
- The QPs include **8 U.S.C. 1252(f)(1) classwide relief**, a question the
  Court has repeatedly reached for (Aleman Gonzalez), and Rule 23/Article III
  class questions that give it multiple handles.

**Why not higher.** The residual ~8% is mostly not "the Court shrugs": it
covers the petition being overtaken before disposition (the proclamation
rescinded, superseded, or its statutory basis altered, leading to dismissal or
a mootness denial), a hold behind some related vehicle that ends in something
other than a grant-family outcome, and ordinary model humility about a single
case. A contested straight denial of this petition would be extraordinary.

**Claims.**
- `disposition` 0.92 — restates the top-level probability (grant family:
  plenary grant, granted-in-part, or GVR).
- `relist-increment` 0.97 — the record shows **zero distributions** (the
  petition was docketed today; `distribution_count: 0`). The claim is
  therefore P(the petition is ever distributed), and essentially every paid
  petition that is not withdrawn or dismissed first reaches a conference; the
  government will not withdraw, so the residual is early mootness/dismissal.
- `cvsg-increment` 0.01 — the petitioner is the Solicitor General; the Court
  does not call for the views of a party. Near-zero rather than zero only for
  resolution-mechanics humility.
- `summary-disposition-route` 0.04 (conditional on grant) — no intervening
  decision exists to GVR against; the government seeks plenary review; a
  ruling of this scope decided in the cert order itself would be
  unprecedented-adjacent. Stated as the conditional, per the declaration.
- `dissent-from-denial` 0.30 (conditional on denial) — a contested denial
  would likely draw a noted dissent, but a large share of the denial branch is
  quiet mootness/overtaken-case denials, which pulls the conditional down.

**Sources and their limits.** I anchored on the committed `metrics/statpack.md`
(federal band segment, relist and CVSG cuts) and read the provisioned petition
text (`petition.txt`: the QPs, introduction, statement, and the
warrants-review section; `documents.json` marks it `truncated: true` — the
408-page PDF includes ~350 pages of appendix, and the text I have covers the
full petition body, so the truncation cost me the lower-court opinions'
verbatim text, not the petition's argument). No brief in opposition exists yet
(due September 23, 2026), so I have only the petitioner's characterization of
the decision below — the usual arrival-moment asymmetry, and one reason my
confidence is 0.85 rather than higher. Two corpus `query` pulls added little
beyond the statpack (rows carry no captions for these dockets); one
CourtListener search confirmed the litigation chain (D.D.C. 2025-07-02;
D.C. Cir. partial stay 2025-08-01; D.C. Cir. merits opinion 2026-04-24,
No. 25-5243) and surfaced no disposition of this petition, which cannot exist
— it was docketed today. Corpus vintage: the statpack and corpus were
refreshed in commits dated 2026-08-24, the same day as this run's snapshot.

**Where to discount me.** The 0.71 → 0.92 uplift is judgment, not a published
cut — the statpack has no "SG petitions from invalidated flagship policies"
stratum, and n=201 federal-band cases over nine Terms show Term-to-Term rates
from 43.5% to 89.5%, so the anchor itself is noisy. If the political or
statutory landscape moves against the proclamation before conference, the
mootness branch grows and my number is too high.
