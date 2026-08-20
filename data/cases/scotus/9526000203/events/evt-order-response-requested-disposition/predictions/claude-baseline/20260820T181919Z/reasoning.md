# Rationale — why P(unqualified grant) = 0.80

## Anchor

The statpack's "The interim docket (applications)" section grounds the scored
base rate. My cell is an application-Term 2026 docket (26A203), so the pool is
the resolved substantive slice of strictly-prior Terms: 2025 (178 resolved, 16
granted) and 2024 (47 resolved, 14 granted) — 30/225 ≈ **13.3%**, which clears
the pre-registered 50-resolved floor, so this cell has a published baseline.
The section's own caveats travel with it: the pooled cohort is unconditioned on
the escalation ladder while this cell was selected on it (response requested is
the strongest rung), parse coverage is uneven across the two Terms, and the
escalation-signal columns are right-censored — so the 13.3% is the scored
yardstick, not a description of this application's situation.

## Adjustments up (large)

1. **The applicant is the United States.** The Solicitor General is counsel of
   record and the defendants include the President and the Executive Office of
   the President. Over the last two Terms the federal government's substantive
   emergency applications have been granted at a rate far above the pooled
   slice — from my general knowledge of the OT2024–OT2025 emergency docket, the
   government prevailed in the large majority of its applications (with rare
   exceptions such as the USAID-payments vacatur denial). The pooled 13.3% is
   dominated by prisoner and private applications and badly understates a
   government applicant. This is the single largest adjustment.
2. **The court below invited this application.** The D.C. Circuit stayed its
   own affirmance for fourteen days expressly "to allow the Defendants, if they
   choose, to seek Supreme Court review," and reset its mandate to August 21.
   A merits panel that expects its ruling to be tested is a strong signal the
   application is substantial, and the 2–1 split with a 35-page Rao dissent
   hands the applicant a ready-made roadmap.
3. **The escalation ladder.** The Chief Justice called for a response the day
   after filing, on a four-day clock timed to beat the mandate — an affirmative
   act of attention and the strongest observable rung.
4. **The posture favors a stay on this Court's revealed equities.** The
   injunction subjects the President's management of the White House complex to
   judicial supervision; the current majority has repeatedly credited exactly
   that kind of separation-of-powers harm as irreparable, and the reviewability
   question (APA/NHPA applied to presidential action, against Franklin v.
   Massachusetts) gives it a clean likelihood-of-success hook.

## Adjustments down

- The government lost below **after full expedited merits consideration** — a
  101-page opinion affirming the injunction, not a motions-panel ruling — which
  is a stronger record against a "fair prospect of reversal" than the typical
  shadow-docket posture.
- The equities are weaker than in the immigration/personnel line: the claimed
  harm is delay to a construction project, and the East Wing demolition that
  drove the suit is already done, so the status quo costs the government less.
- **The denial-first collapse.** The event resolves as an unqualified grant
  only; a stay granted in part (e.g., preserving some site-work restriction)
  reads as ungranted. I put ~5% mass there.

## Landing

Starting from the 13.3% pooled baseline, the government-applicant and
invited-application signals move this application into a reference class whose
grant rate I judge to be in the 0.75–0.85 range; the strong merits loss below
and the partial-grant risk keep me at the lower-middle of that band.
**P(unqualified grant) = 0.80**, disposition `granted`, `granted = 1`.

## Claims

- `interim-disposition` 0.80 — equals the top-level probability, as required.
- `response-requested-increment` 0.03 — the rung already fired on my record
  (context `response_requested: true`), so the harness resolves this claim as
  vacuous for this cell; the number is my probability of a further,
  post-prediction call for supplemental response, which is low.
- `referral-increment` 0.85 — context shows `referred_to_court: false`. A
  full-Court disposition of a contested application of this profile is the
  overwhelming norm once a response is called for; the residual mostly prices
  the docket never recording a formal referral entry.
- `amicus-increment` 0.93 — frozen count 0, but the snapshot's attorney roster
  already carries six non-party counsel of the amicus-filing kind, several of
  whom filed amicus briefs below; the short window to disposition is the only
  real brake.

None of the three increments has a published baseline; they are banked, and I
have stated them as carefully as the scored claim.

## Votes and big-case score

The vote block is optional here and unscored at this stage; I include a 6–3
lineup (grant: Roberts, Thomas, Alito, Gorsuch, Kavanaugh, Barrett; deny:
Sotomayor writing, Kagan, Jackson) as my honest read of the recent
emergency-docket pattern in executive-power cases. Big-case score 0.85: the
subject (the White House itself), the defendant (the President), and the
doctrinal stakes (reviewability of presidential action) make this among the
most-watched applications of the Term regardless of outcome.

## Uncertainty and where to discount me

- My government-applicant adjustment rests on training knowledge of the
  OT2024–OT2025 emergency docket (knowledge through early 2026), not on a
  committed corpus cut — the statpack publishes no applicant-class or
  ladder-conditioned rate. That is the biggest single discount: if the
  government's recent win rate were materially lower than I recall, my number
  should come down toward 0.6.
- The lower-court posture (the August 7 D.C. Circuit judgment, the 14-day
  self-stay, the Rao dissent) came from CourtListener retrieval of the D.C.
  Circuit docket, not from the provisioned snapshot, which carries only the two
  SCOTUS application entries. That material predates my snapshot cutoff
  (2026-08-15) and is legitimate forward signal; it is decisive here, and is
  flagged in `flags.json` as good hygiene.
- I deliberately stopped retrieval short of anything that could surface this
  application's own disposition (the response fell due August 18 and today is
  August 20, so a ruling or administrative stay may already exist). I did not
  encounter it and have predicted as if undecided.
- Corpus freshness: the priors query I ran returned rows with
  `last_live_polled` of 2026-08-19/20, so the corpus blob is current to within
  a day; the query itself (recency-ranked applications) surfaced mostly
  time-extension dockets and did not move my number.
- The snapshot is marked `snapshot_provenance: "truncated"` and its attorney
  roster appears to include post-cutoff amicus-counsel appearances while the
  frozen context says `amicus_briefs: 0`; I treated the frozen context as the
  state my increment claims resolve against, per the contract, and noted the
  mismatch in `flags.json`.
