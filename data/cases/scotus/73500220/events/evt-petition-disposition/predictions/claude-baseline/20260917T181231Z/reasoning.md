# Reasoning — why P(grant) = 0.02

## What I read

Provisioned inputs: the snapshot `record/snapshots/2026-09-17.json`,
`record/context.json` (mode `forward`, band `baseline` under `sal-v4`,
`distribution_count` 1, no CVSG, Term 2025, paid), `documents.json`,
`questions-presented.txt`, and `petition.txt` (240 pages, `truncated: true`;
I read the QP, statement of the case, the circuit-split section, the vehicle
section and the conclusion, and the caption of the appended Third Circuit
opinion). No brief in opposition exists: the docket shows the United States
**waived** its right to respond on June 11, 2026. The petition was
distributed once, for the Long Conference of September 28, 2026. The
statpack (`metrics/statpack.md`) supplied the base rates.

## Anchor

`context.band` is `baseline` and the segment table's heading names `sal-v4`,
matching `salience_version`, so the table is a valid anchor. Pooling the
**bracketed `reached`** baseline figures over Terms strictly before 2025 (OT2017
to OT2024, the eight prior rows the table renders; `n` = 1643, 1524, 1399,
1739, 1500, 1192, 1312, 1271) gives a weighted rate of about **5.1%**. That
is the rate for a private paid petition that has reached the baseline band,
including those that later climb into `elevated` or `high`.

For shape rather than anchor: the relist-count cut's terminal relist-0 bucket
grants (plus GVR) at about 1.7%, the CVSG `none` bucket at about 6.3%, and the
Third Circuit's modern-cert grant family at about 2.4%.

## Adjustments (net: down, from ~5% to 2%)

Down:

- **The United States waived its response.** The Court does not grant a paid
  petition without a response on file; a grant here would require a
  call-for-response first. The waiver is the SG's judgment that the petition
  presents nothing needing an answer. This is the single largest negative.
- **The split is soft.** The petition's "conflict" pits the Third and Seventh
  Circuits' categorical rule against the Second Circuit en banc (*Farhane*,
  2024) and the Eleventh (*Bauder*). But *Farhane* concerned denaturalization
  that leads to deportation, which the Second Circuit itself treated as a
  "straightforward application of *Padilla*," and *Bauder* was an affirmative
  misadvice case, a distinct doctrine. No court of appeals has held that
  failure to warn of a civil collateral estoppel or monetary consequence is
  constitutionally deficient. The petition's own survey concedes most
  circuits confine *Padilla* to its facts.
- **Vehicle problems.** The claim arrives on § 2255 collateral review; the
  district court denied an evidentiary hearing; the facts about what counsel
  knew of the qui tam action and what the Patels understood are contested and
  undeveloped; prejudice is doubtful given a stipulated loss of $4.8 million,
  restitution in the same amount, and an affirmed FCA judgment. The Court
  could also see counsel's performance as a fact-bound *Strickland* question
  the Third Circuit could have resolved on the alternative ground. The
  consequence at issue (treble-damages exposure in a civil suit) is far from
  deportation's severity and automaticity, so the case is a poor one for the
  extension the petitioners want.
- **Petitioner profile.** Private petitioners represented by a regional firm
  rather than a repeat Supreme Court advocate; no amicus support on the
  docket; the appeal was submitted on the briefs below.
- **The Court's record on *Padilla* extensions.** Since *Chaidez* (2013) the
  Court has repeatedly denied petitions asking it to extend *Padilla* to
  parole eligibility, sex-offender registration, civil commitment, and
  professional licensing consequences. I know of no signal that a majority
  wants to revisit the direct/collateral line.

Up (modest):

- The Third Circuit's opinion is **precedential**, squarely adopts a
  categorical rule, and rehearing en banc was denied, so the legal question is
  cleanly presented rather than buried in facts.
- The Second Circuit's en banc *Farhane* (2024) does create genuine tension
  in reasoning even if not in holding, and the question recurs constantly.
- The government's waiver leaves open a call for response, which would raise
  the odds materially if it happened; I price that path inside the 2%.

## Claims

- `disposition` 0.02 (equals `probability`).
- `relist-increment` 0.14. The record shows one distribution (the Long
  Conference). The terminal population is relisted at least once roughly a
  quarter of the time, but that pool is dominated by petitions the Court is
  actually weighing. For a waived, baseline-band petition the realistic route
  to a second distribution is a call for response after the Long Conference or
  a reschedule; the harness counts either as a distribution, so I sit above
  the bare relist hazard.
- `cvsg-increment` 0.005. The United States is the respondent; a CVSG is
  structurally inapplicable. Not exactly zero only because docket-parsing
  edge cases exist.
- `summary-disposition-route` 0.2 (conditional on a grant). No intervening
  decision supports a GVR and the opinion below is reasoned, so plenary review
  is the likelier route on the rare grant branch; the prior share of grants
  disposed of in the cert order is substantial, which keeps me off the floor.
- `dissent-from-denial` 0.03 (conditional on denial). Below the paid-petition
  norm: no acknowledged split, no sympathetic-liberty stakes, no response on
  file for a Justice to engage with.

## big_case_score = 0.4

A holding on whether the Sixth Amendment reaches non-deportation collateral
consequences would affect plea practice nationwide, which is real doctrinal
significance. The concrete stakes here (collateral estoppel in a civil False
Claims Act case) are narrow and the case would draw little attention outside
the criminal-defense bar. Stakes, not odds.

## Uncertainty and where to discount me

- I could not verify the split against the lower-court opinions themselves:
  the CourtListener MCP server returned HTTP 429 (rate limit, about fifteen
  minutes of throttle) on my first search, so I worked from the petition's
  characterization of the circuit cases plus my own knowledge of *Padilla*,
  *Chaidez*, *Farhane*, and *Bauder*. No REST fallback was attempted.
- The petition is truncated in provisioning, so I did not read the whole
  appended Third Circuit opinion; my reading of its holding is from the
  petition's quotations of it.
- The biggest swing factor is a call for response after the Long Conference.
  If one issues, this petition's odds move to the several-percent range; if
  the Court denies on the first October order list, the 2% was, if anything,
  generous.
- One data oddity: the docket dates the petition filing entry "Apr 08 2026"
  although the extension ran to May 16, 2026, the PDF is stamped May 15, and
  the case was docketed May 28. I treat the filing as late-May 2026 and the
  entry date as a supremecourt.gov artifact; it does not affect the forecast.
