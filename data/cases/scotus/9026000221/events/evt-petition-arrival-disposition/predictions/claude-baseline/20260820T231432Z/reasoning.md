# Rationale for the numbers (claude-baseline, run 20260820T231432Z)

## Cell posture

Forward-mode arrival cell (`moment: arrival`): the petition was docketed
August 20, 2026 (No. 26-221, paid) and the record shows zero distributions, no
CVSG, and no BIO — by construction. Frozen context: `band: baseline` under
`sal-v3`, `distribution_count: 0`, `term: 2026`, `signals_observable: true`.
Provisioned inputs: the 2026-08-21 snapshot (docket header plus three
proceedings entries — the 26A15 extension application, its grant by Justice
Alito, and the August 17 filing) and extracted text of the 314-page petition
including the questions presented (`empty_text: false` on both; no BIO exists
yet to fetch).

## Anchor

Per the arrival-moment rule, I anchor on the arrival population's own rate:
the **weakest band's bracketed `reached` figure** in the statpack's "Segment
base rate by salience band (sal-v3)" table — the whole paid scored segment,
unconditional on trajectory — pooled over the rendered Terms strictly before
this case's Term (OT2017–OT2025, all nine prior rows the table renders). That
pool is ~857 weighted grants over n≈13,163, i.e. **~6.5%**. The context's
`salience_version` (sal-v3) matches the table's heading, and the frozen band
(`baseline`) is the weakest band, so the anchor and the scoring yardstick
coincide. This is not a federal petitioner, so the `federal`-class arrival
carve-out does not apply.

## Adjustments — why 0.72, an order of magnitude above the anchor

The anchor is the rate for an undifferentiated paid petition at docketing.
This petition's pre-docket features put it in the extreme right tail of
cert-worthiness, and every one of them is visible at arrival (no docket
signal is being inferred):

1. **The en banc Fifth Circuit expressly declared a Supreme Court precedent
   no longer good law.** The 9–8 en banc majority (Duncan, J.) held that Stone
   v. Graham did not survive Kennedy's abrogation of Lemon and upheld a
   statute the petition credibly describes as "nearly identical" to the one
   Stone struck down. Lower-court refusal to follow a directly controlling
   precedent is among the strongest known cert triggers (Rodriguez de
   Quijas / State Oil v. Khan / Bosse-type postures are granted at very high
   rates), and the petition documents an acknowledged methodological split:
   the Second and Seventh Circuits (Jusino; Childs) hold that Lemon-era
   precedents bind until this Court overrules them, while the Fifth now holds
   the opposite.
2. **Exceptional, still-escalating national stakes.** Statutes mandating
   classroom Ten Commandments displays are enacted in Texas, Louisiana,
   Arkansas, Alabama, and Tennessee, with litigation pending in the Eighth
   Circuit (Stinson, No. 26-1722) and roughly two dozen legislatures active.
   The disuniformity is concrete: the mandate is enforceable in the Fifth
   Circuit and enjoined or presumptively unconstitutional everywhere Stone
   binds.
3. **Both sides effectively want review.** Louisiana has already filed a
   conditional cert petition in the companion Roake litigation; Texas's
   interest is a nationwide validation of S.B. 10, and the petitioners' is
   reversal. Defensive-denial dynamics exist on both wings but are weaker
   than usual because leaving the en banc decision standing is itself a
   substantive outcome (Stone dead in three states and spreading).
4. **Vehicle quality.** The en banc court found the claims justiciable and
   reached both merits questions on a developed evidentiary record; the
   parallel Roake case went off on ripeness, making Nathan the clean vehicle.
   Elite counsel (Simpson Thacher; ACLU; Americans United; FFRF). The
   interlocutory (preliminary-injunction) posture is a mild negative, but the
   Court granted Mahmoud in the same posture in 2025.
5. **Court behavior.** This Court has granted essentially every major
   religion-in-public-schools case presented to it in the last decade
   (Espinoza, Carson, Kennedy, Mahmoud), and four Justices who share the en
   banc majority's view of Stone have an affirmance to gain from a grant.

