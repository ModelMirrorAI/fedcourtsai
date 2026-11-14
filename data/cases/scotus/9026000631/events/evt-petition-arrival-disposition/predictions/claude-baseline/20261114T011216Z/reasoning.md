# Reasoning — Robison v. Collins, No. 26-631 (arrival cell)

**P(grant) = 0.007; predicted disposition: denied.**

## What I read
- Snapshot `2026-11-14.json`: paid petition filed Nov 11 2026, docketed Nov 13; one docket entry (petition filed, response due Dec 14 2026). No distribution, no response, no amici — the arrival state by definition.
- `questions-presented.txt` and `petition.txt` (43 pages with appendix; the argument section is about six pages).
- `decision-below.txt`: a nonprecedential Federal Circuit per curiam (Lourie, Hughes, Stoll), June 2 2026, checked against the petition's description — it is the judgment the petition challenges. `lower-court-docket.txt` adds nothing on rehearing (CourtListener's entries stop before the Aug 13 2026 denial); the petition itself says rehearing en banc was denied, with no dissent mentioned.
- `same-question.json`: empty list — no similar pending or granted petition, so no hold theory.
- `context.json`: forward mode, band `baseline`, sal-v8, `cert_anchor.rate` 0.0517.

## Anchor
Private petitioner against a federal officer as respondent: caption class is private, so the floor is `baseline`'s bracketed reached rate. The frozen `cert_anchor` is 5.2% (pooled prior Terms; the sal-v8 table rows run roughly 4.1%–6.0% reached per Term). That is the rate for every paid private petition at arrival, including those that later relist or draw a CVSG.

## Why far below the anchor
1. **Vehicle defect.** The Federal Circuit did not decide the question presented; it dismissed for lack of jurisdiction under 38 U.S.C. § 7292(d)(2), reasoning that the petitioner conceded Haines and Crews control and so was only challenging application of law to fact. The Court would have to get past that jurisdictional ruling (which the petition addresses in about a page) before reaching the statutory question.
2. **No split, and none possible.** The Federal Circuit has exclusive jurisdiction over Veterans Court appeals. The petition claims only importance, not a conflict.
3. **The Court has declined this question before.** The petition itself says cert was denied in Haines (1999) and Crews (2023) and that it adopts those petitions' arguments. No intervening change in law is identified; the panel's footnote notes the same.
4. **Unpublished, per curiam, no dissent, en banc denied.**
5. **Thin petition.** Short argument, no specialist Supreme Court counsel, no amici at filing. The Solicitor General will likely waive a response; a call for a response is the only realistic path to any further attention.
6. **Statutory text is unfavourable.** § 5109A(c) limits CUE requests to "the claimant", which is the basis of Haines.

Slight upward considerations: veterans cases get occasional interest (the pro-veteran canon debate, Justices Gorsuch/Sotomayor/Jackson), and the cafc originating-court cut shows a somewhat above-average grant rate (granted 3.1%, gvr 1.6%, n=884 resolved) — but that is driven by patent cases. These keep me above zero, not near the anchor.

Net: about one-seventh of the anchor, 0.7%.

## Other claims
- `relist-increment` 0.96: the frozen distribution count is 0, so any distribution for conference resolves this true; only a pre-distribution withdrawal/dismissal (e.g. Rule 46) avoids it. I read the claim as "count rises above the frozen zero"; if the harness means a true relist, this number is far too high (I would say ~0.02).
- `cvsg-increment` 0.002: the United States is already the respondent; a CVSG is essentially unavailable.
- `summary-disposition-route` 0.40 (conditional on grant): a grant here would most plausibly come via a GVR after some intervening decision or SG confession on the jurisdictional ground; plenary review is the other path. Weakly held.
- `dissent-from-denial` 0.008 and `order-writers`: small; Gorsuch, Sotomayor and Jackson marginally likelier given past interest in veterans' claims.

## Retrieval and limits
One corpus query (generic denied-petition priors; not informative for this case) and the committed statpack. No CourtListener MCP or web calls. I did not verify the Haines/Crews cert denials independently; they are the petitioner's own account against interest, so I rely on them. No outcome information surfaced.
