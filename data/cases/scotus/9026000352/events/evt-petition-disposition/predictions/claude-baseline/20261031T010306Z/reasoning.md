# Reasoning — scotus/9026000352 (No. 26-352, Wray v. RTX Corporation)

**P(grant) = 0.003; predicted disposition: denied.**

## Inputs read
- Snapshot `record/snapshots/2026-10-31.json`: paid petition filed Sep 11 2026 (docketed Sep 16), response due Oct 16, 2026; no response, waiver, or call for response on the docket; **DISTRIBUTED for Conference of 11/13/2026** (one distribution, no relist, no CVSG). The petitioner is pro se; the respondent has counsel below (Smith Anderson, Raleigh), but no Supreme Court appearance is recorded.
- `record/context.json`: forward mode, band `baseline` (sal-v4), distribution_count 1, `cert_anchor.rate` = 0.0509 (pooled reached rate over 10 prior Terms).
- `record/documents/questions-presented.txt`, `petition.txt`, `appendix.txt` (none empty, none OCR-derived). `same-question.json`: no matching petitions.

## Anchor and adjustments
- Anchor: the baseline band's reached rate of ~5.1%. That figure covers the whole paid baseline segment, which includes counseled petitions with real splits.
- Adjustments down (large):
  - The petitioner is pro se, and the questions presented are abstract and non-justiciable as framed. QP1 asks in general terms whether whistleblower laws bind businesses with foreign ties. QP2 asks what actions a retired servicemember may take when the "federal government is compromised by a foreign adversary." Neither question identifies a statute, a holding below, or a legal error.
  - The decision below is an unpublished, two-paragraph Fourth Circuit per curiam ("find no reversible error"), affirming a W.D.N.C. Rule 12 dismissal of a complaint that the district court called "difficult to parse."
  - The "conflict" section of the petition is not a circuit split on a defined question. Most of the "reasons" section describes allegations against unrelated companies.
  - The petition was distributed with no response requested. In practice this means the Court treats it as a routine denial candidate.
- The relist-count cut (paid scored segment) shows a 1.3% grant and 0.5% GVR rate for relist-0 petitions, and this petition is at the bottom of that population. Petitions of this profile are granted essentially never, so 0.3% is mainly a floor for tail risk.

## Claims
- relist-increment 0.03: a relist would need a call for response, or a reschedule. Both are rare for a pro se filing of this kind.
- cvsg-increment 0.002.
- summary-disposition-route 0.3: this is a conditional number. In the near-impossible world where the Court grants, a GVR or summary route is somewhat more plausible than plenary review, but no intervening decision bears on the case.
- dissent-from-denial 0.003: I see no plausible hook for a separate writing.

## Uncertainty
The respondent's waiver is not shown on the docket, but this does not matter. Retrieval was limited to one corpus query, which returned similar pro se paid denials, plus the committed statpack. I did not need the CourtListener MCP server.
