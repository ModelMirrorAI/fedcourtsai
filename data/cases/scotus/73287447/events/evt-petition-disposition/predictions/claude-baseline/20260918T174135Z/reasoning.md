# Reasoning: why P(grant) = 0.13

## Inputs read

- Snapshot `record/snapshots/2026-09-17.json` (supremecourt.gov docket 25-1243, `sJsonCreationDate` 09/09/2026): paid petition, docketed May 1, 2026, from CA2 (No. 24-981, decided Dec 16, 2025, rehearing denied Jan 28, 2026). Respondent waived (Jun 1); distributed for the 6/25 conference (Jun 9); **Response Requested** (Jun 23); extension granted to Aug 21; BIO filed Aug 21; reply Sep 4; distributed for the 9/28/2026 long conference (Sep 9). No amicus briefs on the docket.
- `record/context.json`: `mode: forward`, `band: elevated` under `sal-v4`, `distribution_count: 2`, `cvsg_date: null`, `term: 2025`, `signals_observable: true`, `cutoff: null`.
- `record/documents/`: `questions-presented.txt`, `petition.txt` (40 pp.) and `brief-in-opposition.txt` (36 pp.), all with text, none truncated. I read both briefs in full.
- `metrics/statpack.md`: the modern-cert disposition section, the relist-count and CVSG cuts, the by-Term table and the sal-v4 segment base rate by salience band.

## Anchor

The frozen band is `elevated` under `sal-v4`, and the statpack's band table is headed `sal-v4`, so the table is my anchor. Pooling the bracketed `reached` figures for `elevated` over Terms strictly before this case's own (OT2017–OT2024, every prior row the table renders) gives 484.4 / 2810 ≈ **0.172**. The three most recent Terms alone pool to 0.181. That is the yardstick the evaluator will score against, and I start there.

## Adjustments down

- **Interlocutory posture.** The Second Circuit reversed a dismissal; the case is back in the district court in discovery (the BIO says so, and notes the district court has since rejected petitioners' remaining dismissal arguments). The Court strongly prefers to wait for final judgment, and the petition does not confront this vehicle problem.
- **The split is contestable, and the BIO's answer is strong.** The petition frames a 2-1 split with City of Oakland (CA9) and Montreal Trading (CA10). But both of those opinions expressly disclaimed a bright-line rule against non-purchaser standing and named a prior course of dealing as the fact that could change the result — exactly the fact the Second Circuit relied on. The petition's rule (non-purchasers categorically lack standing) is one no circuit has adopted, and the "circuit split" collapses into a disagreement about applying a shared multi-factor test to unusual facts (sole-target conspiracy, existing three-year contracts, no more direct victim). The Court is unlikely to see a clean conflict.
- **The United States is already on the respondent's side of the doctrine.** The DOJ Antitrust Division's July 24, 2024 amicus brief in the Second Circuit (in support of neither party) argued that non-purchaser status is not a categorical bar and that a prior course of dealing can make a non-purchaser an efficient enforcer. A CVSG would very likely return a recommendation to deny, and the Justices know that.
- **No amicus support at the cert stage.** For a petition claiming sweeping consequences for antitrust defendants across industries, the absence of any amicus (no Chamber of Commerce, no broadcaster trade group) is a notable signal that the bar does not see the decision as the floodgates the petition describes.
- **Fact-bound merits section.** The petition's argument that the decision is wrong is mostly an argument that DirecTV's allegations are too thin, which the Court reads as error correction.

## Adjustments up

- **Response requested after a waiver.** At least one chambers wanted to see an opposition; that is a genuine screening signal beyond mere distribution and it is the reason the band is elevated rather than baseline. (The band already prices this in, so I do not double-count it heavily.)
- **Published split-panel decision with a substantial dissent** (Judge Sullivan) on a question the Court has not addressed since AGC in 1983, in a circuit that handles a large share of antitrust litigation. The Court has shown appetite for antitrust-standing questions (Apple v. Pepper).
- **Sophisticated counsel** on both sides (Covington, Wiley, Venable for petitioners; King & Spalding for respondent), so the petition is well presented.

## Net

Starting from ≈0.17, the interlocutory posture, the weakness of the asserted split against a well-argued BIO, the government's known position and the silence of amici together outweigh the response-request and dissent signals. I settle at **0.13** — below the band anchor but well above the paid-docket rate, because the response request is real evidence of interest. My predicted disposition is `denied`.

## Claim numbers

- `disposition` 0.13 (equals `probability`).
- `relist-increment` 0.30, stated from the frozen count of 2. Note the count includes a June distribution that was mooted by the response request, so this is effectively a first-consideration petition; see `flags.json`. The number bundles grant-after-relist (≈0.11), a CVSG path (≈0.12, which redistributes after the SG's brief) and a small relist-then-deny share, with overlap between the first two.
- `cvsg-increment` 0.12: the Court CVSGs private antitrust petitions at a meaningful rate, and the existing DOJ brief predates the current administration, which is a reason to ask again; the interlocutory, low-percolation posture is the reason not to.
- `summary-disposition-route` 0.04 (conditional on grant): no GVR hook, no summary-reversal shape.
- `dissent-from-denial` 0.06 (conditional on denial): business antitrust denials rarely draw writings.

## Retrieval and its limits

Forward cell, so retrieval was unrestricted. The `fedcourts query` corpus surface cannot filter SCOTUS rows by subject, so the priors it returned (recent granted and denied SCOTUS dockets, mostly emergency applications) were not comparable and did not move the number; I used the statpack, not the query results, for base rates. CourtListener holds no docket entries for this docket (0 rows) and no docket for the related United Biologics v. Amerigroup petition (No. 25-1388, a Sixth Circuit indirect-purchaser case the BIO cites), so I could not check either beyond the snapshot; the web search confirmed the United Biologics petition exists but turns on the Illinois Brick indirect-purchaser rule, not non-purchaser standing, so I do not treat it as a hold candidate. The DOJ brief's date and signatories came from a local text extraction of the PDF fetched from justice.gov. The web search surfaced only pre-snapshot trade-press coverage of the petition and the BIO; no disposition exists (conference is 9/28/2026).

## Where to discount me

I am most uncertain about how the Court weighs a response request that follows a waiver: if it reflects a Justice actively interested in reining in antitrust standing, my number is too low by several points. I am also reading the split's weakness from the BIO's characterization of City of Oakland and Montreal Trading rather than from those opinions themselves, though the petition's own quotations of Montreal Trading ("at least when they lack a past course of dealing") corroborate the BIO's reading.
