# Reasoning — Robinhood Markets, Inc. v. Sodha (No. 25-944), merits, moment: grant

**Call:** P(judgment below disturbed) = 0.84; predicted judgment `vacated`; predicted lineup 9–0.

## What I worked from

Forward cell. Snapshot `2026-11-14.json` (cut by date at 2026-11-14), which shows the grant order of Nov 13, 2026, limited to the Solicitor General's reformulated first question. Provisioned documents read: the questions presented, the SG's invited brief (in full), both supplemental briefs (respondents' closely), key passages of the Ninth Circuit opinion (`decision-below.txt`, which matches the judgment the petition describes: Sodha v. Golubowski, No. 24-1036, Aug. 29, 2025, M. Smith and Rakoff in the majority, Rawlinson dissenting in part), and `lower-court-docket.txt` (rehearing en banc denied, no dissent noted). I skimmed rather than read the petition, BIO and cert reply, relying on the SG brief's and the supplemental briefs' account of them. No merits briefs are on disk, as expected at this moment, and I retrieved none. No argument has occurred. I did not use the CourtListener MCP server or the web.

## Anchor

The statpack's merits section publishes an `excluded` count, so it is quotable. The grant date is Nov 13, 2026, so the grant Term is OT2026 and the pool is grant Terms 2016–2025; the table carries 2017–2025: disturbed 395 of 560 parsed = 70.5% (coverage: 560 parsed of 603 granted in those rows; the 2025 row is the most censored, 26 parsed of 53). The context's `band` (high) is a cert construct and I did not use it.

## Adjustments (up from 70.5% to 84%)

- **The United States sides with petitioners on the merits of the question granted.** The SG's brief, joined by the SEC, says the Ninth Circuit erred by collapsing materiality and misleading effect, and the Court granted exactly the question the SG wrote. The government as amicus supporting a petitioner is a strong predictor of reversal, and the SEC is the expert agency here.
- **The Court adopted a question framed to isolate the Ninth Circuit's weakest sentence.** The panel described itself as "collapsing the duty to disclose into materiality" and said Sections 11 and 12 "create a duty to disclose all material information in cases like this one." That is hard to square with the statute's two-part text and with Omnicare (Section 11 is "not a general disclosure requirement") and Macquarie ("half-truths, not pure omissions"), both recent and unanimous or near-unanimous.
- **Ninth Circuit, divided panel, business petitioner with securities-industry amici.** All lean modestly toward disturbance.

## Why not higher

- **DIG risk (~7%).** Respondents say there is no real disagreement: they accept two elements and argue only that, on these facts, materiality proves misleadingness. They cite the 2024 DIGs in Facebook and NVIDIA, two securities cases from the same circuit. The reformulation ("without an additional inquiry") was designed to fix this, which is why I keep it under 10%, but the risk is real and counts as undisturbed.
- **Affirmance (~9%).** Respondents have a respectable narrow reading: the panel acknowledged the two elements are distinct and held only that they coalesce where a statement about one period is followed by a known contrary later event, which they trace to the Second Circuit's Time Warner and Stadnick decisions. A Court persuaded by that could affirm with clarifying language.
- I have not seen merits briefing or argument.

## Judgment label

`vacated` over `reversed`: the Ninth Circuit applied (on the SG's view) the wrong legal standard and expressly did not decide whether the complaint states a claim; the Item 303 holding is outside the grant and stands. The natural disposition is to vacate and remand for application of the correct test, as in Omnicare and Macquarie. The Court could instead write "reversed" (or reversed in part); I put roughly 50% on vacated, 30% on reversed, 4% on a mixed label. This choice does not affect the scored probability.

## Votes

All nine in the majority. Macquarie was 9–0 and Omnicare had no dissent; the question is textual and the government supports the result. The Justices most likely to break off are Jackson and Sotomayor (investor-protective, or favoring a DIG), but I expect at most a concurrence. Statpack per-Justice rates (OT2025: with-judgment rates between 69.8% for Jackson and 96.2% for Roberts, of 52–53 sat) are pooled over all cases and do not move a call on a case of this type. Discount the lineup: it is the least certain part of this forecast.

## Authorship numbers

Near the flat prior, tilted toward Kagan (wrote Omnicare) and Sotomayor (wrote Macquarie), and slightly to Barrett, Kavanaugh and Jackson. Roberts is lower because he rarely keeps a case like this. Separate-writing numbers are low across the board for an expected unanimous statutory decision, highest for Jackson, Sotomayor, Thomas and Gorsuch.

## Retrieval and data notes

One corpus query succeeded and returned recent granted dockets with no subject match; it did not inform the numbers. The `--citation` lookup for Macquarie and Omnicare came back with the coverage-gap note. What I say about those two cases beyond what the staged briefs quote, and about the Facebook and NVIDIA dismissals beyond respondents' description, rests on my own recall. No flags.
