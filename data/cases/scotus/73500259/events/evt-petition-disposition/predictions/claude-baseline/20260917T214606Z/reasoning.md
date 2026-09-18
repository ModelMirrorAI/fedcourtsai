# Reasoning — why 0.18

## Inputs read

Snapshot `record/snapshots/2026-09-16.json` (the file `context.json` names); `record/context.json` (forward mode, band `elevated` under sal-v4, distribution_count 2, no CVSG, Term 2025, cutoff null); `record/documents/questions-presented.txt`, `petition.txt` (38 pp.), and `brief-in-opposition.txt` (36 pp.), all with `empty_text: false` and untruncated; `metrics/statpack.md`. Beyond the provisioned inputs I ran two corpus queries, three CourtListener MCP calls, and three web searches (see `retrieval.md`). No web result disclosed a disposition; the petition is set for the September 28, 2026 conference, eleven days after this run.

## Anchor

The band is `elevated` under sal-v4, which matches the statpack's segment table heading, so the table is the anchor. Pooling the bracketed `reached` rate over every rendered Term strictly before OT2025 (OT2017 through OT2024, eight rows, n = 2,810 weighted resolved) gives **17.2%**. The terminal `elevated` figure pooled the same way is 10.5%, but this cell carries a frozen band and is scored against the reached rate, so 17.2% is the yardstick.

For shape only: the paid-segment relist cut shows one relist at 8.2% granted plus 5.1% GVR, two relists at 27.8% plus 13.1%; the CVSG cut shows 29.4% granted plus 5.5% GVR after a CVSG versus 4.0% plus 2.3% without; ca9 petitions grant at 2.1% plus 1.1% GVR overall.

## Adjustments

**Down: the band overstates this petition's trajectory.** The two distributions are not a relist. The first (June 9, for June 25) was superseded by the June 15 call for response; the second (August 5) is the first real conference. The statpack itself warns that a reschedule before first consideration inflates the count. A genuinely once-relisted paid petition sits near the 8 to 13% terminal range; this petition is, in trajectory terms, at its first conference. I flag this in `flags.json`.

**Up: a call for response after a waiver.** Seagate waived on June 8 and the Court called for a response a week later. That is at least one chambers deciding the petition could not be denied on the papers, and it is not a band feature under sal-v4 (the bands read the distribution count and CVSG date). Roughly, these two adjustments offset, leaving me near the anchor.

**Up, case-specific.** The Ninth Circuit opinion is published, unanimous (Callahan, Lee, Rash by designation; Lee writing), rehearing denied, and it expressly says the Seventh Circuit in Motorola "did not substantially grapple with the FTAIA's language." That is the Court's preferred kind of split: acknowledged by the lower court itself. Petitioner's counsel (Paul Hastings, Benjamin Snyder as counsel of record) is experienced Supreme Court counsel, an amicus filed at the cert stage, and the question is a federal-statute extraterritoriality question of the sort this Court has taken repeatedly in other statutes (RJR Nabisco, Abitron, Yegiazaryan).

**Down, case-specific, and this is where most of my weight goes.** The BIO's vehicle arguments are substantial. First, the QP as written is contestable: the Ninth Circuit did not adopt a situs-of-negotiations rule, and it rejected Seagate's broader "conduct in America suffices" argument in a footnote, so the Court would have to reformulate to grant. Second, the posture is interlocutory: the panel remanded the proximate-cause question as a factual matter, remanded the domestic plaintiff's Illinois Brick control-exception claim (which would make the FTAIA irrelevant to a large share of the commerce), and left the import-effects exception unreached. Third, the split is softer than the petition says: Motorola's causation theory ran the other direction (finished-goods prices as the domestic effect), and the Ninth Circuit distinguished it on that ground; the Court can plausibly read the two as consistent applications of Empagran's "independent foreign harm" rule. Fourth, the Court's record on FTAIA petitions since Empagran (2004) is one of denial, Motorola itself included. Fifth, the "unique facts" framing in the panel opinion makes the case look like a one-off. The guilty plea and the civil-remedies-in-lieu-of-restitution point are equities the BIO leans on; I give them little weight in the grant calculus but they do make a summary reversal or a dissent from denial less likely.

## Path arithmetic

I think of the disposition as two paths. If the Court calls for the SG's views (0.22), the conditional grant probability is about 0.35, near the statpack's CVSG cut (29.4% plus 5.5% GVR). If it does not (0.78), the petition either grants directly after a relist or is denied, and I put the direct-grant probability at about 0.13, a little below the anchor for the vehicle reasons above. Blended: 0.22 × 0.35 + 0.78 × 0.13 ≈ 0.18.

## Other claims

- `relist-increment` 0.42: every CVSG and almost every grant implies a further distribution, plus a relist-or-reschedule-then-deny tail I put near 0.10 to 0.12 for a paid, CFR'd long-conference petition.
- `cvsg-increment` 0.22: high relative to the 1.2% population rate because the statute is a direct federal enforcement interest and the DOJ prosecuted this cartel; held below 0.3 because the Court passed on Motorola without asking.
- `summary-disposition-route` 0.04: no intervening decision; a grant is plenary.
- `dissent-from-denial` 0.06: no obvious writer; interlocutory posture gives cover to wait.
- `big_case_score` 0.45: a real question about the reach of U.S. antitrust law over global supply chains, but technical and business-facing.

## Uncertainty and where to discount me

The two largest uncertainties are the CVSG probability (the case for and against is nearly balanced, and it swings the grant number by several points) and how much the Court credits the BIO's "QP not presented" argument, which I cannot test against the full Ninth Circuit opinion beyond its summary and the parties' quotations. The corpus queries returned no subject-matched priors (the Empagran citation lookup was empty for coverage reasons), so my sense of the Court's FTAIA denial record comes from general knowledge, not the corpus. I hold no outcome knowledge: the conference has not happened.
