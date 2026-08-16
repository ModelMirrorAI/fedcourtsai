# Rationale: P(grant family) = 0.02

## Anchor

This is an arrival-moment cert cell (`moment: arrival`): the record carries no
distribution, no relist, no CVSG by construction. `record/context.json`
freezes `band: baseline` under `sal-v3`, matching the statpack band table's
version, so the anchor is the **baseline band's bracketed `reached` rate** —
which for the weakest band is the whole paid scored segment's grant rate,
unconditional on trajectory, exactly the arrival population's own base rate
the prompt directs an arrival cell to. Pooling the rendered Term rows
strictly before this case's Term (OT2017–OT2025; the OT2026 row is empty)
gives roughly **6.5%** (≈862 weighted grants over n≈13,163). That is the
yardstick this cell's skill is scored against.

## Adjustments — down, substantially

- **No split.** The petition alleges no circuit or state-court conflict; it
  expressly styles QP 1 as a "Question of First Impression" and says "there is
  no controlling Supreme Court precedent directly on point." First-impression
  framing without a conflict is the classic denial profile.
- **Fact-bound and state-law-entangled.** QP 1's federal hook (Caperton /
  Williams / Lavoie due process) rests on an antecedent state-law predicate —
  whether one Maryland retired senior judge was categorically ineligible for
  recall under Md. CJP § 1-302 while allegedly practicing law — that the
  Maryland courts evidently resolved against the petitioner. That is a poor
  vehicle: the Court would have to relitigate Maryland recall law to reach the
  federal question.
- **QP 2 is not a federal question.** It asks for summary reversal because a
  later Maryland Supreme Court decision (Sugarloaf) tightened state-law
  attorney-fee-memorandum specificity. The Court cannot review a state court's
  application of its own fee rules; this QP contributes nothing to grant
  probability.
- **Low stakes, weak presentation.** A private residential-fraud /
  attorney-fee dispute; solo-practitioner counsel; the QPs are rambling,
  multi-clause run-ons. Presentation quality correlates with the Court's
  attention, and everything here signals the bottom of the paid pool.
- **Originating court.** State-court petitions in the pooled
  originating-court table grant rarely (the statpack's state high-court rows
  run ~0–1% granted).

The one genuine upward feature is the oddity of the core allegation — a final
judgment purportedly entered by a judge with no lawful authority to sit — which
is the kind of extreme-facts due-process claim that occasionally draws a
summary per curiam (cf. Rippo v. Baker). That keeps me from going to the
terminal-baseline floor (~1%), but it does not carry the petition anywhere
near the 6.5% average arrival, which includes the petitions that go on to
relist, attract CVSGs, and grant. I land at **0.02**.

## Claim numbers

- `disposition` **0.02** — as above; equals the top-level probability.
- `relist-increment` **0.96** — from a zero-distribution state this is P(ever
  distributed). Nearly every paid petition not withdrawn or dismissed reaches
  a conference; the residual ~4% covers pre-distribution dismissal/withdrawal
  (e.g., settlement of the underlying fee dispute).
- `cvsg-increment` **0.003** — CVSGs run ~1.3% of the paid segment overall
  (173/13,596 in the CVSG cut) and this case has zero federal interest;
  near-floor.
- `summary-disposition-route` **0.6** — conditional on a grant. The
  population's cert-order share of the grant family is large (the disposition
  table's gvr count is ~46% of granted+gvr, though the statpack warns the
  split is not comparable across Terms), and this case's only plausible
  favorable action is a summary per curiam on the judicial-bias claim rather
  than plenary review, so I sit above the population share.
- `dissent-from-denial` **0.01** — silent denials are the overwhelming norm,
  and nothing here attracts a statement. No published baseline; banked.

## Uncertainty and discounts

- The pooled 6.5% anchor is my own arithmetic over the band table's bracketed
  figures; the per-Term rates vary (5.4%–8.0%) and the weights are
  denial-reweighted estimates, so treat 6.5% as approximate.
- I have not seen the Maryland Supreme Court's decision below (the snapshot
  and provisioned documents do not include it, and I did not retrieve it), so
  my read of what the state courts held on the recall-eligibility question is
  inferred from the petition's own framing — which is an advocate's framing.
  If the state court in fact left the federal question cleanly presented and
  undecided, my downward vehicle adjustment is too harsh; I doubt it, but this
  is my largest uncertainty.
- The docket is linked with application 25A1252, which is just the
  time-extension application already reflected in the proceedings — no
  independent signal.
- One corpus `query` (a Caperton citation lookup) returned no rows — the
  citation column is a known-case lookup with sparse coverage — so no
  case-level priors beyond the statpack informed the number. Both provisioned
  documents extracted cleanly (`empty_text: false`); no brief in opposition
  exists yet (response due August 26, 2026), so the BIO side of the ledger is
  unknowable at this moment, as the arrival definition intends.
