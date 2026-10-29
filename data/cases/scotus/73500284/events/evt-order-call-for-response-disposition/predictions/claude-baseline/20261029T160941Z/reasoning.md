# Why P(grant) = 0.27

**Anchor.** `context.json` freezes band `baseline` under `sal-v4`, which matches the statpack table's heading. The table's bracketed `reached` rate for `baseline`, over Terms strictly before 2025 (2017–2024), is about 4.5–5.9%, pooling near 5.3%. That is the yardstick this cell is scored against.

**The call for response.** The prompt notes that no committed table conditions on a called-for response. My judgement is that a call after a waiver roughly doubles or triples the paid-petition rate, to about 10–15%. Most such petitions are still denied.

**Adjustments up:**
- The QP states a question the Court expressly reserved in *GE Energy v. Outokumpu*, 590 U.S. 432, 445 (2020). The petitioner claims a 4–1 split (First, Second, Fourth and Ninth Circuits against the Fifth). The reply says 4–2, counting the Seventh Circuit with the Fifth.
- The Fifth Circuit denied rehearing en banc. The petition says the choice of law decided the outcome, and cites the Fifth Circuit's own *Bufkin* decision as a near-identical case that came out the other way under federal law.
- Counsel is elite (Skadden, Dvoretzky). Two amicus briefs filed on the same 9/28 distribution: APCIA and a group of international-arbitration scholars. The statpack's amicus cut puts the 2+ bucket at 18.4% granted plus 4.5% GVR (n≈1449 resolved), against 2.0% for 0 amici.
- The issue recurs: hurricane-claim litigation over surplus-lines policies in Louisiana and other coastal states.

**Adjustments down, from the brief in opposition** (read live from supremecourt.gov; it is not in the provisioned documents):
- It argues the split is illusory. The four cited decisions were truly international disputes, and three predate *Arthur Andersen* and/or *GE Energy*.
- It argues the vehicle is poor: domestic parties only, insurance (a McCarran-Ferguson-flavored state interest), and plaintiffs that are Louisiana public entities. It also says estoppel fails even under federal common law, so the answer would not matter. That last point is the strongest vehicle objection, although the petitioners' *Bufkin* argument cuts against it.
- It argues the merits are straightforward under *Arthur Andersen* plus § 208.

These are respectable arguments that could peel off votes. The split's age and the pre-*Arthur Andersen* cases are real weaknesses.

**CVSG.** A meaningful share of the probability mass sits on a CVSG, which would delay the outcome. I set `cvsg-increment` at 0.20. Holding that aside, I land at 0.27 for an eventual grant. This is above the amicus 2+ bucket because the QP is the reserved *GE Energy* question with an acknowledged split, and below a coin flip because of the BIO's vehicle points.

**Inputs.**
- I read the snapshot `2026-07-27.json`, `questions-presented.txt`, `petition.txt` (reasons for granting, split and vehicle sections) and `appendix.txt` (TOC and the en banc denial).
- None of the documents is OCR-derived or empty.
- The BIO and reply are not provisioned. I fetched them from the Court's docket as forward-mode retrieval. I read only the BIO's table of contents and summary of argument, and the reply's headings.
- The case summaries under `summaries/` were not read.
- No outcome is known to me. The live docket confirms the petition is pending (distributed for 11/6/2026).

**Uncertainty.** The main uncertainty is how much weight the Court gives the "split is stale or not squarely presented" argument. If the Court thinks the government's view matters, the CVSG path is live.
