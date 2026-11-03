# Reasoning: 26A619, Smith v. Brown, Savage, Britto, Stitely & Callahan, LLP (interim, arrival)

**P(relief granted in whole or in part | not mooted) = 0.02.**

## What the record shows
- The snapshot (`2026-10-28.json`, an arrival-position cut at entry 0) has one entry: "Application (26A619) for a stay, submitted to The Chief Justice" (Oct 27, 2026). It was docketed Oct 30. The lower court is the Supreme Court of Maryland, case number "(119)".
- The applicant, Denise Smith, represents herself and is listed as her own counsel of record. The respondents are a Maryland law firm "et al." The case is private and not capital.
- Context: no response requested, not referred, 0 amicus filings, band null. That is the normal interim state, so I used no cert band.
- `application.txt` was fetched (37 pages) but has `empty_text: true`. The PDF had no text layer, and `fedcourts pdf-text` cannot read the staged `.txt`. So I cannot say what relief is sought or on what grounds. I treat the content as unavailable and infer only from the docket. A state high court and a law-firm respondent fit a collection, foreclosure or fee dispute, but that is a guess and none of the numbers rests on it.
- I checked the Court's live docket page (forward mode). It shows the same single entry, with nothing after it.

## Base rate
- Under the contract the anchor is the finer reading pooled over application-Terms 2016–2025. In `metrics/statpack.json`, every one of those Terms has `finer_resolved = 0` and a non-zero `finer_unread`. The pool therefore fails the "unread count zero" condition, and **no published baseline exists for this cell**. I anchored without one. The md section's caption reads as the descriptive or older layout.
- For shape only: the older substantive reading pools to about 160/1366 ≈ 11.7% over 2016–2025. That population includes Solicitor General and other government applications, capital stays and represented parties, which account for almost all grants. Self-represented stay applications against private parties from state courts are granted only very rarely.

## Adjustments
Self-represented filer, private respondent, state-court judgment, no ladder rung fired, and no text that could show an unusual equity. All of this points to a Chief Justice denial in chambers, possibly followed by a renewal to another Justice that gets referred and denied. I put the grant chance at 2% rather than lower to allow for an unseen point in the filing.

## Increments
- Response requested: 3%. The Court rarely asks for responses on applications like this.
- Referral to the full Court: 12%. Self-represented applicants often renew to a second Justice after a denial, and renewed applications are commonly referred to the Court.
- Amicus: 1%.

## Discount me where
I could not read the application. If it is actually from an unusual posture (for example, a constitutional question with real stakes), my number is too low, though only slightly.
