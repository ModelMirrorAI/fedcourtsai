# Rationale — P(unqualified grant) = 0.01

**The cell.** Interim stage, `moment: arrival`, `forward` mode. The provisioned
snapshot (`record/snapshots/2026-08-26.json`, provenance `truncated`, cutoff
2026-08-26) shows a single docket entry: "Application (26A245) for an
injunction pending appeal, submitted to Justice Barrett" (Aug 17, 2026),
docketed Aug 25, 2026. The frozen context carries the interim ladder at its
floor: `response_requested: false`, `referred_to_court: false`,
`amicus_briefs: 0`; `band: null`, which is the normal interim state, so I did
not derive a band or touch the cert band table.

**Published baseline.** The committed `metrics/statpack.md` carries "The
interim docket (applications)" with the scored-base-rate caption (not the
older descriptive-only one). This is an application-Term 2026 cell, so the
pool is Terms strictly before 2026: OT2025 contributes 178 resolved
substantive applications (16 granted) and OT2024 contributes 48 (14 granted) —
pooled 30/226 ≈ **13.3%**, which clears the pre-registered floor of 50
resolved. That is the yardstick this cell is scored against. (The prompt's own
example of a pool that misses the floor describes an OT2025 cell; against an
OT2026 cell the OT2025 Term joins the pool, and the section's arithmetic is
the authority.)

**Adjustment down, and why it is large.** The pooled 13.3% is measured over a
cohort dominated by counseled, often governmental, often referred-and-briefed
applications (the OT2024 slice alone runs 29.2% with heavy escalation-signal
counts). This application sits at the opposite extreme on every observable:

- **Pro se on both ends of the caption.** The counsel of record is the named
  applicant herself; the underlying case is a pro se emergency habeas by two
  family-member applicants against the local district attorney.
- **The ask carries the hardest standard.** An injunction pending appeal
  demands a "significantly higher justification" than a stay — it grants
  affirmative relief no court has yet ordered rather than preserving a status
  quo.
- **The posture below is as weak as it can be.** The district court (E.D. Wis.
  2:26-cv-01287) denied the habeas petition, dismissed the action, dismissed
  the emergency TRO motion as moot, and declined a certificate of
  appealability — all within six days of filing. The appeal (CA7 26-2577) is
  from that.
- **No escalation signal has fired**, consistent with an application headed
  for prompt single-Justice denial.
- **A near-exact recent analogue resolved as expected**: 26A237 (Golden v.
  Transunion), a pro se substantive application, denied four days after
  filing with no response requested and no referral. The Term-2026 row shows
  0 grants across 24 resolved substantive applications so far.

Grants in this population go to applications with institutional petitioners
and genuinely contested equities. I put this one at **0.01** — about as low as
I am willing to price any application given order-entry noise (a clerical or
classification surprise), and an order of magnitude under the pooled baseline.

**Ladder claims.** `response-requested-increment` 0.04: a response call is an
act of attention this filing is unlikely to draw. `referral-increment` 0.10:
somewhat higher, because some Justices refer even weak applications so the
denial issues from the full Court, and a renewed application after a
single-Justice denial is sometimes docketed as a referral on the same number.
`amicus-increment` 0.02: no organized interest exists here.

**Uncertainty and discounts.** I have not read the application's text — no
`record/documents/` were provisioned and I did not retrieve the filing itself
— so my read of the ask rests on the docket entry's own words plus the
district-court record. The district docket's entries 5–8 and 10–17 carry no
description text in RECAP, so the post-judgment motion practice there is
partly opaque; nothing in it plausibly changes the SCOTUS-side forecast. The
main tail risk on the disposition claim is not legal merit but resolver
behavior on an unusual order form; `withdrawn`/`dismissed` outcomes also
count as ungranted, which only reinforces the low number.
