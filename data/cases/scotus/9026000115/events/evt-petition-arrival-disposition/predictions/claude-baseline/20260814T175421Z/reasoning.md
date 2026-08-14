# Rationale — P(grant) 0.015

**The cell.** An arrival-moment cert cell (`moment: arrival`), forward mode:
the petition was docketed July 24, 2026 and the record shows no distribution,
no CVSG, and no response yet — that absence is the moment's definition, not a
gap. The frozen context carries `band: baseline` under `sal-v2`,
`distribution_count: 0`, Term 2026.

**Anchor.** The statpack's sal-v2 salience-band table matches my context's
version, and my frozen band is `baseline` — the weakest band, whose bracketed
`reached` figure is the whole paid scored segment's rate, which is exactly the
arrival population's base rate the prompt directs an arrival cell to anchor on.
Pooled over the nine rendered Terms (2017–2025, all strictly before Term
2026), the bracketed `reached` rates weighted by their risk-set denominators
come to ≈6.5%; the most recent Term (2025) sits at 5.4%. So my starting point
is ≈0.06. The petitioner is private, not federal, so the federal-band segment
does not apply.

**Adjustments, all downward.**
- *No circuit conflict.* The petition alleges none — a grep of the full
  petition text finds no split or conflict language. The "Reasons for
  Granting" argue sufficiency of the evidence: that the district court and
  Fourth Circuit misapplied *Groff v. DeJoy*, 600 U.S. 447 (2023), by
  accepting a non-economic (health-and-safety) undue-hardship defense without
  cost evidence, and that a fact dispute over the vaccine's EUA status was
  glossed over. The supporting authorities are district-court decisions, not
  conflicting circuit holdings. This is error correction, the classic denial
  shape.
- *Poor vehicle markers.* The decision below is an **unpublished per curiam
  affirmance** (the appendix says so expressly), which the Court usually
  treats as a weak vehicle and which signals the Fourth Circuit saw the case
  as factbound.
- *Weak drafting signals.* Four questions presented, of which QPs 3 and 4
  restate QPs 1 and 2 at the district-court level; all four are "did the court
  below err" formulations. Counsel is a small Maryland firm, not a repeat
  Supreme Court practitioner.
- *Originating circuit.* CA4 petitions grant at 1.3% overall in the statpack's
  circuit cut (a blended paid+IFP figure, so a soft signal, but not an upward
  one).
- *Subject-matter history.* The Court has repeatedly declined COVID-mandate
  religious-objector petitions, and post-*Groff* percolation is a reason to
  wait, not to grant an unpublished sufficiency case.

The one countervailing consideration is that how *Groff*'s
"substantial increased costs" language applies to non-economic hardship claims
is a genuine, recurring post-*Groff* question. But this petition frames it as
record-bound error rather than a doctrinal conflict, so it earns only a small
residual, not a rescue. I land at **0.015** — well below the 6.5% arrival
anchor, reflecting that this petition lacks every marker that drives the
anchor's grant mass (splits, government or state petitioners, published
precedential decisions, experienced cert counsel).

**Claims.**
- `disposition` 0.015 — restates the number above.
- `relist-increment` 0.97 — the frozen count is 0, so this resolves on the
  petition being distributed *at all*. A paid petition with a response due
  August 24, 2026 will almost certainly reach a fall conference; the residual
  3% covers withdrawal, settlement, or procedural dismissal before any
  distribution.
- `cvsg-increment` 0.005 — private Title VII dispute, evidentiary framing,
  weak petition; CVSGs are rare even among strong paid petitions.

**Uncertainty and discounts.** I could not verify whether any pending merits
case could generate a GVR in light of an intervening decision — the corpus
query surface has no subject-matter filter and I did not find one otherwise;
if one exists, the grant-side probability is understated. My read of the
respondent's position is inference from the docket (no BIO exists yet — at
arrival none can). The corpus priors I pulled were mostly granted
time-extension applications rather than cert grants (see `retrieval.md`), so
retrieval added little beyond the committed statpack; the number rests on the
statpack anchor plus the provisioned petition and QP texts.
