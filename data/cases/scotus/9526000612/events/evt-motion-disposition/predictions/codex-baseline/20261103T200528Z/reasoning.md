# Rationale

## Target and record

I forecast denial, with **P(relief granted in whole or in part | no moot disposition) = 0.05**. This is an interim application, not a certiorari petition or a prediction of the ultimate merits. The number is not discounted for possible mootness.

The event definition identifies the arrival moment for Martin Akerman v. Merit Systems Protection Board, et al. I read the provisioned `record/snapshots/2026-10-21.json`. Its only proceeding is the October 20, 2026 submission of application 26A612 for an injunction to the Chief Justice. The lower-court identifier is D.C. Circuit No. 26-5131. The applicant is listed as his own attorney; that supports an inference of self-representation but says nothing conclusive about the merits. I do not infer the subject of the dispute, the order below, exhaustion, jurisdiction, or a particular employment injury from the respondent's identity.

The frozen `record/context.json` records forward mode, an arrival-position cut anchored at entry zero, no requested response, no full-Court referral, and zero amicus entries. Its null band is expected for an application and supplies no cert-stage anchor. A submission to the Chief Justice is not a referral to the full Court. Silence at this opening-entry moment is not evidence that the application later attracted no attention.

## Unavailable application and chronology

I opened `record/documents/application.txt`; it contains only whitespace. `documents.json` identifies a fetched, untruncated, 20-page application with `empty_text: true` and `ocr_derived: false`. The filing exists, but its content is unavailable. Consequently I cannot describe the actual grounds, assess the claimed irreparable injury, or identify the challenged order. I treat this as an information limitation, not an adverse fact about the applicant. An attempted open of the provisioned PDF URL returned no usable tool content. Two bounded CourtListener MCP searches for the lower-court matter returned no matches, which does not establish that the lower-court record or an opinion does not exist.

The snapshot's header gives October 30, 2026 as the docketed date, later than its October 21 filename and cutoff; the document metadata also records a November 3 fetch. The submission entry itself is dated October 20, matching the event's opening. I use that entry and the frozen context for the procedural starting state rather than treating the header as evidence of developments after submission. I flag the chronology for review and do not infer an elapsed period of judicial inaction from it.

## Base-rate check

I consulted the interim section of `metrics/statpack.md` and the machine-readable `metrics/statpack.json`. For application Term 2026 the contract requires the ten strictly prior application Terms, **2016 through 2025**, using `finer_granted`, `finer_resolved`, and `finer_unread`. Summing those rows gives:

- `finer_granted`: **0**.
- `finer_resolved`: **0**.
- `finer_unread`: **1,366**.
- `unparsed`: **16**, concentrated in Terms 2016 and 2017.

There is therefore **no eligible published baseline**: the finer-reading pool does not reach 50 resolved applications and has unread resolutions. Zero resolved cases is not a zero-percent grant rate. The markdown table reports the older substantive reading; its displayed rates cannot substitute for the required finer-reading pool. I do not use its whole-pack figure, its current-Term row, any single prior Term's rate, or a cert salience-band rate as an anchor. The escalation columns also describe last-polled levels across substantive applications, not prospective transition rates from this arrival state; they do not numerically determine my increment forecasts.

## Why these probabilities

Without a valid empirical anchor or readable grounds, the five-percent relief estimate is a deliberately conservative, judgmental prior for an individual applicant seeking an injunction from the Supreme Court. Following the prompt's interim framework, I would need a persuasive prospect of review or reversal together with irreparable harm to move substantially higher. Those grounds cannot be evaluated here. Their unavailability is not proof that they are absent; it substantially lowers my confidence in the estimate. Self-representation supplies only a modest downward qualitative consideration, not a dispositive rule. I have no record-supported basis for forecasting partial relief rather than ordinary denial.

I assign 0.12 to a new request for a response, 0.20 to a later referral, and 0.03 to an increase from zero amicus entries, including submitted briefs under the contract's counting rule. These are independent marginal forecasts, not categories summing to one, and referral need not follow a response request. They reflect the most likely path of disposition without escalation while leaving meaningful room for full-Court consideration. No request, referral, or amicus event is already on the frozen record. Separate-writing probabilities are very low because I expect a short unexplained order; they concern authorship, not votes or mere joins. I do not forecast a Justice-by-Justice vote split.

The missing application prevents a defensible assessment of significance, so `big_case_score` is explicitly null with an explanation rather than inferred from low grant odds. I have no known outcome for this application. I did not retrieve its disposition, subsequent history, another predictor's output, or an evaluator outcome. External attempts provided no usable substantive evidence. The forecast rests on the frozen record and the limitations described above.
