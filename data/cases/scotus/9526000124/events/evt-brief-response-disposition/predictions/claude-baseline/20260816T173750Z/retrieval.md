# Retrieval log

Forward-mode cell; retrieval unrestricted. Beyond the provisioned snapshot,
`event.yaml`, `record/context.json`, and the committed `metrics/statpack.md`:

## Corpus lookups

- `uv run fedcourts query --court scotus --include-applications --limit 8`
  — stderr: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`. Returned mostly
  recent time-extension applications plus one substantive capital application;
  no usable priors for a government election-stay application. Not used in
  the anchor.

## Web searches (engine-surfaced)

- `26A124 Trump v. California Supreme Court stay application Justice Jackson`
  — identified the case (stay of D. Mass. injunction against the mail-in
  voting executive order; SCOTUSblog case page; Election Law Blog post noting
  record-long pendency of the emergency motion; supremecourt.gov filing PDFs
  including the Aug 12 supplemental brief and Aug 4 reply; companion
  application 26A139 by state applicants).
- `Trump mail-in balloting executive order Supreme Court stay 26A124
  supplemental briefs August 2026` — EO dated March 2026 directing USPS
  mail-ballot restrictions; two Talwani orders enjoined; 12 states joined the
  government's side, 23 states + D.C. behind the injunction; DOJ supplemental
  brief urged prompt action and a decision written to cover parallel
  challenges; no administrative stay entered; application still pending.
- `Supreme Court mail-in voting executive order stay decision pending
  "longest" emergency election motion Hasen` — EO titled "Ensuring
  Citizenship Verification and Integrity in Federal Elections," signed
  March 31, 2026; injunction covers the 23 plaintiff states and D.C.; fully
  briefed for over a week with the SG pressing for action; Hasen's view that
  the President lacks the authority and the changes are unimplementable for
  2026. Sources consulted via these searches: scotusblog.com (case page and
  July/August coverage), electionlawblog.org (headline only — direct fetch
  returned HTTP 403), democracydocket.com, votebeat.org, constitutioncenter.org,
  supremecourt.gov docket PDFs, ms.now, newsweek.com.

## Failed fetches

- `WebFetch` of the Election Law Blog post on the motion's pendency — HTTP
  403; used its headline from search results only.

## CourtListener MCP

- None. The MCP search tool was loaded but no CourtListener call was made;
  the SCOTUS docket snapshot plus web coverage answered the posture
  questions.

No retrieval sought this application's disposition; searches confirmed it
remains pending as of the snapshot date.
