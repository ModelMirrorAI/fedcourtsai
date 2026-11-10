# Reasoning — scotus/9026000355 (No. 26-355, del Rio v. CrowdStrike), evt-petition-disposition

**P(grant) = 0.05.**

## Inputs read
- Snapshot `record/snapshots/2026-11-09.json`. This is a paid petition from CA5 (No. 25-50518), docketed Sept. 16, 2026. CrowdStrike waived its response on Oct. 10. The petition was distributed for the Nov. 6, 2026 conference on Oct. 14. On Oct. 19 the Court requested a response, due Nov. 18, 2026. No CVSG, no amici, no related dockets.
- `record/context.json`: forward mode, band `baseline` (sal-v8), distribution_count 1, `cert_anchor.rate` = 0.0516 (the baseline band's reached rate, pooled over 10 prior Terms).
- `questions-presented.txt` and `petition.txt`. The question is whether the Airline Deregulation Act's preemption of state claims "related to a … service of an air carrier" covers tort and product-liability claims against a third-party software vendor. The petition argues there is a circuit split: Hodges (CA5 en banc, broad reading) against Charas (CA9 en banc, narrow reading), with other circuits on each side (it places CA3 with CA9 and CA4, CA6 and CA7 with CA5). It also argues that extending preemption to a non-carrier vendor is a new expansion.
- `decision-below.txt`: an unpublished CA5 per curiam (Richman, Duncan, Oldham) reading only "AFFIRMED. See 5th Cir. R. 47.6", i.e. no opinion. `lower-court-docket.txt` confirms it is unpublished. Rehearing was denied June 15, 2026.
- No brief in opposition yet; the requested response is not due until Nov. 18. `same-question.json` lists no similar petitions.

## Anchor and adjustments
- I anchored on `cert_anchor.rate` ≈ 5.2%. The statpack's sal-v8 baseline column shows reached rates of about 4.7–6.0% across OT2017–OT2025. Two cross-checks: the paid-segment relist-0/1 cuts, and CA5's overall grant+GVR share of about 3.9%.
- **Up:** the Court asked for a response after a waiver, so at least one chambers looked at the petition. The Hodges/Charas split is real and acknowledged (CA9 in National Federation of the Blind). The CrowdStrike outage is a well-known event.
- **Down:** (1) The vehicle is poor. The judgment below is a Rule 47.6 affirmance with no opinion, so the Court would be reviewing the district court's reasoning, and the summary affirmance suggests CA5 saw the case as controlled by its own precedent. (2) The Court has let the Hodges/Charas split stand for decades. Its later ADA cases (Wolens, Ginsberg) did not resolve it, and it has denied many petitions raising it. (3) The question as framed (claims against a non-carrier vendor) is narrow, and the petition shows no circuit splitting on that particular question. (4) Response requests are common and most of those petitions are still denied.
- Net: about the anchor. The response request and the split roughly cancel the vehicle problem, so I put it at 5%.

## Claims
- relist-increment 0.95: the docket shows 1 distribution, and the response request took the case off the Nov. 6 conference in effect. Once the response and any reply are in, the Court will almost certainly distribute it again.
- cvsg-increment 0.04: private parties, but the federal government has a regulatory interest in ADA preemption (DOT). The Court has occasionally called for the SG's views in ADA preemption cases, but rarely with a vehicle this weak.
- summary-disposition-route 0.08 (conditional on a grant): I know of no intervening decision that would support a GVR, so a grant would almost certainly go to plenary review.
- dissent-from-denial 0.03 (conditional on a denial): unlikely. Gorsuch and Thomas are the most plausible writers on a preemption question.

## Uncertainty and retrieval
I read no brief in opposition, so I don't know whether CrowdStrike will dispute the split or point to vehicle problems (it probably will). My knowledge of the Court's earlier denials on the Hodges/Charas split comes from training memory, not from retrieval. The corpus query was a generic shape check. I made no MCP or web calls.
