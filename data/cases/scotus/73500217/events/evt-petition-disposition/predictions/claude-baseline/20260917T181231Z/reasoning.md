# Why 0.012

## What I read

- `record/context.json`: forward mode, band `baseline` under `sal-v4`, Term 2025,
  `distribution_count` 1, no CVSG, `signals_observable` true, snapshot 2026-09-17.
- `record/snapshots/2026-09-17.json`: paid petition, No. 25-1317, from the Ninth
  Circuit (No. 24-6664, unpublished memorandum of Nov. 10, 2025; rehearing denied
  Dec. 19, 2025). Extension granted by Justice Kagan; petition filed May 18, 2026;
  respondent **waived** its right to respond June 12, 2026; **distributed June 24,
  2026 for the Conference of 9/28/2026**. No call for a response, no amici.
- `record/documents/questions-presented.txt` and `petition.txt` (36 pages, full text,
  `empty_text: false`, not truncated). No brief in opposition exists because of the
  waiver, so my read of the opposing case is inference from the Ninth Circuit's
  ground as the petition describes it, not from a filed BIO.

## Anchor

Band `baseline`, frozen at prediction, so the yardstick is the bracketed `reached`
rate in the statpack's "Segment base rate by salience band (sal-v4)" table, pooled
over Terms strictly before OT2025 (the table renders OT2017-OT2026; OT2026 is empty
and OT2025 is this case's own Term). Pooling OT2017-OT2024 by weighted n gives
about **593 / 11,580 = 5.1%**. That is the rate faced by every paid petition that
ever reached the weakest private-petitioner band, and it is the bar I am scored
against.

Cross-checks from the same pack: the relist-count cut's `0` bucket (petitions that
*ended* undistributed-again) grants about 1.7% including GVRs; the CVSG `none` cut
about 6.3%; the ca9 originating-circuit cut about 3.2% (grant plus GVR). These are
terminal-bucket rates, read for shape only.

## Adjustments, all downward

1. **Waiver plus distribution without a call for a response.** A paid petition that
   the Court is seriously considering after a waiver almost always draws a call for
   a response before it is decided. The Court distributed twelve days after the
   waiver and asked for nothing. That is the ordinary shape of a denial at first
   conference and is the strongest single signal here.
2. **No genuine split.** The petition's "split" pairs (a) Court of Federal Claims
   Military Pay Act rulings that service members had standing under 10 U.S.C.
   § 1107a (Harkins, Bassen, Botello) and a district court in Doe #1-#14 against
   (b) the Ninth Circuit's holding that a civilian has no private right of action
   under 21 U.S.C. § 360bbb-3 against a private hospital. Different statute,
   different defendant, different cause of action. The petition concedes that
   every court to consider the civilian question has rejected it. No court of
   appeals is on the petitioner's side.
3. **Vehicle.** Unpublished, three-page memorandum affirmance of a Rule 12(b)(6)
   dismissal; the FDCA claim was one of five; solo-practitioner counsel; no amici.
4. **Doctrine.** The claim runs directly into 21 U.S.C. § 337(a), Buckman, and the
   Sandoval/Gonzaga line the current Court reaffirmed in Medina (2025). The
   petition's own authorities cut against it.
5. **Topic trajectory.** COVID-19 EUA vaccine-mandate petitions raising the
   § 360bbb-3 informed-consent theory have been denied repeatedly since OT2021,
   and the EUA posture has since lapsed, reducing forward importance.

Roughly: P(the Court calls for a response after all) about 0.05, times
P(grant | call for response) about 0.15, plus a small residual for a direct grant,
gives about 0.01. I round to **0.012**.

## The other claims

- **relist-increment 0.10.** Paid petitions in the scored segment see a second
  distribution about a quarter of the time overall, but that pool is dominated by
  petitions with responses on file or with a call for response pending. From a
  one-distribution, waived, unrequested state on the Long Conference the hazard is
  lower; the corpus query's recent granted cert priors all carried multiple
  distributions, which is the shape a live grant would show, and nothing here
  suggests it.
- **cvsg-increment 0.01.** Private-party dispute, no response requested; a CVSG
  before a call for response would be extraordinary.
- **summary-disposition-route 0.30.** The pack's grant family is roughly 47%
  summary overall, but that share is driven by GVRs on intervening decisions, and
  there is none here. Conditional on the improbable grant I lean plenary.
- **dissent-from-denial 0.03.** A statutory implied-right claim against a private
  party is a weak hook for the Justices who have written on mandate denials.
- **big_case_score 0.12.** Narrow, aging, private-party dispute.

## Retrieval and its limits

- CourtListener MCP: both search calls were **throttled (HTTP 429, 300/hour limit,
  about 14 minutes until available)**. Per the prompt I did not wait, did not fall
  back to REST, and proceeded on the provisioned inputs and the corpus tooling. I
  therefore did not read the Ninth Circuit memorandum itself or verify the
  disposition history of sibling § 360bbb-3 petitions beyond what I carry as
  general legal knowledge; discount points 2 and 5 accordingly.
- `fedcourts query` (see `retrieval.md`): the corpus surface has no text filter,
  so the two queries returned recency-ranked recent SCOTUS matters rather than
  topic-matched priors. I used them only for shape (recent granted cert petitions
  carried 3, 17, and 22 distributions; recent denials sat at 0 or 1).

## Where to discount me

I am confident in the direction and less so in the last decimal: the honest range
is 0.005 to 0.03. The one thing that would move me materially is a call for a
response before the conference; nothing on the snapshot suggests it. I know no
outcome for this case; today is 2026-09-17 and the conference is 2026-09-28.
