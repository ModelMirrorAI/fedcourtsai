# Why P(grant) = 0.17

**Anchor.** `context.json` freezes band `baseline` (sal-v4) with one distribution. In the statpack's "Segment base rate by salience band (sal-v4)" table, the bracketed `reached` figure for `baseline` over OT2017–OT2025 runs 4.0%–5.9% (n ≈ 1,200–1,700 per Term), so roughly 5% pooled. OT2026's own row (1.8%, n=169) is my own Term and immature, so I set it aside.

**The called-for response.** No committed table conditions on this moment, so how far the call moves me is my judgement. A response request is a low bar: one Justice or a clerk flags the petition. Most such petitions are still denied. I treat the call as roughly doubling the baseline, to about 10%.

**Adjustments up:**
- The QP repeats a question the Court has granted twice: *Tyson Foods* and *Labcorp v. Davis* (24-304, DIG'd in 2025). The petition (pp. 2–4, 15–20) argues the split has deepened since then.
- Justice Kavanaugh's *Labcorp* dissent says the Ninth Circuit's rule is wrong and consequential.
- The vehicle pitch is clean: an interlocutory Rule 23(f) appeal with district-court proceedings stayed, which avoids the post-judgment and mootness problems that sank *Tyson* and *Labcorp*.
- The snapshot lists counsel for the Chamber of Commerce (with ATRA and Business Roundtable) and for the Retail Litigation Center. The live docket shows both amicus briefs filed on 2026-10-05. In the statpack's amicus cut, the 2+ bucket grants about 18% (n=1,543), against 2% for 0. That cut is marginal and not additive to the band, but it points the same way.

**Adjustments down:**
- The petition itself says the Court denied cert in 2026 in *Painters v. Takeda*, another Ninth Circuit uninjured-class case. That is a recent sign the Court isn't eager to take just any vehicle on this question. Petitioner distinguishes it: there, class members had at least a 98.5% chance of injury, while here 1,275 members got refunds.
- The Ninth Circuit memorandum is unpublished.
- The stakes are 10-cent deposits plus Oregon statutory damages.
- The "uninjured" theory turns on refunds paid before suit. Respondents can recast that as a merits or damages question rather than standing, which is a vehicle risk I can't assess without the BIO.
- Eight Justices joined the *Labcorp* DIG. That turned on posture, but it shows no rush.

Net: about 0.17. My main uncertainty is whether the Court is waiting for a better-capitalized vehicle, possibly another pending petition on this question that I couldn't locate. That case would push this petition toward a hold and GVR rather than a plenary grant.

**Other claims.**
- `relist-increment` 0.97: masked on this moment; it is near-certain anyway.
- `cvsg-increment` 0.03: private dispute.
- `summary-disposition-route` 0.12: the hold-then-GVR path.
- `dissent-from-denial` 0.11: Kavanaugh is the likely writer, which is consistent with `order-writers`.

**Inputs used.**
- Snapshot `2026-09-04.json`.
- `petition.txt`, `appendix.txt` and `questions-presented.txt`, all with text and none OCR-derived. I read the petition's introduction and vehicle sections and skimmed the appendix only through the petition's citations to it.
- The live supremecourt.gov docket, read in forward mode. It shows the petition still pending, two extensions of the response deadline (now 2026-12-04) and two amicus briefs. Nothing on it discloses a disposition.

I know *Labcorp*'s outcome from training. It is public pre-snapshot context, not this case's outcome.
