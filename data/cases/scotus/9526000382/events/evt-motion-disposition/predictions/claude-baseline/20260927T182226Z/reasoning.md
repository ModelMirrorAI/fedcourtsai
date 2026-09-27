# Why these numbers

## What I read

- **Snapshot** `record/snapshots/2026-09-18.json` (cut kind `arrival-position`, anchored at entry 0): one entry, the September 17, 2026 submission of application 26A382 to Justice Sotomayor. No response requested, no referral, no amicus at the frozen moment. Docketed September 22; lower court is the Appellate Division, Second Department (No. 2026-04501).
- **Application text** `record/documents/application.txt` (38 pages, fetched, not truncated, not empty). Applicants Strulovitch and two LLCs, represented by Dechert (McGinley, Engel) and the Notre Dame Religious Liberty Clinic, seek a stay of a Westchester County commercial-division preliminary injunction (entered April 2026) that (1) bars Strulovitch from furthering any proceeding before a beis din concerning the parties' nursing-home ownership dispute and (2) orders him to take all steps necessary to have the beis din withdraw the seruv it issued against Bain. The trial court denied a stay from the bench; an individual Appellate Division justice denied interim relief on May 7, 2026; the motion for a stay pending appeal has been fully briefed since May 21 and remains undecided despite a July 20 letter. Jurisdiction is pleaded under the All Writs Act and 28 U.S.C. 2283, with a fallback that the order can be treated as final under 1257 (citing Nash, Skokie, Cox Broadcasting). Merits: the order is an individualized, non-general rule so Smith does not apply and strict scrutiny does; the compelled-withdrawal command is compelled speech and coerced religious exercise (Barnette, Wooley, Janus, Kennedy) and intrudes on ecclesiastical decisions (Watson, Kedroff, Milivojevich). The application cites Yeshiva University v. YU Pride Alliance for its exhaustion posture and Malliotakis v. Williams (2026, Alito concurring) for All Writs authority over state proceedings.
- **Context** `record/context.json`: mode `forward`, `band: null`, `response_requested: false`, `referred_to_court: false`, `amicus_briefs: 0`, term 2026, cutoff 2026-09-18, snapshot provenance `truncated`.
- **Statpack** `metrics/statpack.md`, section "The interim docket (applications)". Its caption already carries the scored-base-rate language (not the older descriptive-only caption).

## Anchor

Application-Term 2026, so the pool is application-Terms 2016 through 2025. Only two of those rows carry parsed substantive applications:

| Term | resolved (subst.) | granted | unparsed |
| --- | --: | --: | --: |
| 2025 | 226 | 17 | 0 |
| 2024 | 70 | 14 | 972 |

Pooled: 31 of 296, a grant rate of about 10.5%, which clears the 50-resolved floor. Term 2024 is only partly parsed (972 unparsed), so the pool leans on Term 2025. This rate is over every substantive application, most of them pro se or IFP stay requests with no realistic prospect; the scored cohort sits higher on the escalation ladder than that pool, as the pack itself warns.

## Adjustments from 10.5% to 0.17

Upward:
- **Escalation already under way.** In forward mode I fetched the live docket page: a response was requested September 23 (due September 28) and Becket submitted an amicus brief September 25. A response request is the interim analogue of a CVSG and moves this application into the minority of substantive applications the Court looks at seriously. The pack's raw signal counts (64 response-requested out of 367 substantive) show how selective that rung is.
- **Merits strength.** The compelled-withdrawal provision is an unusually stark order: it directs a litigant to petition his own clergy to reverse a religious ruling he agrees with. Several current Justices have been receptive to free-exercise and compelled-speech claims, and the applicants' counsel (Engel, McGinley, Becket-adjacent clinic) are repeat players who do not bring hopeless applications.
- **Exhaustion better than Yeshiva University.** In Yeshiva University (2022) the 5-4 majority denied a stay of a New York trial-court order because state appellate avenues for expedited or interim relief were untried, and said applicants could return if they obtained neither. Here an Appellate Division justice denied interim relief and the stay motion has sat undecided for four months, which is closer to the condition that majority named.

Downward:
- **Posture.** This is a stay of a state trial court's interlocutory preliminary injunction while the state appeal is pending. The Court almost never grants such relief. The finality problem under 1257 is real; the All Writs and 2283 theory is the applicants' primary hook and the Court has been reluctant to use it against state courts (the application's own Malliotakis citation is to a concurrence on a denial).
- **A partial order counts as denial.** The two provisions are separable, and a Court inclined to help would most naturally stay only the compelled-withdrawal command. The resolver reads a mixed order denial-first, so that plausible shape lands in my complement.
- **Mootness risk.** The response request may prompt the Appellate Division to rule on the pending motion, after which the application is withdrawn or dismissed, both ungranted.
- **Private commercial dispute.** No government party, no injunction against a statute or policy; the Court's grants on the interim docket over the pooled Terms are dominated by government applicants.

Net: roughly 0.17. I would not defend anything above 0.30 or below 0.10.

## The increments

- `response-requested-increment` 0.97: the rung fired on September 23, after my frozen moment. Forward mode permits me to see this; I disclose it in `flags.json`. The residual is for the harness resolving against something other than the entry I saw.
- `amicus-increment` 0.97: one Becket submission on September 25, counted under the submitted-English form. Same disclosure.
- `referral-increment` 0.75: not yet referred as of the docket page fetched today (September 27). Circuit Justices who call for a response on a contested, counseled First Amendment application nearly always refer it; the residual covers an in-chambers denial by Justice Sotomayor and a withdrawal or dismissal before referral.

## Uncertainty and where to discount me

- The base-rate pool rests almost entirely on Term 2025 plus a partly parsed Term 2024; the interim section's coverage is thin, and the published number is unconditioned on the ladder my cell sits on.
- I have not read Bain's response (not yet filed); the state-court record's account of the seruv's communal consequences and of any bad faith in the beis din filing could shift the equities.
- Two of my four claims are stated with knowledge of post-snapshot docket entries. That is the ordinary forward shape under the prompt, but it means the response-requested and amicus increments measure nothing about forecasting skill for this cell.
- The web search tool returned a machine-written summary claiming the application had been granted on August 24, 2026 with dissents. That date precedes the application's own filing and the authoritative docket page shows it pending, so I treated the summary as fabricated and did not use it. It is disclosed in `flags.json`.
- `fedcourts corpus-info` raised an exception in this cell (no local blob and the read-only connect failed), so I cannot quote a corpus vintage; the priors returned by `fedcourts query` include Term 2026 dockets numbered after this one (through 26A408), so the blob is at least as fresh as the last few days.
- MCP: one CourtListener docket search for 26A382 returned zero results (CourtListener does not carry SCOTUS application dockets); the docket state came from the Supreme Court's own docket page.

## Big-case score

0.42. Doctrinally interesting and closely watched within the religious-liberty bar and Orthodox community, with organized amicus interest already, but a private commercial dispute over a nursing home with no governmental defendant and a fact-bound remedy.
