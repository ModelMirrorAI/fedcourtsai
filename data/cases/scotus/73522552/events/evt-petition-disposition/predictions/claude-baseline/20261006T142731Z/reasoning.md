# Why P(grant) = 0.10

## What I read

Provisioned inputs: `record/snapshots/2026-10-06.json` (the docket as polled October 6, 2026), `record/context.json` (mode `forward`, band `baseline` under sal-v4, Term 2025, distribution_count 1, no CVSG), `questions-presented.txt`, `petition.txt` (120 pp., truncated after the appendix began; the argument section is complete), and `brief-in-opposition.txt` (both respondents' briefs, 22 pp., full text). Beyond those: the committed statpack, two `fedcourts query` pulls, four web searches, and direct fetches of the supremecourt.gov dockets for this petition and four related ones, plus the Chamber of Commerce amicus brief, the petitioner's reply, and a Rules Committee suggestion (details in `retrieval.md`).

The CourtListener MCP server returned HTTP 429 (daily rate limit exhausted, roughly 55 minutes until reset) on all four calls I made, so I did not use it; the live-docket facts below came from supremecourt.gov fetches instead. The MCP outage degraded nothing material here because the relevant dockets are Supreme Court dockets that the Court publishes itself.

## The anchor

Context band is `baseline` under sal-v4; the statpack's band table is also sal-v4, so it is my anchor. Pooling the bracketed `reached` figure for `baseline` over the eight Term rows strictly before OT2025 (OT2017–OT2024) gives roughly **5.1%** (weighted n ≈ 11,600). The relist-count cut's bucket 1 (8.2% granted + 5.1% GVR) and the CVSG `none` bucket (4.0% + 2.3%) describe terminal states, not my forward hazard, so I read them for shape only. The Second Circuit's whole-docket grant rate (2.6% granted, 2.3% GVR) is a weak positive relative to other circuits. The case is Paid.

## Adjustments up

- **Response requested after both respondents waived** (August 19). A Justice's chambers wanted to hear from the other side. This is the strongest docket signal available at this moment.
- **Chamber of Commerce amicus in support of the petitioner**, Steven Engel (Dechert) as counsel of record, arguing the question is exceptionally important and recurring and that Congress forbade such awards in the PSLRA and condemned them in CAFA's findings. Business-side amicus support on a class-action question tends to be taken seriously by the current Court.
- **A conceded, entrenched split that is now 5–1 and growing**: the respondent concedes the conflict is "real"; the Federal Circuit joined the majority side in March 2026 (*NVLSP*); the Second Circuit itself has said awards are "likely impermissible under Supreme Court precedent" (*Fikes*); Judge Easterbrook wrote that "the Supreme Court must sooner or later resolve this conflict"; the Eleventh Circuit denied en banc over four dissents and will not move. The petition's "only this Court can overrule its own precedents" framing is the kind of argument that has drawn grants before.
- **A companion petition, No. 26-302, by the same petitioner on the identical question** (Fed. Cir., United States as a respondent; docketed September 8, 2026; respondents' time extended to November 9). Two live vehicles raise the chance the Court addresses the issue in at least one of them, and this is the cleaner of the two (private parties, final judgment, no government-fund wrinkle).
- The petitioner, though pro se, is an experienced class-action appellate lawyer, and the petition is a clean, single question of law.

## Adjustments down

- **The Court has declined this exact question three times in the last three Terms**, each with a decent vehicle:
  - *Johnson v. Dickenson*, No. 22-389 (from the Eleventh Circuit side, the class representative whose award was struck): four distributions and reschedules, denied April 17, 2023.
  - *Isaacson v. Meta Platforms*, No. 24-259 — **the same petitioner, the same question, the same posture**: respondents waived, the Court requested a response, BIOs came in, the petition was redistributed once and **denied at that first conference**, January 27, 2025.
  - *Dart v. Scott*, No. 24-464 (a county sheriff as petitioner, with a DRI amicus): denied February 24, 2025.
  That record says a response request on this question from this petitioner has already once gone nowhere, which is why I discount the August 19 signal well below what it would ordinarily be worth.
- **Lopsided split and low stakes in the case.** A $5,000 award in a $2.375 million settlement; the respondent's BIO argues (fairly) that the outlier circuit is internally divided and that the award's reasonableness was never contested. The Times' separate BIO asks for finality after six years.
- **Objector-petitioner, unpublished summary order.** The Court does grant from unpublished orders resting on published circuit law (the reply collects examples), but objector petitions from affirmed settlements are a poor-granting class.
- **Pending rulemaking.** A Rules suggestion (26-CV-4, from the Committee to Support the Antitrust Laws, February 2026) asks the Civil Rules Committee to amend Rule 23 to expressly permit reasonable service awards. The Court often prefers to let the rulemaking process address Rule 23 practice questions, and a Justice inclined to deny has a ready reason.
- **The United States waived in No. 26-302** (September 23), suggesting the Solicitor General does not regard the question as needing this Court's attention now.

## Net

From a 5% anchor, the response request, the Chamber's brief, and the growth of the split pull up toward 15%; the three recent denials, the near-identical *Isaacson v. Meta* trajectory, the lopsided split, and the rulemaking alternative pull back down. I land at **0.10**. I would not go below 0.07, because the Court's own precedents are squarely at issue and the amicus support is new; I would not go above 0.15, because a petition on this question with a requested response from this very petitioner was denied without a relist twenty months ago.

## The other claims

- **relist-increment 0.97.** The one distribution in the snapshot was for a conference that could not consider the petition once a response was called for. A redistribution after the October 2 reply is close to certain; the residual is dismissal or withdrawal before any distribution, which nothing suggests.
- **cvsg-increment 0.04.** See `predicted_reasoning.md`; the government's waiver in the companion is the main evidence.
- **summary-disposition-route 0.04** (conditional on grant). No intervening decision; a summary reversal of five circuits is not plausible.
- **dissent-from-denial 0.12** (conditional on denial). No separate writing accompanied the three prior denials as far as the dockets I fetched record; the Chamber's participation and the growth of the split raise the chance of a short statement respecting denial somewhat.

## Where to discount me

- I could not read the Chamber brief beyond its interest statement, summary of argument, and the opening of Part I, nor the reply beyond its first seven pages, because of extraction effort; neither omission seems likely to move the number.
- I have no corpus-conditioned rate for "response requested after waiver"; my discounting of that signal rests on one closely analogous docket (24-259) plus the general pattern, not a measured hazard.
- Whether the Court holds this for No. 26-302 or decides it alone is the main uncertainty about timing, not about the outcome; a hold would make the relist count larger without making a grant much likelier.
- The case is pending: the live docket fetched October 6, 2026 shows no entry after the October 2 reply, so no outcome was seen or used.