Against a grant: the Court could deny and let the Eighth Circuit create a
crisp post-Kennedy split first (percolation), or a wing uncertain of five
merits votes could deny defensively; arrival-time uncertainty is also real —
no BIO exists, and an unforeseen vehicle problem could yet surface. Those
scenarios, plus the residual base-rate discipline of a petition that has not
yet even been distributed, keep me at **0.72** rather than higher. I
considered 0.5–0.6 (more weight on percolation/defensive denial) and 0.8+
(treating precedent-defiance as near-automatic); 0.72 reflects that the
identifiable deny scenarios are individually plausible but each requires the
Court to tolerate an en banc court having overruled Stone for it.

## Claim-level numbers

- `disposition` 0.72 — restates the top-level probability. Most of the mass
  is a plenary grant; `granted` = 1 and `predicted_disposition` = `granted`.
- `relist-increment` 0.97 — from a frozen `distribution_count` of 0, this
  resolves true on the first distribution. A counseled, paid petition in a
  live controversy essentially always reaches a conference; the residual 3%
  covers pre-conference dismissal/withdrawal or docket anomalies.
- `cvsg-increment` 0.03 — no federal party or program; the SG will
  participate uninvited if at all (as the United States did in the companion
  Louisiana litigation). The statpack's CVSG cut (CVSG in ~1% of the paid
  scored segment) supports a low number; this case's ideological salience
  makes an invitation even less necessary.
- `summary-disposition-route` 0.05 — conditional on a grant. Petitioners ask
  for summary reversal or GVR first, but there is no intervening decision to
  GVR against, and summarily reversing a 9–8 en banc court on a contested
  reading of Kennedy is not this Court's practice; several Justices likely
  agree with the decision below, which forecloses the "clearly wrong under
  settled law" predicate. The statpack's cert-order share of grants is
  substantial (GVRs dominate the grant family in some Terms), which is why I
  don't go lower — but that share is driven by intervening-decision GVR
  stacks, a mechanism absent here.
- `dissent-from-denial` 0.85 — conditional on denial. A denial that leaves an
  en banc declaration of Stone's demise standing would very likely draw a
  written dissent or statement (Sotomayor and/or Jackson, plausibly Kagan);
  silent denials of petitions with this profile are rare. Not 0.95 because a
  strategic silent denial (to avoid signaling) is conceivable.

## Base rates consulted

Committed `metrics/statpack.md` (repo copy at HEAD, bdc77c4d7 "live: refresh
corpus + outcomes (2026-08-20)"): salience-band segment table (sal-v3) for the
pooled baseline `reached` anchor (~6.5% over OT2017–OT2025); modern
discretionary-cert base rate (grant family a few percent); relist-count cut
(0-relist terminal rate 1.2% granted — read as shape only, not as the arrival
hazard); CVSG cut (173/13,610 ≈ 1.3% incidence; 29.4% granted given CVSG —
shape only); Term table for timing (median ~62 days to resolution — dominated
by denials; a granted blockbuster runs far longer).

## Uncertainty and discounts

- I am most uncertain about the deny-and-percolate scenario's weight; there
  is no good base rate for "en banc court declares SCOTUS precedent
  abrogated" because the posture is rare. My 0.72 rests on qualitative
  reference-class reasoning more than on the statpack.
- No BIO exists yet; if respondents surface a jurisdictional or vehicle
  defect I cannot see (e.g., standing arguments the en banc court's 9–8
  justiciability holding papered over), the number is too high.
- I carry background knowledge of this litigation wave through my training
  data (the district-court injunctions and the Louisiana panel decision in
  2025); the en banc reversal and everything after it I know only from the
  provisioned petition and two CourtListener metadata lookups confirming the
  decisions exist as described. Petitioner framing is the primary source for
  what the en banc opinions say — the BIO would contest emphasis, though not
  the holding's existence.
- Corpus-freshness note: I did not read corpus rows for this prediction (the
  committed statpack, refreshed 2026-08-20 per its data commit, is my only
  corpus-derived input); the snapshot and documents were provisioned
  2026-08-20/21, i.e. current as of docketing day.
