# Why these numbers

**Cell.** Interim stage, `moment: response-requested`, forward mode. Snapshot
`2026-10-03.json` (provenance `truncated`, `cut_kind: date`, cutoff 2026-10-03),
two docket entries: submission to Justice Kavanaugh on Sep 29 and his call for a
response on Oct 2, due Oct 8. Frozen context: `response_requested: true`,
`referred_to_court: false`, `amicus_briefs: 0`, `band: null` (correct for an
application docket; not anchored on). Provisioned document: the 44-page stay
application (`application.txt`, full text, not truncated). No response or BIO
exists yet.

## Anchor: the statpack's interim-docket section

The committed `metrics/statpack.md` carries "The interim docket (applications)"
with per-Term substantive counts. The application Term is 2026 (docket 26A446),
so the pool is application-Terms 2016–2025, strictly before 2026. Only two of
those Terms carry parsed substantive rows:

| Term | resolved (subst.) | granted | unparsed |
| --- | --: | --: | --: |
| 2025 | 226 | 17 | 0 |
| 2024 | 70 | 14 | 972 |
| pooled | 296 | 31 | — |

Pooled grant rate 31/296 = 10.5%, which clears the pre-registered floor of 50.
That is the baseline this cell is scored against. Two cautions from the
section's own caption: 2024 is mostly unparsed (972 of 1,297 applications), so
its 20% rate rests on a partial poll; and the published cohort is unconditioned
on the escalation ladder while predicted applications are selected on it, so
the raw rate is a yardstick, not a conditioned prior for a response-requested
application. The section's caption already describes the rate as grounding the
scored base rate (not descriptive-only).

## Adjustment from the anchor: down to 0.06

The pooled 10.5% blends every substantive applicant class. The grants in that
pool are, from my general knowledge of the 2024–2026 emergency docket, dominated
by government applications (the Solicitor General as applicant) and by
state-party applications; private applicants against the United States grant
far less often, and criminal defendants seeking release from custody pending
certiorari almost never obtain a stay from the full Court. Specific drivers:

- **The relief is extraordinary in kind.** A stay of the Sixth Circuit's order
  is, functionally, an order releasing a defendant whom a court of appeals found
  dangerous by clear and convincing evidence on the basis of posts urging
  followers to take federal officers' guns. The Court does not use the emergency
  docket to override appellate dangerousness findings, whatever the standard of
  review question's merit.
- **The government opposes, and the SG's views carry weight here.** The
  response will emphasize the record of the posts, the "self-inflicted" harm
  point from the stay-denial order (Wagner agreed to trial continuances), and
  the looming mootness (trial set for Nov 3, 2026, with a stipulated 60-day
  extension possible). Mootness also undercuts the "reasonable probability of
  certiorari" prong.
- **The stay standard is conjunctive.** Even granting a real prospect that the
  deferential-review position wins on the merits (the application's Pierce /
  Highmark / Lakeridge framework is the stronger doctrinal reading, and the
  dissent below adopts it), the irreparable-harm and equities prongs cut toward
  the government on this record in the current Court's hands.
- **Upward pressure.** A requested response is a selective signal (64 of 367
  substantive applications in the statpack cohort), counsel is first-tier, the
  split is genuine, acknowledged by the panel author, and 5-4-3 deep, and a
  petition is already docketed. These keep me from going to the 0.02–0.03 I
  would assign a pro se or unrepresented release application.

Net: 0.06. The downward move from 10.5% reflects applicant class and the
nature of the relief; the residual above the floor reflects the response call
and the quality of the vehicle.

## The three increment claims

- **response-requested-increment 0.97.** Vacuous for this cell (the rung fired
  Oct 2, inside the record); the harness masks it. The number is the
  counterfactual hazard for a record like this one.
- **referral-increment 0.82.** Of 367 substantive applications in the statpack
  cohort, 178 were referred to the Court (48%) across all states, pending ones
  included; a response call is the strongest predictor of referral, and Justice
  Kavanaugh's practice on counseled applications is to refer rather than deny
  in chambers. I leave real mass (about 0.18) on a single-Justice denial or a
  disposition recorded without an explicit referral entry.
- **amicus-increment 0.30.** 66 of 367 substantive applications in the cohort
  carry an amicus (18%). This case's speech/ICE profile makes it likelier than
  average to draw a civil-liberties amicus, but the disposition window after
  Oct 8 is short, so I move only modestly above the cohort share.

## What I used and did not use

- Read in full: `AGENTS.md`, the predict prompt, `schemas/prediction.schema.json`,
  `event.yaml`, `record/context.json`, the snapshot, `documents.json`, and the
  provisioned application text. I did not read the prior arrival-moment
  predictions under `evt-motion-disposition/`, to keep this moment's forecast
  independent.
- Corpus: one `fedcourts query` for 2020s SCOTUS applications
  (`--include-applications`); it returned mostly time-extension grants and no
  ask filter exists, so it contributed texture (the recent application stream
  is overwhelmingly extensions) rather than a prior. Logged in `retrieval.md`.
- CourtListener MCP: one search located the Sixth Circuit docket (No. 26-1294,
  CourtListener docket 73117360, filed 2026-03-27); a search for the SCOTUS
  dockets returned nothing. Three follow-up calls (Sixth Circuit docket entries,
  the Sixth Circuit opinion, and the No. 26-391 docket) were refused with HTTP
  429 rate limiting (300/hour, shared key). Per the prompt I did not wait and
  did not seek any other path; the forecast rests on the provisioned inputs
  and the statpack. Nothing I retrieved touched this application's disposition.

## Where to discount me

- The applicant-class adjustment (10.5% → 6%) is from general knowledge of the
  emergency docket, not from a committed cut; the statpack carries no
  applicant-class or ask-type breakdown of grants. A reader who trusts only
  committed numbers should read me as "somewhat below baseline."
- The disposition vocabulary may not capture a hold or deferral: if the Court
  defers the application pending the petition, the event may sit unresolved
  for weeks, and if the Court grants certiorari on No. 26-391 while denying the
  stay, the application still resolves `denied`. Both read as non-grant on the
  scored axis, consistent with my number.
- I have not seen the government's response, which will exist within five
  days; a later moment (response-filed) will forecast from a better record.
