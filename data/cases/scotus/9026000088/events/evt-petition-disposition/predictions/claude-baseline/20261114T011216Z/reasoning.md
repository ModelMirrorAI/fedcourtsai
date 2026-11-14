# Reasoning — Alaska Policy Forum v. Alaska Public Offices Commission (No. 26-88)

**P(grant) = 0.11; call: denied.**

## What I read
- Snapshot `2026-11-14.json` (forward cell, no cutoff), `context.json`, `documents.json`, `questions-presented.txt`, and the body of `petition.txt` through the start of Part II (the file is truncated at the pipeline cap; I did not read the appendix, so my view of the Alaska Supreme Court's opinion is the petitioner's characterization of it). No brief in opposition exists yet: all three respondents waived, the Court requested a response on Aug 31 2026, and the response is due Nov 30 2026 after an extension. `same-question.json` lists no matching petitions; no `related/` directory.

## Anchor
- `context.json` freezes band `baseline` (sal-v8), `distribution_count` 1, no CVSG, and `cert_anchor.rate` = 0.0517. That is the yardstick; I start there.
- Statpack cross-checks (paid scored segment, terminal-state cuts, so shape only): amicus count 2+ resolves about 22.6% grant family (n=1451 resolved); relist bucket 1 about 13.5% (n=2538); no-CVSG about 6.3%.

## Adjustments up
- **Response requested after three waivers.** At least one Justice wanted an answer. The prompt rightly says the bar is low and most such petitions are still denied; I treat it as roughly doubling the baseline-band rate.
- **Sixteen cert-stage amicus briefs** (Chamber of Commerce, FIRE, Cato, AFP Foundation, ACLJ, Republican Governors Association, and others). That is far out in the tail of the 2+ bucket. I discount it heavily, though: these are largely repeat ideological filers who also turned out for earlier donor-disclosure petitions that were denied.
- Experienced specialist counsel (Institute for Free Speech), a First Amendment subject the Court's majority has shown interest in (*AFPF v. Bonta*), and a final state-high-court judgment squarely deciding the federal questions.

## Adjustments down
- **The Court's track record on this exact family of petitions.** From the corpus: *No on E v. Chiu* (23-926, on-communication donor disclosure) denied Oct 2024 after 2 distributions; *Gaspee Project v. Mederos* (21-890) denied Apr 2022 after 3 distributions. Both had substantial amicus support and similar counsel. The petition itself concedes the First and Ninth Circuits uphold on-communication disclosure, and the Court has passed on that question before.
- **Split quality.** QP1/QP2 are framed mainly as conflict with *WRTL II* and *Buckley* (error correction) with a loosely described "splintering" among courts; the claimed circuit conflicts on zero-dollar thresholds and earmarking are older and fact-bound. Three questions presented, a fact-intensive as-applied dispute (four specific communications), and state-law construction layered in (the Alaska court gave a narrowing construction) make it a messier vehicle than the petition says.
- No BIO yet, so I cannot see what vehicle problems the State will raise (the 2020 election is long over; the sanction appears to be a compliance order). I assume a competent opposition will find some.

Net: about twice the frozen anchor, well below the amicus-2+ marginal. 0.11.

## Other claims
- `relist-increment` 0.97: the docket shows one distribution (Conference of 9/28/2026) that was overtaken by the response request. Once the response arrives the petition must be distributed again; only a withdrawal/dismissal before then would prevent it.
- `cvsg-increment` 0.02: state law, no federal party or program directly at stake.
- `summary-disposition-route` 0.10 (given a grant): I know of no pending merits case that would support a GVR; a summary reversal on *WRTL II* grounds is conceivable but unlikely on a 91-page state opinion.
- `dissent-from-denial` 0.10 (given a denial): Thomas, Alito and Gorsuch are the plausible writers given the subject, but the analog denials drew no noted dissent that I am aware of. `order-writers` is kept consistent (Thomas highest).
- `big_case_score` 0.5: real doctrinal stakes for nonprofit issue speech and donor privacy if decided, but not front-page.

## Where to discount me
- I have not read the decision below or any opposition. My recollection of the analog cases' amicus counts and lack of dissents is from memory, not from the record. A single real relist after the response is in would move this number a lot.
- CourtListener MCP was not used; retrieval was the corpus tooling and the statpack only.
