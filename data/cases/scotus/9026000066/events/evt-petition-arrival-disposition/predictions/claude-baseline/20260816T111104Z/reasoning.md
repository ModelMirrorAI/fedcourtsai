# Rationale — P(grant) 0.005

**Cell.** Cert stage, `moment: arrival`, forward mode. `record/context.json`
freezes band `baseline` under `sal-v3`, term 2026, `distribution_count` 0,
`signals_observable` true. Per the arrival-moment contract I anchored on the
arrival population's own rate — the weakest (`baseline`) band's bracketed
`reached` figure, which is the whole paid scored segment's grant rate,
unconditional on trajectory — never the relist-0 terminal cut.

**Anchor.** Pooling the statpack's "Segment base rate by salience band (sal-v3)"
baseline-band bracketed `reached` rates over the nine rendered Terms strictly
before this case's (OT2017–OT2025, n = 13,163 weighted): **≈ 6.5%**. The
OT2026 row is empty, so the shown strictly-prior window is the whole usable
window.

**Adjustments — all downward, and large.** The anchor is the average paid
petition; this one sits far below it on every observable margin:

- **Pro se petitioner.** The petitioner is his own counsel (the snapshot's
  attorney block names him, non-counsel-of-record; the petition is signed
  "Pro Se Petitioner"). Pro se paid petitions grant at a small fraction of
  the counseled paid rate.
- **Subject matter and posture.** A state-court divorce decree (Maricopa
  County dissolution), affirmed in an **unpublished memorandum decision** by
  the Arizona Court of Appeals, with discretionary review denied by the
  Arizona Supreme Court. State family-law error-correction is a class the
  Court essentially never takes. The statpack's state-court originating rows
  show sub-1% grant rates even among counseled petitions.
- **No split, no recurring open question.** The three QPs dress fact-bound
  grievances (a waiver footnote, a "technical error" holding, a
  missing-transcript presumption under ARCAP 11) in due process terms. The
  petition cites Lee v. Kemna and Michigan v. Long for reviewability but
  alleges no conflict among state courts or circuits on any of the three
  questions. Adequacy-of-state-ground disputes this fact-specific are
  error-correction asks.
- **Vehicle.** The record-dependence the petition itself describes (missing
  transcripts, an incomplete record) cuts against it as a vehicle even on its
  own framing.

The terminal baseline-band grant-family rate (~1.2%: granted 0.8% + gvr 0.4%)
is an upper bound on this petition's realistic pool, and it is dominated by
counseled petitions from federal circuits. I put this petition well below
that: **0.005**.

**Claims.**
- `disposition` 0.005 — equals the headline probability, as required.
- `relist-increment` 0.96 — from zero distributions shown, P(≥1 distribution
  ever). Almost every docketed paid petition reaches a conference; the residue
  is early dismissal (Rule 46 settlement — conceivable in a family dispute) or
  withdrawal, roughly the 2% dismissed share in the modern-cert table plus a
  margin.
- `cvsg-increment` 0.002 — a purely private state-law dispute; no federal
  interest could prompt an invitation.
- `summary-disposition-route` 0.4 — conditional on a grant. In the grant
  family for baseline-band petitions the gvr share is roughly a third, and for
  a petition this fact-bound a summary route is relatively more plausible than
  plenary review; but no intervening decision exists to predicate a GVR, so I
  stay near the population's conditional share rather than above it.
- `dissent-from-denial` 0.003 — conditional on denial. Statements or dissents
  accompany a small fraction of a percent of denials and concentrate in
  capital, qualified-immunity, and high-salience constitutional cases; nothing
  here fits.

**Uncertainty and discounts.** The main uncertainty is not the disposition
(denial is near-certain) but the tail shape: whether the petition is dismissed
or withdrawn before conference (which resolves the relist-increment claim
false) — a settlement in a divorce matter is possible and I cannot see it
coming from this record. Both provisioned documents extracted cleanly
(`empty_text: false`), so my read of the petition is from its text, not
inferred. I did not have a brief in opposition (none filed yet at this
moment), which is the moment's definition rather than a gap. The corpus
`query` I ran returned recency-ranked recent denials rather than close
analogues — the surface has no text-similarity ranking for this shape — so it
informed nothing beyond confirming the tooling works; the anchor is entirely
the statpack.
