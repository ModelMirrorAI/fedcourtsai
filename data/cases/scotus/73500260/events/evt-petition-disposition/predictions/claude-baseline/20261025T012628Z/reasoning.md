# Reasoning — P(grant) 0.09

**Inputs read.** Snapshot `record/snapshots/2026-10-25.json` (docket through
Sep 8, 2026), `record/context.json` (forward mode, band `baseline` under
sal-v4, distribution_count 1, no CVSG, Term 2025), and the provisioned
petition and QP text (`documents.json`: both extracted, not truncated, not
OCR). No brief in opposition exists yet — the response is due Nov 2 — so my
read of the opposition is inference.

**Anchor.** The `baseline` band's bracketed `reached` rate in
`metrics/statpack.md` (*Segment base rate by salience band (sal-v4)*) over
Terms strictly before 2025 (2017–2024) runs 4.5%–5.9%, pooling to roughly
5%. My context's band and salience version match the table.

**Adjustments up.**
- The Court **requested a response** after the first distribution, after the
  respondent waived. This is the strongest signal on the docket: some
  chambers thought the petition worth a look. A called-for response on a paid
  petition historically moves grant odds up materially — though most
  called-for petitions are still denied. The sal-v4 band as frozen
  apparently does not encode the call for response, so I adjust above the
  band rate rather than treat it as already priced.
- Elite Supreme Court counsel; a State amicus (South Carolina) supporting
  petitioners, framing it as a sovereign-against-sovereign dispute; a
  companion petition from the Fifth Circuit is forecast, and the Court
  sometimes waits for two vehicles.
- The QP touches federalism themes (*Ross*, *Mallory*) members of the Court
  have engaged with recently.

**Adjustments down.**
- The claimed split looks soft. The Third, Fifth and Seventh Circuits line up;
  the contrary authority is a 2005/2007 Fourth Circuit line and a 1989 Tenth
  Circuit case, each resting on a predominant federal regulatory interest. A
  BIO can plausibly recast this as fact-bound application of *NOPSI*.
- Vehicle: parallel Pennsylvania administrative/Commonwealth Court
  proceedings are ongoing (the petition cites an April 2026 Commonwealth Court
  decision), so the federal defenses are not foreclosed, and further state
  developments could complicate review.
- Abstention questions are rarely granted absent a deep, acknowledged split.

Net: ~9%. Main uncertainty is the BIO's content and whether the *TMX FCS*
petition arrives in time to be considered together.

**Claims.** relist-increment 0.95 — the requested response virtually
guarantees a fresh distribution once filed (residual risk: withdrawal or
settlement). cvsg-increment 0.02 — no federal interest. summary route |
grant 0.05. dissent-from-denial | denial 0.05.

**Retrieval.** One CourtListener docket search for the companion *TMX FCS*
litigation found only district-court dockets (no SCOTUS docket surfaced).
A corpus `fedcourts query` attempt failed on a wrong flag and I did not
retry; no priors were used. Nothing surfaced about this petition's
disposition.
