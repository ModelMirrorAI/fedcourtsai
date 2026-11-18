# Reasoning — scotus/9526000698 (26A698), evt-motion-disposition

**P(relief granted in whole or in part | not mooted) = 0.01. Call: denied.**

## What I read
- Snapshot `2026-11-13.json` (arrival-position cut): one entry, "Application (26A698) for injunctive relief, submitted to The Chief Justice" (Nov 12 2026). Lower court: D.C. Circuit No. 26-7016 per the docket (the application's cover says 26-7061; the text is OCR-derived, so I do not rely on either number). No response requested, no referral, no amicus entries (`context.json` agrees).
- `record/documents/application.txt` (35 pages, `ocr_derived: true`, not truncated). I read the cover, questions presented, jurisdictional statement and the opening of the argument (roughly the first third); the remainder I did not read line by line. It is a pro se filing by two Tennessee homeowners asking for an administrative stay and injunction against a non-judicial foreclosure sale of their home set for 17 November 2026, a permanent stay of a state misdemeanor prosecution, an end to a wage garnishment arising from an HOA judgment, and a final "decretal" merits judgment under 28 U.S.C. § 2106. It describes itself as a third supplemental application, lists eleven questions presented, and alleges 606 constitutional violations, a scheme to seize a proprietary financial invention, and intruders altering the document.
- No document from the court below was provisioned and I did not retrieve one.

## Anchor
- Statpack "The interim docket (applications)". Scored pool for an OT2026 application per the section's applicant-class table (the ten prior application-Terms, finer counts): 156/1337 = 11.7%, which clears the 50-resolved floor. The per-Term table's `granted` column gives a similar 10–12% over 2016–2025.
- Applicant-class table: I read the `private` / `unmarked` (non-capital) cell, 7.0% (63/906). The caption class (private applicants; a State is respondent) matches my own reading.

## Adjustment
Down sharply from 7%, on features the table does not split on:
- Pro se applicants with no counsel; the private-cell grants are overwhelmingly counselled applications raising a defined federal question against an identified order.
- The application does not identify a D.C. Circuit order it seeks to stay or a certworthy question; it asks this Court to enjoin a private foreclosure and state-court proceedings in Tennessee directly and to enter final judgment on the merits. An All Writs Act injunction from this Court requires indisputably clear legal rights; nothing here approaches that. The underlying federal suit appears (from QP 7) to have been dismissed on Younger grounds.
- The content (hundreds of alleged violations, conspiracy claims) is the profile of applications denied without a response.
- The ladder is at its bottom rung: no response requested, no referral, no amici.

I leave 1% rather than lower for generic uncertainty, including what I did not read in the back two-thirds of the filing. I do not discount for mootness (the sale date is the day this cell runs); the target is conditional on a non-moot decision.

## Other claims
- `response-requested-increment` 0.01: the Court almost never calls for a response to an application of this kind.
- `referral-increment` 0.25: the route to referral is a denial by the Chief Justice followed by a Rule 22.4 renewal to another Justice, which is then customarily referred to the Court and denied. These applicants are persistent filers (this is styled a third supplemental application and its body is addressed to Justice Thomas), which raises the chance of renewal; against that, the foreclosure date may pass and remove the urgency, and many pro se applicants do not renew. No committed table conditions on this, so the number is my judgment.
- `amicus-increment` 0.01.
- `order-writers`: a few tenths of a percent each; a denial here would carry no writing.

## Where to discount me
- I did not read the full application or the decision below. If the D.C. Circuit matter has an unusual posture I would not know.
- The referral number is the softest.

## Retrieval
One corpus query (generic denied SCOTUS priors; not informative for this case) and the committed statpack. No MCP or web retrieval; I did not look at the live docket.
