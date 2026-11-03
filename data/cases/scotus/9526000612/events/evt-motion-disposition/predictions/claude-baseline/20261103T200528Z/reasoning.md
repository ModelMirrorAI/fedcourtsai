# Reasoning — 26A612, Akerman v. MSPB (interim, arrival)

**P(relief granted in whole or part) = 0.005.**

## What the record shows
- Snapshot `record/snapshots/2026-10-21.json` (arrival-position cut, anchor index 0): one entry,
  "Application (26A612) for an injunction, submitted to The Chief Justice" (Oct 20 2026). Docketed Oct 30 2026.
  The case below is D.C. Cir. No. 26-5131. The applicant, Martin Akerman, is pro se and is his own
  counsel of record. Respondents are the MSPB et al., represented by the Solicitor General.
- Context: forward mode, `band: null` (which is normal for an interim cell), no response requested, not referred, 0 amicus.
- `record/documents/application.txt` is listed with `empty_text: true` (20 pages, no text layer).
  I could not read what relief is sought or on what grounds, so the forecast rests on the docket,
  the posture and base rates, not on the application's content.
- A corpus lookup of 26A612 shows it is still pending (no disposition, no response requested). A CourtListener
  docket search shows Akerman has a long run of pro se suits against the MSPB, DoD, Air Force and
  National Guard (D.D.C. 1:23-cv-02574, E.D. Va. 1:22-cv-00696, D. Nev. 2:24-cv-01602 and -01734).
  This is a recurring individual employment dispute, not a novel public question.

## Anchor
The statpack's interim section has no published baseline for this cell. Every pooled Term (OT2016–OT2025) has
nonzero `finer_unread` (e.g., OT2025 226, OT2024 194) and zero `finer_resolved`, so the finer-reading pool
fails the completeness condition. I anchored without a published baseline. For shape only: the
older `substantive` reading pools to about 11–12% granted over OT2016–OT2025 (e.g., 17/226 in OT2025). That rate is
dominated by government and represented applicants seeking stays, and it is not a figure to anchor on.

## Adjustment
- The ask is an **injunction** against a federal agency. A Supreme Court injunction pending appeal under the
  All Writs Act requires the right to relief to be "indisputably clear." That is a far higher bar than a stay,
  and the Court almost never grants it.
- A **pro se** applicant with a history of serial litigation against the same respondents. Grants to pro se
  injunction applicants are vanishingly rare.
- The application went to the Chief Justice as Circuit Justice for the D.C. Circuit. The typical path is a
  denial by the Chief Justice without calling for a response. A pro se applicant then often renews to another
  Justice, who refers it to the Court, and the Court denies it. That path is why I put the referral increment
  at 0.25 rather than near zero. I don't know whether this applicant has renewed past denials, which is my main uncertainty on that claim.
- Response request: 0.03. With the SG as respondent, a call for a response would signal real interest,
  and nothing on this record suggests any.
- Amicus: 0.01.
- Order writers: a written opinion on a pro se injunction denial is very unlikely. Every Justice is about 0.002–0.004.

## Where to discount me
I could not read the application. If it raised something structural, such as MSPB quorum or removal-power
issues tied to current litigation, the stakes could be higher, but a pro se injunction would still almost
certainly be denied.
