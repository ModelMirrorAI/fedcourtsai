# Reasoning: P(grant) = 0.012

## What I read
Snapshot `2026-11-16.json`, `context.json`, and the staged `questions-presented.txt`, `petition.txt` (front matter, statement and argument headings; not every page closely), `appendix.txt`, `decision-below.txt` and `lower-court-docket.txt`. No brief in opposition exists: the docket shows no response and no waiver entry, only the petition (filed July 6, docketed September 28, 2026), one amicus brief (October 28), and distribution on November 10 for the December 4 conference. `decision-below.txt` matches the opinion the petition's Appendix A reproduces (4th Cir. No. 26-1130, April 9, 2026), so I relied on it.

## Anchor
`context.json` freezes band `baseline` under `sal-v8` with `cert_anchor.rate` = 0.0517 (reached rate, ten prior Terms). The amicus line (`some` arm, n = 2,315) is 0.163. The statpack's relist-0 bucket of the paid segment grants about 1.8% (granted + gvr, n = 10,284 resolved), and the 1-amicus bucket about 14.8% (n = 1,163).

## Why far below the anchor
- **Pro se petitioner.** The paid-segment base rates are dominated by counselled petitions; self-represented paid petitions are granted far more rarely. The petition is professionally printed but filed by the petitioner herself as successor trustee of a family trust.
- **Decision below.** A three-page unpublished per curiam (Wilkinson, King, Thacker) that construed her Rule 60(b)(4) motion as a request to intervene, found no abuse of discretion in refusing it, and dismissed the rest for lack of nonparty appellate standing because she did not participate in the district court. It applies settled circuit law to her facts. No rehearing en banc petition appears on the lower-court docket record.
- **Questions do not match the ruling.** Both questions (Fifth Amendment due process for a nonparty property owner; the scope of FTC Act Section 13(b)) go to the merits of the district court's redress and sale orders, which the Fourth Circuit never reached. The petition's argument headings assert importance and recurrence, and I found no developed circuit conflict on the threshold issue actually decided. The Section 13(b) question after *AMG Capital* has surface appeal, but the Fourth Circuit already handled that in the main appeals of this FTC action, and this vehicle cannot reach it.
- **No sign of the Court's interest.** No response was called for before distribution. The Solicitor General is listed as counsel for the nominal respondent (the district court) and filed nothing.
- **The amicus brief.** One brief from "Sanctuary Belize Lot Purchasers", by counsel, supports the petition. That is why I am at 1.2% and not lower: it shows other affected owners and a lawyer who thought the issue worth briefing. But the amicus-line rate of 16% describes a population where a brief usually accompanies a counselled petition with a real split, and I weigh it lightly here. I did not read the amicus brief (not staged).

## Other claims
- `relist-increment` 0.05: essentially the chance the Court calls for a response (which forces a redistribution) plus a small chance of a reschedule or relist.
- `cvsg-increment` 0.003: the federal government is already the respondent's counsel.
- `summary-disposition-route` 0.45: conditional on a grant, I see a vacate-and-remand on the threshold ruling as about as likely as argument. This is a judgement call with little to rest on.
- `dissent-from-denial` 0.01 and small `order-writers` numbers: nothing here fits any Justice's known interests strongly enough to draw a writing; Gorsuch and Thomas get slightly more for their interest in agency-enforcement and property due-process questions.

## Uncertainty
The main way I am wrong is if the amicus brief presents a real conflict on nonparty appellate standing or on district-court power over nonparties' property in receiverships, and a Justice asks for a response. Even then a grant is unlikely. My number sits well under the scored anchor on purpose.

## Retrieval
One corpus query returned generic recent grants and did not inform the number; base rates came from `metrics/statpack.md`. No MCP or web retrieval was used.
