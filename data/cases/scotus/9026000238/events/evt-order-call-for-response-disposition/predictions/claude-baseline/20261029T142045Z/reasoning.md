# Why P(grant) = 0.22

**Inputs read.** The snapshot `2026-09-11.json` (cut at the response-requested day), `context.json` (forward, band `baseline` under sal-v4, distribution_count 1, no CVSG), `questions-presented.txt`, `petition.txt` (read in part: QP, reasons, and the hold section) and `documents.json`. I did not read `appendix.txt` closely. It contains the Second Circuit opinion, so my picture of the panel's reasoning comes from the petition's characterization only. No brief in opposition was provisioned, and none existed at the cutoff.

**Anchor.** Band `baseline`, bracketed `reached` rate over Terms 2017–2025 in the sal-v4 band table. Weighted, this is about 5% (n ≈ 13,200; per Term 4.0–5.9%). That is my yardstick.

**Adjustments up.**
- **A called-for response.** The Court asked for a response after a waiver, so at least one chambers thought the petition merits a look. No committed table conditions on this signal. From general knowledge, petitions with a called-for response are granted several times more often than the paid docket as a whole, though most are still denied. This moves me to roughly the low teens.
- **Elite counsel and organized amicus support.** Lisa Blatt is counsel of record. ASCAP filed an amicus brief before the call, and the live docket shows NMPA/NSAI and Songwriters of North America filing on Oct 13. That makes three amicus entries. The paid-segment amicus cut puts 2+ amicus at 18.4% granted plus 4.5% GVR, against 2.0% plus 1.8% for zero amicus. That is marginal and not additive with the call for a response, but it points the same way.
- **A pending companion.** The petition asks in the alternative for a hold pending *RiseandShine v. PepsiCo* (24-1016). The corpus row shows that case was granted on 2026-06-29 from ca2 after a CVSG, with the United States participating. It is undecided. It is a closely analogous fact/law standard-of-review question from the same circuit, so a hold is likely. A GVR afterward is plausible if *RiseandShine* reasons broadly about labeling factual questions as legal. This hold-then-GVR path is the main reason I sit above the low teens. I put about 0.10 on it.

**Adjustments down.**
- **The split may be thinner than claimed.** The ASCAP/BMI rate courts sit only in S.D.N.Y. under DOJ consent decrees. The other circuits' cases concern condemnation, tax, CRB and other valuation contexts, so the respondent can argue that no other circuit reviews this kind of rate determination at all.
- **Vehicle questions.** The Second Circuit vacated and remanded, which is an interlocutory posture. The respondent will likely say the question is fact-bound.
- **The base rate.** Even for petitions with a called-for response, denial is the modal result.

**Net.** Plenary grant ≈ 0.12 plus hold-and-GVR ≈ 0.10, giving ≈ 0.22. `summary-disposition-route` = 0.45 is the GVR share of that grant mass. `relist-increment` is masked on this moment, but I state 0.96 because the petition will be distributed again once the opposition brief is in. `cvsg-increment` = 0.08 reflects the consent-decree federal interest, discounted because the issue is generic. `dissent-from-denial` = 0.04.

**Uncertainty and discounts.** My hold/GVR estimate rests on judgment about how broadly *RiseandShine* will be written, and that case has not been decided. I have not seen the respondent's brief in opposition. The post-cutoff live-docket entries I consulted (the response extended to Nov 2, two more amicus briefs) are ordinary forward-mode information, not outcome information. I did not look at the `summaries/` directory or any coverage of this case's disposition.
