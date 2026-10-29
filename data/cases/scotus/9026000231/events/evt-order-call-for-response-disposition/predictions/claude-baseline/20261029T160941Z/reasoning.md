# Reasoning — P(grant) 0.20

**Inputs read.** Snapshot `record/snapshots/2026-09-05.json` (forward mode; date
cut at 2026-09-05). Documents: `questions-presented.txt` and `petition.txt`, both
with full text. `appendix.txt` is present, but I did not read it in detail. No
brief in opposition is on the record, which is expected: the response is due
October 5. Context: `band: baseline` (sal-v4), `distribution_count: 1`, no CVSG,
Term 2026.

**Anchor.** I used the sal-v4 "Segment base rate by salience band" table,
baseline column, bracketed `reached` figures, pooled over Terms 2017–2025
(strictly before OT2026). Those Terms fall between about 4.0% and 5.9%, with
n ≈ 1,200–1,750 per Term, so the pooled rate is about 5%. The baseline floor is
also the caption-class floor for a private petitioner. The table's version
matches my context's salience_version.

**Adjustments up.**
- *Response requested.* The SG waived on Aug 31, and the Court requested a
  response four days later. That means at least one chambers flagged the
  petition before the first conference. No committed table conditions on this
  signal. From general knowledge, paid petitions with a called-for response are
  granted several times as often as the baseline, though most are still denied.
  This is the largest adjustment, and it is my own judgement.
- *Split and posture.* The petition describes a 2–3 circuit split after Borden
  (9th and 10th vs. 6th, 7th and 11th). It says the government acknowledged the
  split below and did not dispute that the issue decided the case: without the
  battery conviction, ACCA's 15-year minimum does not apply. ACCA
  elements-clause questions are a recurring part of the Court's docket.
- *Counsel.* Lisa Blatt (Williams & Connolly) is counsel of record, with the
  Federal Defender. The snapshot's "Other" block lists NACDL counsel, which
  suggests an amicus filing, but the proceedings in my snapshot show no amicus
  entry yet.

**Adjustments down.**
- The government will very likely oppose. It can say the Ninth Circuit itself
  disclaims having resolved the debate (the petition quotes *Lopez*), so the
  split may be described as shallow or untested.
- The baseline band reflects that the petition has had no relist so far. Even
  with a response requested, most such petitions are denied.

**Net.** About 5% → about 20%. My main uncertainty is how much weight the
response request deserves. My 20% assumes it lifts the odds roughly 3–4x. A
reader should discount the precision accordingly.

**Other claims.** `relist-increment` 0.95: the petition will be redistributed
once the response is in (the harness masks this claim at this moment).
`cvsg-increment` 0.01: the United States is the respondent. Summary route given
a grant 0.05: there is no GVR hook. Dissent from denial given a denial 0.07:
criminal-defendant ACCA petitions sometimes draw a statement, but rarely.
`order-writers` is kept consistent with that figure.

**Retrieval.** Two corpus queries; neither was informative (see retrieval.md). I
made no MCP or web calls and do not know the outcome.
