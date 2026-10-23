# Basis for the prediction

## Information set and target

This is the forward, briefed merits cell for Kendrick Jarrell Beaird v. United States, not a prediction of certiorari. I used the case-level snapshot `record/snapshots/2026-08-26.json`, the event definition, `context.json`, `documents.json`, the questions presented, the lower-court opinion in `appendix.txt`, and the relevant factual, summary-of-argument, and remedy sections of both `merits-brief-petitioner.txt` and `merits-brief-respondent.txt`. The briefs are provisioned as nonempty and untruncated. I did not read every page of their statutory appendices or every argument subsection. The original petition's three questions are not the scope of review: the April 20, 2026 grant expressly limits review to the Stinson commentary-deference question.

The baseline stops before August 26, 2026. It records argument scheduled for October 13, 2026; a scheduled event is not evidence of what occurred at argument. Although this forward cell permits later retrieval, I have not retrieved argument, subsequent docket entries, or this case's disposition. I do not know this case's Supreme Court outcome. No other prediction or labeling-measurement artifact informed the forecast.

## Published anchor

I used only the merits section of the committed `metrics/statpack.md`, which publishes the required excluded column. The grant was April 20, 2026, in October Term 2025; the August 25 briefed-event date falls in the same Term. The eligible ten-Term window is therefore grant Terms 2015 through 2024. The section actually supplies rows for 2017 through 2024 in that window; it supplies no rows for 2015 or 2016, and I have not manufactured them or treated them as observations. I excluded the 2025 row entirely.

Adding the eligible rows gives 360 disturbed judgments out of 516 parsed judgments, a pooled rate of **0.697674**. Parsed coverage is **516/539 grants, or 95.73%**. Another 56 excluded rows are outside those 539 grants, not an additional subset of them. The pool exceeds the 30-judgment floor. This is a parsed-slice baseline, not a claim about all granted cases; the coverage gap can mix pendency with missing parses, particularly for the nearest Term. It is the committed pack as available to this run, not a freshly queried corpus estimate; I did not retrieve corpus-wide refresh stamps and make no current-corpus freshness claim. The high cert salience band and seven prior distributions play no role in this merits estimate.

## Why P(disturbed) is 0.93

The most important adjustment is adversarial alignment on the immediate judgment. Petitioner's brief, printed pages 10-13 and its remedy section, asks for vacatur and remand. The United States' brief, printed pages 11-14 and 28-33, also expressly asks for vacatur. They disagree substantially on the new rule: petitioner principally seeks independent judicial interpretation without commentary deference, with Kisor as a fallback; the government would retain Stinson understood through Kisor and expects commentary often to satisfy the resulting conditions. Their agreement is therefore stronger evidence for vacatur than for any particular doctrinal rationale.

The appendix's Fifth Circuit opinion treats the guideline challenge as foreclosed by circuit precedent. Petitioner's factual account describes a seventeen-round Glock magazine, a commentary-based increase from a 51-63 month range to a 63-78 month range, and a 72-month sentence. The forecast does not depend on independently deciding whether seventeen rounds are large capacity. It depends on the Court rejecting a deference framework that forecloses the required interpretive analysis.

There are meaningful reasons not to move to certainty. The Court appointed an amicus to defend the continued correctness of Stinson. The snapshot records that brief as filed on August 25, but its text is not provisioned: the respondent slot contains the United States' supporting-vacatur brief, not the Court-appointed defense. I cannot treat two aligned merits briefs as a complete presentation of the opposition. In addition, the United States identifies three separate barriers to ultimate resentencing: circuit stare decisis over the guideline's construction, the possibility that the commentary survives Kisor anyway, and the district judge's statement that the same sentence would have been imposed independently of the range. Those points could produce affirmance or a vehicle-based exit. They are not equivalent to affirmance, however: the government squarely recommends vacatur so the lower courts can address them first.

My internal judgment allocation is vacated 0.84, reversed 0.07, affirmed-in-part-reversed-in-part 0.02, affirmed 0.05, and dismissed-as-improvidently-granted 0.02. Thus P(disturbed) is 0.93, and vacated is the modal six-label judgment. I assign no separate appreciable equally-divided probability without evidence of a recusal; that is a modeling simplification, not a claim of impossibility.

## Rationale, votes, and stakes

The more uncertain part is the doctrinal route. Applying Kisor to Stinson follows the shared Seminole Rock foundation described in both briefs and offers a narrower resolution than eliminating deference altogether. The parties' agreement on at least the need to revisit the Fifth Circuit's framework makes a broad judgment coalition plausible even if the anti-deference Justices would go further. I therefore commit to unanimous vacatur, a seven-Justice Kisor-based majority, and Thomas and Gorsuch concurring in the judgment. This precise rationale split is substantially less certain than vacatur itself; I do not infer it from any retrieved argument or opinion. I do not forecast an author.

The majority-ground claim selects the retained-but-constrained Kisor route over both unchanged Stinson and categorical abolition. The breadth claim predicts a generally applicable commentary rule but leaves this guideline's actual meaning and the harmlessness issues for remand. Wholesale abolition is the strongest competing rationale; a reader should discount the semantic forecast more than the disposition probability.

The 0.67 significance score reflects the rule's reach across federal sentencing and its connection to judicial interpretive authority, tempered by a technical question and a limited grant excluding the petition's broader constitutional gun issues. It is not a grant-likelihood score.

## Retrieval limitations

A CourtListener MCP search verified Kisor's identity and date, but both attempts to search within its opinion were throttled with HTTP 429. Web attempts for general precedent returned no usable content. I relied on the provisioned briefs' characterizations instead of claiming to have independently read the Kisor opinion. No direct CourtListener REST fallback was used. The missing Court-appointed amicus text is recorded in `flags.json`; tooling limitations are also described in `tooling.json` and `retrieval.md`.
