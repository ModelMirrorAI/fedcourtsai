# Rationale for the prediction

## Information set

This is a cert-stage, response-requested cell in forward mode. I read the
provisioned July 22, 2026 snapshot, context.json, documents.json, the extracted
questions presented, the petition's substantive arguments, and the Ninth
Circuit memorandum reproduced at petition appendix 1a-8a. The context freezes
Term 2025, sal-v4 baseline, one distribution, and no CVSG. The date cutoff is
July 23. I do not know this petition's disposition and did not retrieve its
current docket, later history, or another cell's output. Although the run is
dated October 29, the case-specific evidence used here remains the provisioned
July information set.

The snapshot records filing on June 8, respondent's July 13 waiver, July 15
distribution, and the July 22 response request, due August 21. No opposition
is provisioned or yet recorded at this moment, so I infer none of its arguments.
The petition text is marked truncated, with omissions identified within the
appendices; the questions, petition body, and appellate memorandum needed for
this forecast are available. No related-docket snapshot is staged. The account
of Robinhood's CVSG and overlap comes from this petition, pages 2-3 and 24-26,
not from independent verification or knowledge of subsequent proceedings.

## Anchor and adjustment

The committed statpack's sal-v4 table matches the frozen salience version. I
pool the baseline bracketed reached rates over every displayed Term strictly
before this docket's Term: 2017-2024, excluding 2025 and 2026. Using the matching
JSON counts gives 607 grant-family outcomes / 11,599 denial-reweighted resolved
risk-set observations = 5.23%. This is the private-caption arrival-floor risk
set, not the terminal-baseline rate, and not a special called-for-response
cohort. These are committed-pack estimates, not a fresh live-corpus census; I
did not pull a corpus blob or independently establish its newest pull stamp.

I raise the grant-family estimate to 24%, a judgmental adjustment rather than
a measured response-request effect. Three considerations drive the increase:

- A response requested after waiver is affirmative attention, although the
  threshold is low and does not establish that four Justices favor review.
- The petition connects its first question to the risk-disclosure issue the
  Court previously agreed to hear in Facebook before dismissing that case as
  improvidently granted. That history is described in petition pages 2 and
  18-21. It supports issue-level interest, not an assumption that this case
  cures the earlier vehicle problem.
- Questions two and three overlap Robinhood, which the petition says already
  drew a CVSG. A potential hold followed by GVR is a real part of P(any grant),
  even when ON24 is not the likely lead vehicle for plenary review.

I keep the estimate below one in four because the appellate disposition is
unpublished, nonprecedential, and reverses a pleading-stage dismissal rather
than entering liability. Most importantly, the memorandum itself retains a
materiality requirement, credits allegations of pre-IPO churn and management
knowledge, and rejects using judicially noticed revenue data to contradict
plausibly pleaded facts (appendix 5a-8a, especially footnote 5). Thus the
petition's claim that the panel demanded disclosure of immaterial facts is
contested advocacy, not an adjudicated fact. The apparently clean legal split
could become another dispute over what risk was warned of, what had already
happened, and what must be accepted at the dismissal stage. Its cited split
cases also concern Rule 10b-5, while this case presents Section 11 and an
independent Item 303 theory. Those distinctions reduce vehicle quality.

## Other forecasts and stakes

The 99% distribution-increment forecast mostly prices routine redistribution
after a called-for response; it is not 99% confidence in a substantive relist,
and the harness masks this claim at this moment. The paid-segment relist cut
has weighted resolved n = 10,203 / 2,538 / 495 / 484 for terminal buckets
0 / 1 / 2 / 3+. Their grant-family shares are approximately 1.8% / 13.7% /
41.2% / 37.4%. These are terminal categories, not forward transition hazards;
the mandatory response step makes their raw levels especially unsuitable here.

The CVSG cut shows approximately 34.8% grant-family outcomes among n = 164
resolved CVSG petitions, against 6.4% among n = 13,556 without one. That is
population shape, not this docket's CVSG probability. I assign a separate new
CVSG 10% because related government input may do the same work through
Robinhood. The snapshot has no amicus entry, while the frozen amicus count is
null; I do not convert that null into a measured count or use a terminal
amicus bucket as another independent likelihood boost.

The conditional summary-route estimate of 65% makes roughly 15.6 percentage
points of the 24% grant probability summary routes and 8.4 points plenary
routes. It principally prices contingent companion-case treatment; no
intervening Supreme Court decision requiring an immediate GVR is established
by this record. I assign denial-related writing a conditional 3.5% and give
each sitting Justice a small unconditional order-writing probability. The
per-Justice figures include writing on grant orders as well as denials and
need not sum to one. I omit speculative cert votes.

The stakes score is 0.52: rules governing IPO risk disclosures and known trends
could affect issuers, underwriters, and investors nationally. The individual
webinar-company dispute, unpublished ruling, and disputed pleading inferences
keep this below the highest-stakes constitutional or structural cases.

## Retrieval limitations

An official-site web search and direct attempt to open the historical
Macquarie opinion returned no usable content. A CourtListener MCP lookup for
Macquarie, 601 U.S. 257, was refused with HTTP 429 and a daily-limit message.
I used no direct REST fallback and relied on the provisioned documents and
committed statpack instead. No external result supplied additional legal facts
or information about ON24's outcome. The main uncertainties are the missing
adversarial response, the actual strength of the claimed split, and whether the
related petition will yield a decision that changes this judgment.
