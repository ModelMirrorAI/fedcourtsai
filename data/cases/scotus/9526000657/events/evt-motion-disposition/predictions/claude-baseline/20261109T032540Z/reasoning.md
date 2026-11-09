# Reasoning — scotus/9526000657 (26A657), evt-motion-disposition (interim, arrival)

**P(relief granted in whole or in part | not mooted) = 0.015.**

## What the record shows
- Snapshot `2026-11-03.json` (arrival-position cut, anchor index 0): a single entry, Nov 2, 2026, "Application (26A657) for a stay, submitted to The Chief Justice." Lower court: CA4 No. 26-2406. Applicant Paul Schultz appears **pro se** (he is listed as his own counsel of record). Respondent: Kevin McCarthy. Not capital.
- Context: `band: null` (normal for interim), no response requested, not referred, 0 amicus briefs, forward mode.
- `record/documents/application.txt` was fetched (61 pages) but has `empty_text: true`, so I could not read the application's ask or grounds. I treat its content as unavailable, not absent.
- The Court's live docket (fetched Nov 9) still shows only the submission entry; nothing new.
- A CourtListener docket search shows a cluster of *Schultz v. McCarthy* matters: a 2025 adversary proceeding in the E.D. Va. bankruptcy court and several 2026 E.D. Va. civil dockets (likely bankruptcy appeals), plus an earlier Schultz bankruptcy appeal. I infer, without confirming it, that this is a pro se debtor's serial litigation against a bankruptcy trustee or creditor, and that he wants a stay of a bankruptcy-related order pending his CA4 appeal. This inference only reinforces the low number; the forecast does not hinge on it.

## Anchor
The statpack's interim section (the per-Term `finer_granted`/`finer_resolved` in `statpack.json`), pooled over application-Terms OT2016–OT2025 (strictly before OT2026), gives 156/1337 = **11.7%**. That clears the floor of 50, and every pooled Term has `finer_unread` = 0. This matches the applicant-class table's "all" cell, 156/1337. The caption-class cut is `private`/`unmarked` at **7.0% (63/906)**, which I leaned on. That cell mixes in well-represented private litigants: businesses, election cases and organized challenges to government action. A pro se individual seeking a stay of a lower-court order in a private, apparently bankruptcy-related dispute sits far below that. In practice the Circuit Justice denies such applications summarily almost every time.

## Adjustments
Down from 7% to about 1.5% because the applicant is pro se, there are no escalation signals, no government party, the matter looks like a serial private dispute, and the case has no visible cert-worthy question. I keep it above zero because I could not read the application.

## Increments
- Response requested: 3%. The Chief Justice seldom calls for a response on a pro se stay application.
- Referral to the full Court: 15%. Pro se applicants denied by the Circuit Justice often renew the application to another Justice, who usually refers it to the Court. That is the main route to this rung.
- Amicus: 1%.
- Order-writers: near zero for every Justice. Summary denials of such applications carry no writings.

## Discount me where
I could not read the application. The bankruptcy characterization is inferred from case-name matches on CourtListener, not confirmed.
