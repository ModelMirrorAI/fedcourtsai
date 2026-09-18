# Reasoning — why P(grant) = 0.55

## What I read

- Provisioned snapshot `record/snapshots/2026-06-30.json` (cut at the CVSG
  moment under a `date` cut; 42 proceedings entries ending with the June 29
  CVSG and the grant of the Morley amicus motion).
- `record/context.json`: `mode: forward`, `band: high` under `sal-v4`,
  `distribution_count: 2`, `cvsg_date: 2026-06-29`, `term: 2025`,
  `signals_observable: true`.
- `record/documents/`: `questions-presented.txt`, the RNC petition (55 pp.,
  `empty_text: false`), and the combined brief-in-opposition file (100 pp.),
  which contains the Eakin/DSCC/DCCC/AFT brief in opposition plus the
  requested responses of Luzerne, Perry/Franklin, York, Lehigh, Northampton
  and other county boards. All were extracted with text; none truncated.
- `event.yaml`: `stage: cert`, `moment: cvsg`.
- `metrics/statpack.md`: the CVSG cut, the relist cut, and the per-Term
  sal-v4 salience band table.

## Anchor

Two committed figures point the same way:

- **CVSG cut (paid scored segment):** denied 62.0%, granted 29.4%, gvr 5.5%,
  dismissed 3.1% over 163 resolved petitions, so the grant family is about
  34.9%.
- **Band `high`, bracketed `reached` rate, pooled over Terms 2017–2024** (the
  rows strictly before this case's Term 2025; the table renders 10 Terms and
  2026 is empty): 34.95% over a weighted n of 898. For `high` the leading and
  reached figures coincide, because nothing sits above it on a private
  petitioner's ladder. This is the yardstick the evaluator scores against.

So the anchor is roughly **0.35**.

## Adjustments up (to about 0.55)

1. **A state petitioner on the same judgment.** The Commonwealth of
   Pennsylvania filed a companion petition (No. 25-967, "Vide" on this
   docket) asking the Court to review a federal court's invalidation of its
   own election statute. This docket's caption class is private (RNC), so the
   band anchor does not see that; it is the strongest single fact outside the
   anchor. The Court rarely leaves a federal appellate invalidation of a state
   election law unreviewed when the State itself asks.
2. **The Court's own attention signals stack.** Every respondent waived, the
   Court requested a response (April 1, 2026), and then CVSG'd after the
   second conference. The band folds these in, but the sequence (response
   requested on a fully waived docket, then CVSG) is toward the strong end of
   the `high` band.
3. **The Solicitor General is likely to support review.** The CVSG's value
   depends on what the SG says, and the Court follows the SG's cert
   recommendation most of the time. The current SG has aligned with the RNC's
   position in election-integrity litigation, and the federal government has
   a real institutional interest in the standard applied to rules governing
   federal elections. I put P(SG recommends grant, or GVR) around 0.7.
4. **The petition's cert case is strong on its own terms.** The panel itself
   acknowledged deepening circuit splits; the en banc court split 7–6 with
   dissentals by Judges Bove and Phipps; 21 states filed as amici; the case
   arrives after final judgment, not on the emergency docket; and Justice
   Alito's 2022 *Ritter* statement shows sitting Justices already have views
   about this exact requirement.

## Adjustments down (why not higher)

1. **Anderson-Burdick avoidance.** The Court has not taken a plenary
   Anderson-Burdick ballot-casting case since *Crawford* (2008) and has
   repeatedly denied petitions asking it to clarify the framework. A CVSG
   signals interest, not a commitment.
2. **The respondents' outlier argument has bite.** The BIO's strongest point
   is that no Pennsylvania election official defends the date requirement,
   the district court found no evidence it serves any interest, and the rule is
   a 1945 artifact. A Justice who wants to rein in Anderson-Burdick may prefer
   a vehicle where the State's interest is more than rational speculation.
3. **The *Baxter* mootness overhang.** The Pennsylvania Supreme Court heard
   argument in September 2025 on whether the date requirement violates the
   state Free and Equal Elections Clause and has not ruled as of the BIO (June
   2026). I could not confirm its status by retrieval (see below). I put
   P(that court strikes the requirement before this Court disposes of the
   petition) around 0.28. In that branch the Court most likely grants and
   vacates under *Munsingwear* (which resolves as `gvr`, a grant on the binary
   axis), but a denial that leaves the Third Circuit opinion standing, or a
   dismissal, is a real minority outcome. Net, mootness moves mass from
   plenary grant toward `gvr` and a little toward denial.

## Decomposition behind the numbers

- Non-moot branch (about 0.72): plenary grant about 0.55 of it (0.40
  overall); denial the rest (0.32).
- Moot branch (about 0.28): *Munsingwear* GVR about 0.6 of it (0.17 overall);
  denial about 0.3 (0.08); dismissal about 0.1 (0.03).
- Grant family = 0.40 + 0.17 = 0.57; I round to **0.55** to stay honest about
  the anchor's pull. `predicted_disposition: granted` because plenary grant is
  the modal grant outcome.
- `summary-disposition-route` = 0.17 / 0.57 ≈ **0.30**: the cert-order share
  of grants, almost entirely the mootness vacatur.
- `relist-increment` = **0.97**: after a CVSG the petition is redistributed
  once the SG files; only a withdrawal or a very early mootness dismissal
  avoids it.
- `cvsg-increment` = **0.01**: the CVSG is already on the docket; the harness
  masks this claim as vacuous.
- `dissent-from-denial` = **0.50**: Alito's demonstrated interest in this
  requirement makes a writing on denial roughly a coin flip; a mootness
  denial lowers it, a merits-based denial after a supportive SG brief raises
  it.
- `big_case_score` = 0.75: stakes scored on the QPs and posture, not on grant
  odds. A plenary ruling on the standard for neutral ballot-casting rules
  would be one of the most consequential election-law decisions in years; a
  *Munsingwear* exit would make the case much smaller than its filings.

## Where to discount me

- The largest judgment call is the SG's likely recommendation and the Court's
  deference to it; if the SG recommends denial or a hold, my number is too
  high by 10–15 points.
- My *Baxter* probabilities are guesses about a court whose timing I could not
  observe. If *Baxter* has already been decided, the whole decomposition
  shifts.
- I did not read any prior prediction for this case or event; this forecast
  is from the CVSG-moment record alone.
- CourtListener returned no docket entries for this docket and nothing for
  the companion petition or *Baxter*, so retrieval added no post-cutoff facts
  and the forecast rests on the provisioned inputs and the statpack. The
  corpus `fedcourts query` I ran returned recent granted priors for
  transfer-line purposes and general shape only; none was an Anderson-Burdick
  analogue, so I did not adjust on them.
- No outcome for this petition is known to me; nothing I retrieved disclosed
  one.
