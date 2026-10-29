# Reasoning — P(grant) 0.65

**Inputs.** Snapshot `record/snapshots/2026-09-23.json` (cutoff 2026-09-23,
`date` cut, forward mode). `context.json`: band `state` under `sal-v4`,
distribution_count 1, no CVSG, `paper_only_filings: true`, so no
`record/documents/` were staged — expected, not a provisioning gap. Because no
petition text was staged, I identified the question from public sources (the
SCOTUSblog case page and press coverage of the Tenth Circuit decision, Daley v.
Ceja, 158 F.4th 1152); these predate the snapshot or describe the pending
petition and reveal no disposition.

**Anchor.** The frozen band is `state`. Pooling the statpack's sal-v4
"Segment base rate by salience band" `state` bracketed `reached` figures over
Terms 2017–2025 gives roughly 104 grants / 426 ≈ 24%. But the caption is a
federal one: the petitioners are an immigration-detention warden and federal
officials represented by the Solicitor General. The `state` assignment appears
to read "Warden" as a state marker. The `federal` band's pooled reached rate
over the same Terms is roughly 151 / 206 ≈ 73%, which is the population this
petition actually belongs to. I anchor primarily on the federal figure and flag
the band mismatch, since the evaluator will score against the `state` rate.

**Adjustments.**
- Up: a recognized circuit split on a pure question of statutory
  interpretation, a sovereign-immunity waiver (which the Court reads strictly),
  and a high-volume recurring issue with direct fiscal stakes for the
  government — the profile of SG petitions the Court grants.
- Up slightly: the Court itself called for a response (Sept. 22), so at least
  one chamber wants the petition briefed; for an SG petition this is near
  routine, so the signal is weak.
- Down: SG petitions are not granted automatically (federal reached rate is
  ~73%, not ~95%); the respondent will likely argue the split is shallow or
  stale (older authority predating recent detention litigation) or press vehicle
  issues around the fee award; a fee question can look secondary. No relist yet.

Net ≈ 0.65. Main uncertainty: the depth of the split, which I know only from
memory and secondary sources, not from the petition text.

**Claims.** relist-increment 0.97 (masked on this moment; the petition is
redistributed once the response arrives). cvsg-increment 0.01 (the United
States is the petitioner). summary-disposition-route 0.05 conditional on grant.
dissent-from-denial 0.20 conditional on denial — a denied SG petition with a
split draws a written dissent somewhat more often than the ordinary petition.

**Retrieval degradation.** The CourtListener MCP server returned HTTP 429
(daily rate limit), so I could not pull the Tenth Circuit opinion or the
competing circuit decisions; I relied on web sources and the statpack.
