# Rationale: P(grant) = 0.012

**Inputs read.** Snapshot `record/snapshots/2026-10-31.json`, `record/context.json`, `record/documents/questions-presented.txt`, `petition.txt` (57 pages, not truncated, not OCR), and `same-question.json` (empty: no petition scored above the 0.5 threshold). No BIO was filed because the SG waived. No related dockets.

**Anchor.** Context gives band `baseline` (sal-v6) and `cert_anchor.rate` = 0.0519, the pooled `reached` rate for the baseline band over the prior 10 Terms. That figure covers every paid petition that ever reached the baseline band, including the ones that later relisted or drew CVSGs. This petition sits at the bottom of that population: one distribution, the response waived, no call for a response. The statpack's relist-0 bucket shows about 1.3% granted plus 0.5% GVR for petitions that were never relisted. The leading (terminal) baseline figure is about 1.2–2.0% per Term.

**Why I moved below the anchor:**
- **The SG waived.** When the federal government waives a response to a paid petition and the Court does not call for one, the petition is almost always denied. A grant without a response is extremely rare.
- **Vehicle problems.** He's own claim was disposed of by an *unpublished summary affirmance* (January 15, 2025). The D.C. Circuit's published opinion (179 F.4th 8) actually *reversed* in the family's favor on their assault claims and remanded, so part of the case is ongoing. He chose not to seek a FECA coverage determination from Labor, so the record contains no agency ruling on coverage. The jurisdiction statement leans on the later June 2026 judgment to make the petition timely against the January 2025 order, which the government could contest.
- **The split is old and shallow.** It is 9th Circuit (*Figueroa* 1993, *Moe* 2003) against everyone else, and the petition's argument section is about four pages long. It cites one circuit-case quote (*Mathirampuzha*) that is missing from the table of authorities. The Court has left this split alone for decades.
- **Counsel.** A small-firm practitioner, not a Supreme Court specialist.

**Why I did not go lower.** The split is real and recurring, and FECA preclusion affects many federal employees. A Justice could call for a response.

**Increments.** relist-increment 0.06 (mostly the chance of a call for response, plus a small chance of rescheduling). cvsg-increment 0.002 (the federal government is a party). summary-route given grant 0.15. dissent-from-denial 0.015.

**Uncertainty and retrieval.** No external retrieval beyond one structured corpus query (used for format only; it did not inform the number). I did not consult the live supremecourt.gov docket. My first-conference timing assumes nothing changed after the October 21 distribution.
