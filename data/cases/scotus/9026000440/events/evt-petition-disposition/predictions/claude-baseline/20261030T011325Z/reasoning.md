# Reasoning — P(grant) = 0.025

**Inputs read.** Snapshot `2026-10-30.json` (one distribution, for the 13 Nov
2026 conference; US waiver filed 21 Oct 2026; two extensions granted by Justice
Alito under 26A102). From `record/documents/` I read `questions-presented.txt`,
the petition (the reasons section in full) and the relitigation-bar passages of
the appendix (CA3's non-precedential 2026 opinion). No BIO exists because the
government waived its response. Context: `band: baseline` (sal-v4),
`distribution_count: 1`, forward mode, paid docket.

**Anchor.** In the statpack's sal-v4 "Segment base rate by salience band" table,
the `baseline` column's bracketed `reached` rate over OT2017–OT2025 sits
between 4.0% and 5.9% per Term. Pooled, it comes to about 5%. That figure
includes every petition that started in the baseline band and later climbed
through a response call, a relist or amicus support. The paid relist-0 bucket
(1.3% grant, 0.5% GVR) is the end state if nothing more happens, and it
understates a live petition's prospects.

**Adjustments down from ~5%.**
- The government waived. A grant almost always needs a called-for response
  first, so the realistic path is response call (my estimate ~12–15%) times
  grant-family conditional on that (~15–20%).
- The petition pleads no circuit split. It asks for error correction and says
  so, opening with a summary-reversal request. Summary-reversal asks from
  criminal defendants are rarely granted.
- This is a second trip: cert on the direct appeal was denied in 2021 (No.
  20-1369). The 2255 opinion below is non-precedential, and the petitioner is
  serving an immigration-fraud sentence tied to Liberian civil-war conduct, so
  the record is unsympathetic.

**Adjustments up.** The legal hook is real. The direct-appeal panel accepted
that the conduct fell outside the charged statute's text, yet the 2255 court
held the relitigation bar forecloses relief. That sits awkwardly with *Davis*
(1974) and the actual-innocence gateway in *Bousley*. The petition also says
the government waived procedural default below. Counsel is an experienced
criminal appellate lawyer. These points keep me above the relist-0 floor.

Net: about 2.5%, about half the band's reached rate, because the waiver and
the absence of a split mean the petition needs two unlikely steps.

**Other claims.** Relist-increment 0.15 tracks P(response called) plus
reschedule noise. CVSG 0.003, since the US is already the party. The summary
route conditional on a grant is 0.45, because the likeliest grant is a GVR or
summary vacatur after a confession of error. Dissent-from-denial 0.04: a
statement is conceivable from Gorsuch, Sotomayor or Jackson, but most denials
of waived petitions draw nothing. Order-writer numbers sum to roughly that.

**Uncertainty.** I did not verify the petition's characterization of the 2020
direct-appeal holding against the full opinion. The pipeline cut it in the
appendix, and I read only the relitigation-bar portion. If the panel's
"not a crime" statement was really an assumption rather than a holding, the
petition is weaker still. The docket-number lookup of the 2021 petition through
`fedcourts query` returned nothing usable, so that history is taken from the
petition's related-proceedings list.

**Stakes.** big_case_score 0.12: a narrow collateral-review question in one
case, with no split pleaded.
