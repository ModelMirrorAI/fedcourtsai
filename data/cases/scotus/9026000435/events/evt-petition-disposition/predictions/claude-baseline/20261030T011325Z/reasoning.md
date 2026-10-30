# Rationale — P(grant family) = 0.04

**Inputs read.** I read the snapshot `record/snapshots/2026-10-30.json` and the
provisioned `petition.txt` (61 pages, not truncated, not OCR) with its
`questions-presented.txt`. No brief in opposition exists, because the federal
respondent waived on Oct 23, 2026. `context.json` says forward mode, band
`baseline` (sal-v4), distribution_count 1, no CVSG, and Term 2026.

**Anchor.** I took the `baseline` band's bracketed `reached` rate from the
statpack's sal-v4 segment table. Pooled over OT2017–OT2025, it is roughly 5%
(about 4–6% per Term, each n ≈ 1,200–1,700). OT2026 is excluded because it is my
own Term. That rate covers every petition that ever reached the weakest band,
including those that later relisted or drew CVSGs. The relist-0 bucket
(granted plus GVR ≈ 1.8%) is the floor for petitions that end without a relist.

**Adjustments.**
- Down: the federal respondent waived its response, and the Court has not yet
  called for one. Most paid petitions in that posture are denied at their first
  conference. The decision below is an unpublished summary order. QP 1's
  "split" sets that order against a 2002 Eighth Circuit en banc decision on
  similar facts, which is fact-bound, and the Court rarely grants to correct
  how a statutory definition was applied to a particular workforce. The
  petition is also thinly argued (e.g., it cites § 157 as "§ 57").
- Up: the summary order, quoted in the petition (App. 3), states that the
  Board's legal conclusions get "considerable deference" under longstanding
  precedent. That is facially in tension with *Loper Bright*, and the Court
  GVR'd *Hospital Menonita* on the same ground in 2024. The petition also cites
  the Second Circuit's later published *Siren Retail* (Sept. 2026) disclaiming
  deference to the Board, which makes the error look panel-specific. That
  could motivate a GVR. It also cuts against review, because the circuit has
  already corrected itself. A call for a response, followed by a GVR if the SG
  confesses the standard-of-review error, is the main grant path.

I net these to 0.04, just under the band anchor. Positive-signal rates are much
higher (relist 1+ ≈ 14–40% grant family, CVSG ≈ 35%), and none of those signals
is present.

**Increments.** relist-increment 0.15: mostly a call for a response leading to
redistribution, plus a small chance of a reschedule. cvsg-increment 0.003: the
United States is the respondent, so a CVSG is structurally near-impossible.
summary-disposition-route 0.7 given a grant, because a GVR is the natural
remedy the petition itself requests. dissent-from-denial 0.02.

**Uncertainty.** I have not read the Second Circuit's order (App. 1a–13a) in
full. I don't know whether it also held that substantial evidence supports the
Board's findings under any standard, which would make a deference error
harmless and lower the GVR odds. Corpus priors were uninformative for this
question. MCP retrieval was not used.
