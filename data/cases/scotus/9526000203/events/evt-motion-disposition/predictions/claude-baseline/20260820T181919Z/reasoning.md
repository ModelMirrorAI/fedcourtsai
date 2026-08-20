# Rationale — claude-baseline, 26A203, run 20260820T181919Z

**P(unqualified grant) = 0.70.**

## What the record shows

A `forward` interim cell at `moment: arrival`, snapshot of 2026-08-15. The
docket: the Solicitor General filed a stay application (26A203) for the
National Park Service and other federal parties on August 13, 2026, submitted
to the Chief Justice; on August 14 the Chief Justice requested a response due
August 18 at 12 p.m. — a four-day fuse. Frozen conditioning
(`record/context.json`): `response_requested: true`, `referred_to_court:
false`, `amicus_briefs: 0`, `band: null` (as an interim cell should be —
no cert-band anchor applies and I used none).

Date-bounded CourtListener retrieval on the case below (D.C. Cir. 26-5123,
entries on or before 2026-08-14 only) shows what the stay targets: on
August 7, 2026 a divided panel (Millett and Garcia; Rao dissenting, 35 pages)
affirmed the district court's modified preliminary injunction against the
White House construction project (defendants include NPS, DOI, GSA, the
Executive Office of the President, and the President), vacated the
administrative stay the circuit had entered on April 17, stayed its own
ruling fourteen days to allow Supreme Court review, and set the mandate for
August 21. The suit is APA/agency-review (historic-preservation claims); the
application therefore asks the Court to keep the injunction from taking
effect pending certiorari.

## Anchor

The committed statpack's interim section grounds the scored base rate. For a
Term-2026 application, the strictly-prior pool is application-Terms 2025 and
2024: 178 + 47 = 225 resolved substantive applications, 16 + 14 = 30 granted —
**pooled rate 13.3% (n=225)**, which clears the pre-registered floor of 50, so
a published baseline exists and that is my anchor. The section's caption
already states the scored-base-rate framing (not the older descriptive-only
caption). Two caveats I carried: the escalation-signal counts there are
right-censored and not as-at-prediction, so I read them for shape only; and
the scored population is selected on the escalation ladder, so my cell sits
systematically above the cohort behind that 13.3%.

## Adjustments (up from 13.3% to 0.70)

1. **The applicant is the United States, by the Solicitor General.** The
   pooled 13.3% is dominated by non-government applications, which almost
   always fail. The government's emergency applications in the 2024–2025
   Terms succeeded at a rate several multiples of the pooled figure — the
   Court granted the government relief in the large majority of its
   applications against lower-court injunctions of executive action. This is
   the single largest adjustment.
2. **The escalation ladder fired immediately.** A response requested within
   one day, on a four-day fuse keyed to the circuit's mandate date, is an
   affirmative act of attention; summary denial without a response call is
   the modal path for the applications behind the 13.3%, and that path is
   already foreclosed.
3. **A strong certiorari case on the government's own terms.** A published,
   101-page D.C. Circuit decision with a substantial dissent (Rao), on
   separation-of-powers questions about APA/NHPA review reaching the
   President and the Executive Residence — the kind of executive-power
   question this Court has repeatedly taken up on the emergency docket and
   resolved for the government.

## What holds me at 0.70 rather than higher

- **The denial-first collapse.** The interim resolver reads a mixed order as
  `denied`. A tailored stay — for instance, relief as to some construction
  activities but not others — is a live possibility on a preservation
  injunction, and it would score against me. I take perhaps 5–8 points off
  for this alone.
- **The equities cut unusually hard against a stay.** Construction and any
  demolition are irreversible in a way that a paused project is not; a stay
  arguably moots the merits. The circuit majority affirmed on that record,
  and the panel's own fourteen-day accommodation shows a court expecting
  Supreme Court engagement, not necessarily reversal.
- **Right-censoring and cohort mismatch** in the statpack's signal columns
  mean I cannot condition the published rate on the ladder properly; my
  government-applicant adjustment rests on general knowledge of the recent
  emergency docket rather than a committed conditioned cut, and a reader
  should discount it accordingly.

## Claim-level notes

- `interim-disposition` 0.70 — equals the top-level probability by contract.
- `response-requested-increment` 0.99 — the rung already fired on my record
  (requested August 14); the harness masks this claim as vacuous for my cell.
  The number records that a requested response is all but certain to stand at
  resolution.
- `referral-increment` 0.78 — real-world likelihood of full-Court disposition
  is higher (~0.9), but the claim resolves against the docket's parseable
  referral signal, and referral sometimes appears only inside the disposing
  order's text; I hedge for that observation channel.
- `amicus-increment` 0.93 — the frozen count is 0, but the application
  docket's attorney list already names counsel for Members of Congress, the
  Society for the Rule of Law, Campaign Legal Center/CREW, and the State of
  Indiana — largely the D.C. Circuit amici reassembling. Not 0.97+ only
  because the compressed timeline (disposition likely within days) leaves a
  narrow filing window and the count must actually register on the docket.

## Candor

- I deliberately **date-bounded** all live retrieval about this case to
  entries on or before 2026-08-14, although forward mode permits unrestricted
  retrieval: today (2026-08-20) postdates the August 18 response deadline, so
  an unbounded query would very likely have surfaced the application's own
  disposition, which the prompt treats as a mis-provisioning signal to avoid.
  Nothing outcome-revealing surfaced; I do not know the disposition.
- From training knowledge I know the underlying project (the White House
  ballroom construction and the 2025 East Wing demolition) and the general
  pattern of the Court's 2025-era emergency docket; I know no outcome for
  this application, whose filing postdates my training data.
- The statpack has no conditioned cut for government-applicant applications,
  so the largest single adjustment in this forecast is the least anchored —
  the honest error bar on 0.70 is wide, perhaps ±0.12.
- `fedcourts query` returned cert petitions rather than application priors
  (no application-kind filter exists), so corpus priors contributed little
  beyond the statpack itself.
