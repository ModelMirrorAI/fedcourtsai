# Reasoning — scotus/9526000752 (26A752), evt-motion-disposition, interim / arrival

**P(relief granted in whole or in part | not mooted) = 0.005. Call: denied.**

## What I read
- Snapshot `2026-11-18.json`: one entry — "Application (26A752) for a stay, submitted to Justice Barrett" (Nov 17 2026). Applicant is self-represented; lower court is the Seventh Circuit, No. 26-2488. Not capital. No response requested, no referral, no amicus entries (`context.json` agrees: all three rungs at zero; `band` null, as expected on an interim cell).
- `record/documents/application.txt` (17 pages, `ocr_derived: true`, not truncated). I rely on it for the argument only, not for any figure. The applicant asks Justice Barrett to stay a November 10, 2026 Seventh Circuit order that denied leave to appeal in forma pauperis and required payment of the appellate filing fee by November 24 on pain of dismissal; to stay further appellate proceedings pending a certiorari petition; and to appoint counsel under Criminal Rules 1 and 44, with alternative post-payment relief. The underlying case is a pro se civil RICO action (stolen car run through a salvage chain) that the district court screened and dismissed with prejudice as frivolous / failing to state a claim, with a $500 sanction for disrespectful language and a filing bar until payment. The application says a stay will be sought below "simultaneously" and asks for the Rule 23.3 exception.

## Anchor
- Statpack "The interim docket (applications)", applicant-class table (the scored pool for an OT2026 application: ten prior application-Terms, `finer_*` counts): all applicants 11.7% (156/1337), comfortably over the 50-resolved floor. That is the baseline my cell is scored against.
- The caption class is `private`, unmarked (non-capital): 7.0% (63/906). I read that cell, and it is the more relevant population; I lean on it over the margin.

## Adjustment (downward, a lot)
The private/unmarked 7% pools counseled emergency applications of real consequence with a large body of pro se applications that are denied by the Circuit Justice without a response. This one sits at the bottom of that cell:
- Self-represented, no response requested, nothing on the ladder.
- The order below is a routine appellate IFP denial resting on a no-arguable-merit finding; the "irreparable harm" is having to pay a filing fee or have a civil appeal dismissed. That is not the kind of harm the Court stays orders for, and there is no reasonable probability four Justices would grant certiorari on a fact-bound IFP/screening dispute.
- The applicant concedes relief was not first sought (or was only simultaneously sought) below — Rule 23.3 makes that a ground for denial on its own.
- The counsel request rests on applying the Criminal Rules to a civil sanction, which has no footing.
- The fee deadline (Nov 24) has probably passed by the time of action; if that produced a moot dismissal it would leave the scored set, so I do not price it.

I know of no instance of a stay being granted in this posture. Residual 0.5% covers clerical/unknowns. A reader should discount only for my not having seen the Seventh Circuit orders' full text (the appendix content is described by the applicant, and the OCR is imperfect).

## Other claims
- Response requested: 0.01 — essentially tracks the grant chance; the Court does not call for responses on applications it will summarily deny.
- Referral to the full Court: 0.05 — the realistic path is denial by Justice Barrett alone; a referral happens mainly if the applicant renews the application to another Justice after that denial (Rule 22.4), which determined pro se filers sometimes do. This applicant is clearly persistent, hence 5% rather than ~1%.
- Amicus: 0.003.
- Order-writers: ~0.001–0.002 each; a single-Justice or unsigned denial carries no writing.

## Retrieval
One corpus priors query (recent denied SCOTUS application rows, which showed same-week pro se applications denied within days) and the committed statpack. No CourtListener MCP or web lookups; I did not look at the Court's live docket. No forecast of this case surfaced.
