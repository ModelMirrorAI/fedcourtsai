# Why 0.20, and where to discount me

## What I read
- Provisioned snapshot `2026-09-09.json` (cutoff 2026-09-09, `date` cut, forward
  mode). It shows one entry: the petition filed 2026-09-03, response due
  2026-10-08. Paid docket, Term 2026, Federal Circuit below (No. 2024-1757,
  decided 2026-03-20, rehearing denied 2026-06-05). Petitioner Eric Alan Isaacson
  is a class-member objector appearing for himself; respondents are the three
  named nonprofit plaintiffs and the United States (Solicitor General as counsel).
- `record/context.json`: `band: baseline`, `salience_version: sal-v4`,
  `distribution_count: 0`, `cvsg_date: null`, `signals_observable: true`.
- `documents/questions-presented.txt` (complete) and `documents/petition.txt`
  (140 pages, **truncated** — the text ends mid-section II, so the vehicle
  argument in section III and the conclusion were not available). No BIO exists yet.

## Anchor
Cert-stage arrival cell, private petitioner (an individual objector; the
government party is a respondent, so the caption class is `private`). The
statpack's sal-v4 band table carries a `baseline` column, so the class floor is
its bracketed `reached` rate pooled over the Terms strictly before OT2026 that the
table renders (OT2017–OT2025, 9 of the pack's 10 Terms): **5.0%** (n = 12,720
weighted). That is the yardstick the evaluator scores this cell against. The
modern discretionary-cert table's grant family is ~2.8%, the relist-0 cut's 1.7%
is the terminal-state figure the prompt says not to use, and the CAFC row of the
circuit cut (granted 3.1%, gvr 1.5%) is in the same range as the floor.

## Adjustments up (to ~0.20)
1. **The companion petition drew a call for a response.** *Isaacson v. Moses*,
   No. 25-1411 (2d Cir., same QP, same petitioner), was docketed 2026-06-23; both
   respondents waived; it was distributed for the 2026-09-28 conference; on
   2026-08-19 the Court **requested a response**; on 2026-09-18 both respondents
   filed BIOs and the **Chamber of Commerce filed an amicus in support of
   petitioner** (Dechert, Steven Engel as counsel of record). A CFR is an
   affirmative act of attention by at least one Justice on exactly this question,
   and it is the single biggest reason this number sits well above the floor. It
   is public information postdating my snapshot but predating my run; in forward
   mode that is legitimate signal, disclosed in `flags.json`.
2. **The split is real, deep and acknowledged.** Five circuits against the
   Eleventh; Judge Jacobs (CA2, *Fikes*) wrote that his court is "on the wrong
   side of a circuit split," Judge Easterbrook (CA7, *Scott v. Dart*) that "the
   Supreme Court must sooner or later resolve this conflict," and Judge Jill
   Pryor's en banc dissent in *Johnson* that it "will be up to the Supreme Court."
   The question recurs in essentially every common-fund class settlement.
3. **Prior serious consideration.** *Johnson v. Dickenson*, No. 22-389 (the
   Eleventh Circuit case itself), was distributed for four conferences with
   supplemental briefing before denial on 2023-04-17. The Court has already
   spent real attention on this question once.

## Adjustments down (why not higher)
1. **This is the weaker of the two vehicles.** A Little Tucker Act class action
   against the United States in the Federal Circuit, $10,000 awards, a short
   published order, and a pro se objector-petitioner who is also the petitioner
   in 25-1411. If the Court grants, 25-1411 is the natural lead; 26-302 gets
   there only by consolidation or by a hold that ends in a GVR. My decomposition:
   P(Court takes the question this cycle) ≈ 0.28; given that, P(26-302 granted
   in any form) ≈ 0.7 (roughly 0.35 consolidated grant + 0.6 × ~0.55 hold-then-GVR
   + a little for a solo grant). Product ≈ 0.20.
2. **The Court passed once already**, despite a four-conference look, and the
   per-case dollar stakes are small; the Court may prefer to let the Rules
   Committee address incentive awards.
3. **The federal respondent waived** on 2026-09-23, so the government signals no
   interest in the question — consistent with the fund, not the Treasury, paying
   the awards.
4. I do not know how the Court read the 25-1411 BIOs, and the class respondents
   here have not yet answered; a strong BIO on objector standing or on the
   Federal Circuit posture would push this down.

## The other claims
- `relist-increment` 0.97: from zero distributions, "at least one more" is
  simply "distributed at all," which every petition that is not withdrawn or
  dismissed pre-conference is. The residual is Rule 46 dismissal or withdrawal,
  neither plausible for this petitioner.
- `cvsg-increment` 0.01: the United States is a party and has waived.
- `summary-disposition-route` 0.45: conditional on a grant, the hold-then-GVR path
  is nearly as heavy as a consolidated plenary grant in the decomposition above.
  No intervening decision exists today, so any GVR would follow a merits ruling
  in 25-1411.
- `dissent-from-denial` 0.08: separate writings on denial are rare (low single
  digits overall); a CFR'd split raises it, but a denial after an affirmance in
  the companion would carry none, and the 2023 denial in *Johnson* had none.
- `big_case_score` 0.35: doctrinally consequential for class practice, small
  dollars, low public salience.

## Uncertainty and discounts
- The cell's own baseline is an arrival snapshot with one entry; nearly all my
  lift comes from the companion docket, read off supremecourt.gov, not from
  anything in the provisioned record. If that read is wrong the number should be
  near 0.06.
- Corpus priors (`fedcourts query`) could not be filtered to this legal question
  (no keyword filter), so they contributed only the shape of recent SCOTUS rows;
  the statpack carried the base rates. Statpack vintage: the committed
  `metrics/statpack.md` in this checkout (OT2026 row still nearly empty).
- CourtListener returned no SCOTUS docket entries for any query; the companion
  docket and this docket's later entries came from supremecourt.gov's public
  docket JSON via web fetch. No disposition of 26-302 surfaced anywhere.
- I have no training-data knowledge of how 25-1411 or 26-302 was resolved; my
  knowledge of the split predates these filings and matches the petition's account.
