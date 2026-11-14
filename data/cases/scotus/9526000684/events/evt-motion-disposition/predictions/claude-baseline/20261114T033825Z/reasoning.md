# Reasoning — scotus/9526000684 (26A684, Schultz v. BOKF, N.A.), interim arrival

**P(relief granted in whole or in part | decided, not moot) = 0.01. Call: denied.**

## What I read

- Snapshot `2026-11-11.json` (forward mode, `arrival-position` cut, truncated): one entry — "Application
  (26A684) for a stay, submitted to The Chief Justice", Nov 10 2026. Applicant is self-represented;
  respondent is a bank. Not capital. No response requested, no referral, no amicus entries
  (`context.json` agrees: all three ladder signals at zero/false). `band` is null, as expected for an
  application; I used no cert band table.
- `record/documents/application.txt` (63 pages, `ocr_derived: true`, not truncated). I relied on it for
  the argument only, not for any figure. In summary: a pro se Chapter 7 debtor asks the Chief Justice for
  an "immediate temporary administrative stay" and a "limited stay in aid of prospective jurisdiction"
  that would (a) stop the E.D. Va. district court from finally disposing of his bankruptcy appeal
  (No. 1:26-cv-01125) and (b) stop enforcement of a bankruptcy order lifting the automatic stay, i.e. a
  foreclosure sale of a residence noticed for December 17, 2026, with an injunction as a fallback. The
  decision below is a Fourth Circuit unpublished per curiam of Oct. 22, 2026 denying mandamus
  (No. 26-2405); rehearing and an emergency stay motion were still pending there by the application's own
  account. The grounds are judge-recusal / neutral-tribunal and "party-presentation" theories built on a
  long history of related bankruptcy matters; the appendix itself includes two orders enjoining the
  applicant's further filings in adversary proceedings.

## Base rate

The statpack's interim section's applicant-class table is the scored pool for an OT2026 application
(ten prior application-Terms, `finer_*` counts): 156/1337 = 11.7% overall, clearing the 50 floor. That
is the yardstick. The cell that actually describes this application is `private` / `unmarked`
(non-capital): 63/906 = 7.0%. The caption class (private) is right here; no misread. I leaned on the
cell, not the margin, and then went well below it.

## Why far below 7%

- The private/unmarked 7% pools counseled, institutionally-backed applications (election, religious
  liberty, regulatory challenges) with pro se filings. Pro se civil stay applications arising from
  foreclosure/bankruptcy disputes are, in my experience of the docket, denied essentially always —
  typically by the Circuit Justice alone, or by the Court after a renewed application is referred.
- The posture is weak on every stay factor: the underlying ruling is a discretionary denial of mandamus
  in an unpublished per curiam; there is no split or cert-worthy question; rehearing below is still
  pending, so relief is arguably available below (Rule 23.3); and the harm is a property foreclosure
  after lift-stay litigation the applicant lost at several levels.
- Corpus lookups (see `retrieval.md`) surfaced two sibling applications by the same applicant, filed
  Nov 6 2026 out of the same cluster of litigation (26A657, Schultz v. McCarthy, from CA4 No. 26-2406;
  26A658, Schultz v. Gold): both denied within four to five days, with no response requested and no
  referral. These are different dockets, not this case's outcome, and they predate my snapshot; they
  were material in pushing me from ~2% to 1% and in keeping the response-request claim low.
- The request for an "administrative" stay does not change this: the Chief Justice enters those where
  he intends to call for a response, which I do not expect.

## The other claims

- `response-requested-increment` 0.02: no response called for on the siblings; nothing here invites one.
- `referral-increment` 0.12: referral happens here mainly if the applicant, after the Chief Justice's
  denial, renews the application to another Justice under Rule 22.4, who then refers it. That lands on
  the same docket number. This applicant is a persistent filer, and the Dec. 17 sale date gives time,
  but the siblings show no referral so far. This is my least certain number.
- `amicus-increment` 0.01: nobody files amicus briefs in a matter like this.
- `order-writers`: a few tenths of a percent each; a denial here will be a one-line order.

## Uncertainty and discounts

OCR text: I rely on it only for the shape of the argument. I did not look at the Court's live docket
for 26A684 (permitted in forward mode, but unnecessary and I preferred not to risk meeting a
disposition). The residual 1% covers the unknown: a misreading of the posture or a narrow temporary
order. I saw no forecast by anyone else.
