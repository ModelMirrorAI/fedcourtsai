# Rationale for the numbers

**P(unqualified grant) = 0.01; predicted disposition `denied`.**

## What the record shows

The provisioned snapshot (2026-08-06, `truncated` provenance) shows a single
proceedings entry: "Application (26A163) for a stay, submitted to Justice
Alito" (July 22, 2026), docketed August 5, 2026. The applicant, Bridget
Gilmore, is her own counsel of record (pro se, a PO Box address in Texarkana,
TX); the respondent is Walmart, Incorporated; the lower court is the Fifth
Circuit (No. 26-30022). Not a capital case. The frozen context confirms the
escalation ladder at its floor: no response requested, not referred to the
full Court, zero amicus briefs.

Forward mode, so I retrieved the underlying Fifth Circuit docket (CA5
26-30022) via the CourtListener MCP server — deliberately *not* the Supreme
Court docket's current state, which could have surfaced this application's own
disposition. The CA5 record shows: a pro se civil-rights appeal (nature of
suit 3440) from W.D. La. No. 5:20-cv-1589, docketed January 20, 2026;
Walmart's motion to dismiss the appeal granted February 26; rehearing en banc
denied **without a poll** March 31; four successive motions to stay the
mandate denied (May 7, May 20, May 22 twice, after an earlier denial covering
the April 5 motion); serial filings alleging fraud on the court and clerk
misconduct, several rejected as procedurally improper; **mandate issued May
29, 2026**. The stay application here asks the Supreme Court for what the
Fifth Circuit refused repeatedly.

## Anchor and adjustment

The statpack's interim-docket section grounds the scored base rate for this
cell. My Term is 2026, so the pool is application-Terms strictly before it:
Term 2025 contributes 178 resolved substantive applications (16 granted) and
Term 2024 contributes 47 (14 granted) — pooled 30/225 ≈ **13.3%**, which
clears the pre-registered floor of 50 resolved. So this cell *does* have a
published baseline, computed from the section as the prompt directs (the
prompt's own worked figure of 44 describes an OT2025 cell, not this one). The
section's caveats apply: the pooled cohort's escalation-signal counts are
right-censored and the scored population is selected above this cohort on the
ladder.

I adjust far below that 13.3% anchor because the pooled cohort is dominated by
represented, often governmental, emergency applications, and every observable
feature of this one points the other way:

- **Pro se applicant against a private party** in an individual civil-rights
  dispute — the class of application that single Justices deny on the papers
  essentially without exception.
- **The appeal was dismissed below on motion**, not decided on the merits, so
  there is no plausible "fair prospect of certiorari" — the threshold showing
  a stay requires.
- **En banc denied without a poll** — not one CA5 judge asked for a vote.
- **The mandate already issued** (May 29), so the application arrives after
  the event it would most naturally have stayed, weakening even its form.
- **The ladder is at its floor**: no response requested, no referral, no
  amici, and the application sat with a single Circuit Justice for two weeks
  before docketing.
- The applicant's serial, escalating filings below (fraud-on-the-court
  motions, demands to the clerk) mark this as vexatious-adjacent litigation,
  which the Court disposes of summarily.

A 1% grant probability is, if anything, generous; I do not go lower because
the interim resolver occasionally matches an ambiguous administrative entry
as a grant, and because a floor of about a percent respects my own
calibration limits on rare events.

## The increment claims

- **response-requested-increment 0.03**: a response is called for where relief
  is plausibly on the table; nothing here suggests it. The statpack's
  response-requested count (53 across 254 substantive applications, ~21%,
  right-censored) describes a far stronger cohort.
- **referral-increment 0.12**: above my grant number by an order of magnitude
  because the path to referral does not require merit — a *renewed*
  application after a single-Justice denial is customarily referred to the
  full Court, and this applicant's demonstrated persistence (four stay motions
  below) makes a renewal on this same docket a live possibility. Most denied
  pro se applicants nonetheless stop, or refile under a new application
  number, so I keep it well under the cohort's raw referred share (92/254,
  right-censored).
- **amicus-increment 0.02**: no institutional stake; pro se employment
  disputes attract no amici.

## Uncertainty and discounts

The main uncertainty is not the disposition but the *route* — whether denial
comes from Justice Alito alone (my modal path) or after referral following a
renewal; that uncertainty lives in the referral number, not the grant number.
I did not read the stay application itself (no `record/documents/` text was
provisioned and I did not fetch the SCOTUS filing), so I infer its content
from the CA5 record; given four denied stay motions below rehearsing the same
grounds, I discount the chance that the application contains something new
almost to zero. Today is August 20 and the application was docketed August 5,
so it may already have been acted on; per the forward-mode etiquette I did not
look, and nothing outcome-revealing surfaced in what I did retrieve. No
published baseline conditions on the escalation ladder, so the three increment
numbers are banked judgment, not anchored figures.
