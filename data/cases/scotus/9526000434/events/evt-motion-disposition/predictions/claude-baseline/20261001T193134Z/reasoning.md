# Why 0.01

## The record I was given

- **Snapshot** `record/snapshots/2026-09-26.json`, cut at `arrival-position` (anchor index 0): one docket entry, "Application (26A434) for an injunction, submitted to Justice Alito," dated Sep 25 2026. The caption is *Ryan P. Givey, Applicant v. Todd Blanche, Attorney General, et al.*; the applicant is his own counsel of record (pro se, Pennsylvania); the Solicitor General is counsel for the respondents. Lower court: Third Circuit, No. 26-1067. The docket is linked with 26-153.
- **Context**: `mode: forward`, `band: null`, `response_requested: false`, `referred_to_court: false`, `amicus_briefs: 0`, `term: 2026`. Band is null as the prompt says is normal for an interim cell, so no cert-band anchoring and no caption-class floor applies here.
- **Documents**: `documents.json` lists the application (55 pages) with `empty_text: true`. The text could not be extracted, so I have no view of the application's own argument. Everything about the merits below is inferred from the docket and from retrieved public records, not from the filing.

## Base rate

The statpack's "The interim docket (applications)" section carries the scored base rate. Pooling strictly-prior Terms within the ten-Term window (2016 through 2025): only Terms 2025 and 2024 carry parsed substantive rows.

| Term | resolved (subst.) | granted |
| --- | --: | --: |
| 2025 | 226 | 17 |
| 2024 | 70 | 14 |
| pool | 296 | 31 |

Pooled grant rate 10.5% (n = 296), which clears the 50-resolved floor, so this is the published baseline my skill is scored against. I read the section's current caption, which already describes the rate as grounding the scored base rate rather than as descriptive-only. Caveats I carry from it: Term 2024 is 972 rows unparsed, so that Term's 20% rests on partial coverage; the pool is unconditioned on the escalation ladder while predicted cells are selected on it.

## Adjustments from the anchor

The 10.5% pool is dominated by government and state applicants, capital cases, and represented parties with amicus support. This application sits at the opposite end of that population on every observable dimension:

1. **Pro se applicant seeking an injunction against federal officers.** Among the Term-2026 substantive applications the corpus returned, every application I could identify as pro se (Randolph, Banks, Downs, Cheleden, Aderemi, and the applicant's own 26A397) was denied, with no response requested and no referral. Pro se injunction applications to a Circuit Justice are granted essentially never.
2. **Posture below.** CourtListener shows the underlying suit, *Givey v. Bondi*, E.D. Pa. 2:25-cv-00943 (a 42 U.S.C. § 1983 civil-rights action against the Attorney General, the FBI Director and a U.S. Attorney), dismissed on 2025-12-30 under Rule 12(b)(1) for lack of subject-matter jurisdiction. The Third Circuit appeal 26-1067 was docketed 2026-01-13; CourtListener's copy of that docket shows only the docketing entries, so I do not know whether the circuit has ruled. An applicant whose case was dismissed for want of jurisdiction has little prospect of showing the "fair prospect" of reversal plus irreparable harm an injunction requires, and an injunction pending appeal is the most demanding form of interim relief.
3. **The applicant's own recent history on the interim docket.** The corpus shows 26A397, *Givey v. Givey* (a substantive application from a Pennsylvania Supreme Court matter), denied 2026-09-23, two days before this application was submitted, with no response called for and no referral; and 26A331, a time-extension application in the same matter, granted 2026-09-11 in the routine way extensions are. The 26A397 denial is public information predating my snapshot and is legitimate forward signal about how the Circuit Justice is handling this applicant's filings. It is not this case's outcome.
4. **Links to 26-153.** A companion cert petition exists but I could locate it in neither CourtListener nor the corpus's most recent 500 rows, so I know nothing about it beyond the link. It slightly raises the chance of referral (the Court sometimes disposes of an application together with the petition) without raising the chance of a grant.

Net: I move from 10.5% to **0.01**. I would not go to zero because the resolver reads the disposing entry's text and an unusual order shape is always possible, but nothing in the record supports more than a token probability.

## The increments

- **Response requested (0.04).** Pro se applications of this shape are typically denied on the papers. The SG as counsel of record makes a response cheap to obtain, which is why I am not lower.
- **Referral (0.12).** Justice Alito usually acts alone on pro se applications; the companion petition is the main route to a referral. The statpack's referral count (178 of 367 substantive applications) describes a far more consequential population than this one and is right-censored, so I read it as shape only.
- **Amicus (0.01).** No organized interest in sight.

## Where to discount me

- I never read the application. If it raises something the docket does not reveal, for example a genuine emergency, my probability is too low, though even then the grant rate for this class is tiny.
- I do not know the Third Circuit's current state in 26-1067 and could not find petition 26-153; the forecast of referral is the number most sensitive to that gap.
- `fedcourts query` has no free-text filter, so my "pro se" identification of corpus priors is a heuristic on counsel-of-record names and is approximate.
