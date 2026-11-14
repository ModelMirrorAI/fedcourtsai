# Reasoning — scotus/9526000680 (26A680), evt-motion-disposition, interim / arrival

**P(relief granted in whole or in part | decided, not moot) = 0.01.**

## What I read

- Snapshot `2026-11-12.json` (forward mode, `arrival-position` cut at entry 0): a single docket entry, "Application (26A680) for a stay, submitted to Justice Sotomayor" (Nov 11 2026). Lower court: Supreme Court of Connecticut (PSC-250444). Applicant is self-represented; respondent is Deutsche Bank National Trust Company as trustee. Not a capital case. Context: no response requested, not referred, zero amicus entries, `band: null` (normal for an interim cell; I did not derive a band).
- `record/documents/application.txt` (38 pages, `ocr_derived: true`, not truncated). I relied on it for the argument only, not for any figure. It is an emergency application for an administrative stay and a stay pending a not-yet-filed certiorari petition, aimed at a Connecticut trial-court property proceeding set for November 16, 2026. The applicant says she is 89 and cognitively disabled, that the trial court withdrew an approved disability accommodation, that liability was then entered on her resulting non-opposition, and that the Connecticut Appellate Court and Supreme Court declined review. The federal grounds are ADA Title II and Fourteenth Amendment due process. The application itself notes a separate federal civil-rights appeal pending in the Second Circuit.

## Base rate

From the committed `metrics/statpack.md`, "The interim docket (applications)". The applicant-class table's bottom-right cell is the scored pool for an OT2026 application (ten prior application-Terms, finer reading): **11.7% (156/1337)**, well above the 50-resolved floor. That is the yardstick. The cell that describes this application is `private` / `unmarked`: **7.0% (63/906)**. I leaned on that cell, not the margin, and then moved far below it.

## Why far below the private-applicant cell

- The private cell pools counselled, high-stakes emergency applications (elections, religious-liberty, major injunctions) with the much larger stream of pro se applications arising from foreclosure, eviction and family-court matters. To my knowledge the latter are denied essentially without exception, usually by the Circuit Justice alone and without a response.
- The stay standard needs a reasonable probability of certiorari and a fair prospect of reversal. The questions are fact-bound (whether a particular accommodation was wrongly withdrawn in one state trial court), the state high court's action was a discretionary refusal to review, and no split or recurring legal question is identified.
- Jurisdictional and vehicle problems: the trial proceedings are still ongoing, so finality under 28 U.S.C. § 1257 is doubtful (the application invokes Cox Broadcasting, which signals awareness of the problem); the relief sought is in substance a stay of an upcoming state trial-court hearing rather than of a judgment under review.
- Nothing on the escalation ladder has fired: no response request, no referral, no amici.

The sympathetic facts (age, disability, a home) are the only thing keeping me off an even lower number; they could conceivably prompt a response request, but I put that at about 2%.

## Other claims

- `response-requested-increment` 0.02: the hearing is days away; a Circuit Justice inclined to deny does so without calling for a response.
- `referral-increment` 0.07: Justice Sotomayor will most likely deny alone. The residual is the pro se pattern of renewing a denied application to a second Justice, which is then referred to the Court and denied. I discounted it because the November 16 hearing will likely overtake the request before a renewal could be acted on.
- `amicus-increment` 0.01.
- `order-writers`: near zero for every Justice; single-Justice denials carry no writing.

## Uncertainty and discounts

- The application text is OCR-derived; I used it only for the shape of the argument.
- The filing carries a clerk's received stamp later than the docket's submission date; in forward mode that is ordinary and I flag nothing.
- If the hearing passes before action, the application may be denied or dismissed as moot, which leaves the scored set; my number is conditional on a decision as the contract asks.
- I did not use the CourtListener MCP server or the web; the forecast rests on the provisioned record, the statpack, and one corpus query (see `retrieval.md`) that returned generic recent denials and did not move the number.
