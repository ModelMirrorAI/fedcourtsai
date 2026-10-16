# Rationale — P(grant) = 0.02

**Inputs read.** Snapshot `record/snapshots/2026-10-16.json` (one entry:
petition filed Oct 9, 2026, response due Nov 16, 2026; paid docket; CA6
No. 25-5579, decided June 16, 2026, rehearing denied July 16, 2026);
`record/documents/questions-presented.txt`; and the petition text
(`petition.txt`, 159 pages, truncated at the cap — I read the tables, the
statement of the case, and searched the reasons section for split language).
No brief in opposition exists yet. `context.json`: forward mode, arrival
moment, band `baseline` under `sal-v4`, zero distributions, no CVSG.

**Anchor.** This is an arrival cell, so the anchor is the caption class's
floor. Petitioners are private individuals (an attorney and a co-plaintiff),
so the class is `private` and its floor is `baseline` — which is also the
frozen band. Pooling the statpack's "Segment base rate by salience band
(sal-v4)" `baseline` bracketed `reached` figures over the Terms strictly
before 2026 (2017–2025, n ≈ 13,277 weighted) gives roughly **4.8%**. I did
not use the relist-0 cut (1.2%), per the prompt.

**Adjustments (down).**
- The questions are framed as error correction: the petition argues the panel
  misapplied *Heien*, *Chiaverini* and *Buckley* to these pleaded facts and
  inserted an unbriefed rationale. QP 3 is pure case-management grievance.
- The split claim ("every other circuit has rejected mistake of law as
  objectively reasonable") is asserted in a heading; I did not find a
  developed, acknowledged split in the text I read, and a qualified-immunity
  posture gives the Court an easy alternative ground (clearly-established law).
- Vehicle: Rule 12 posture with multiple defendants and both absolute and
  qualified immunity, plus state-law claims — messy for a clean ruling.
- The petitioner has litigated related matters in the Sixth Circuit before
  (the petition cites *Reguli v. Russ*, 109 F.4th 874); repeat litigation of
  this saga is not a grant signal.

**Adjustments (up).** The opinion below is published (178 F.4th 995), the
case is paid and counseled, and *Chiaverini* (2024) is recent enough that the
Court has some appetite for follow-on malicious-prosecution questions.

Net: about 2%, well under half the class floor. Main uncertainty is whether
the *Heien*-as-probable-cause question is a genuine circuit conflict I could
not verify from a truncated petition; if it is, a response call and a relist
become more plausible, but a grant would still be unlikely in this vehicle.

**Claims.** relist-increment 0.95: the docket shows zero distributions, and
almost every paid petition is distributed at least once (the residual is
withdrawal/dismissal before conference). cvsg-increment 0.003: no federal
interest. summary-disposition-route 0.15 (conditional on grant): plenary
review dominates for a question like QP 1; no obvious GVR vehicle.
dissent-from-denial 0.02: fact-bound immunity denials rarely draw writings.

**Retrieval.** None beyond the provisioned inputs and the committed statpack;
I did not query the corpus or CourtListener.
