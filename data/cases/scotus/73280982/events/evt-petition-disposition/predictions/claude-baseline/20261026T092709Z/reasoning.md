# Reasoning — P(grant) = 0.72

**Inputs read.** Snapshot `record/snapshots/2026-10-26.json`; `context.json`
(forward mode, band `high` under sal-v4, distribution_count 2, CVSG 2026-06-01,
Term 2025); provisioned documents: the petition (truncated around its appendix),
the BIO (Apr 23 2026), the cert reply (May 11 2026), and the SG's invited brief
(Oct 7 2026). The provisioned `questions-presented.txt` is a mis-cut — it holds
part of the petition's "exceptionally important" argument rather than the QP
section — so I took the questions presented from the SG brief's restatement.
The supplemental briefs of Oct 20/21 are on the docket but not provisioned; I
did not read them.

**Anchor.** The salience-band table (sal-v4, matches my context) gives the
`high` band's bracketed `reached` rate for Terms strictly before 2025
(OT2017–OT2024): pooled ≈ 314 grants / 898 ≈ **35%**. The CVSG cut (all Terms,
paid segment) puts the grant family (granted + gvr) at ~35% as well.

**Adjustments.** Neither cut conditions on the SG's recommendation, which is the
single strongest signal at this stage: the SG brief recommends **granting
Question 1** (with a reformulation) and denying Question 2. Historically the
Court follows an SG grant recommendation in a large majority of CVSG cases
(my recollection is roughly 70–80%; no committed table splits the CVSG cut by
recommendation, so this is a remembered figure, not a pack rate). Further
support: experienced petitioner counsel, three amicus filings (including the
Chamber/SIFMA), the SEC's institutional interest, a Ninth Circuit decision with
a dissent (Rawlinson, J.), and a Court that has recently taken Section
10(b)/omissions questions (*Macquarie*).

**Discounts.** The interlocutory posture (Ninth Circuit vacated a motion-to-
dismiss ruling and remanded) — the BIO presses it and the SG answers it, but it
is a real reason the Court sometimes passes; the respondents dispute the split
(the SG concedes the First Circuit comparison is debatable); the SG wants the
question reformulated, which mildly complicates the grant; and the Court has
DIG'd recent securities cases (NVIDIA, Facebook), which may make it vehicle-
cautious. Net: 0.72.

**Claims.** relist-increment 0.60 — the Court rarely grants without a relist,
so the 11/6 conference is likely to produce a further distribution unless it
grants straight away or denies. cvsg-increment 0.01 — vacuous, CVSG already on
the docket. summary-disposition-route 0.04 — no intervening decision; the SG
seeks plenary review. dissent-from-denial 0.08 — denials of SG-backed
business petitions seldom draw writings. `predicted_disposition`
`granted-in-part` reflects my expectation that the grant is limited to Q1.

**Retrieval.** No MCP or corpus retrieval; I relied on the provisioned inputs
and the committed statpack. Main uncertainty: how much the interlocutory
posture and the reformulation weigh, and what the unread supplemental briefs say.
