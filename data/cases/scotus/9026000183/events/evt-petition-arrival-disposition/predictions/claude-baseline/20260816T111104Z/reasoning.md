# Rationale for the numbers

**P(grant family) = 0.20** on an arrival-moment cert cell, band `baseline`
(sal-v3), forward mode, zero distributions.

## Anchor

`record/context.json` freezes `band: baseline` under sal-v3, matching the
statpack's Segment-base-rate table version, so the yardstick is the baseline
band's **bracketed `reached`** rate — which for the weakest band is the whole
paid scored segment's grant rate, the correct unconditional anchor for an
arrival cell. Pooling the table's Term rows strictly before OT2026
(OT2017–OT2025, all nine rendered rows): weighted grants ≈ 862 over n ≈ 13,163
→ **≈ 6.5%**. That is the base rate this forecast starts from and the baseline
my skill is scored against.

## Adjustments up (6.5% → 20%)

- **Counsel.** Noel Francisco (former Solicitor General) is counsel of record,
  with a Jones Day team plus United's GC. Expert-SCOTUS-bar representation is
  among the strongest observable arrival-time grant predictors in the paid
  segment.
- **Asserted circuit conflict with a quotable separate opinion below.** The
  petition claims the Fifth Circuit's commonality approach (168 F.4th 713)
  splits from the 3d, 4th, 6th, 7th, 8th, 9th, and 11th Circuits' application
  of Wal-Mart's "one stroke" rule, and Judge Willett declined to join the
  operative portion, writing that under the panel's approach "no putative class
  would ever fail the commonality requirement." A published opinion + named
  dissenting-in-part circuit judge is a classic grant profile.
- **Demonstrated current appetite for Rule 23.** The Court granted LabCorp v.
  Davis (605 U.S. 327 (2025)) on a Rule 23(b)(3) question and DIG'd it, leaving
  the predominance cleanup undone — a Court looking for a better vehicle is a
  live possibility, and this petition pitches itself as one.
- **Stakes.** A certified ~1,000-member Title VII class with formula-based
  backpay and punitive damages against a major carrier; business amici
  (Chamber-type) are predictable, which historically correlates with grants.
- **The Detwiler hold ask.** Even if plenary review fails, the petition's
  fallback (hold for Detwiler v. Mid-Columbia Medical Center) opens a GVR
  route, which counts as a grant on the binary axis.

## Adjustments down (why not higher)

- **The split is contestable.** The BIO (not yet filed) will argue the Fifth
  Circuit applied settled standards to unusual facts and that the three-phase
  trial plan is case management, not a commonality holding. Application splits
  get denied far more often than square rule splits.
- **Cross-cutting valence.** Granting United's petition would unwind a class of
  religious objectors to a vaccine mandate. Justices most sympathetic to
  class-action-abuse arguments are also the most sympathetic to religious
  accommodation plaintiffs, which mutes the usual coalition for a grant.
- **Detwiler is unconfirmed.** CourtListener shows the Ninth Circuit opinions
  but no SCOTUS docket for a Detwiler petition as of today, so the hold/GVR
  route is priced modestly rather than as a pending companion.
- **Novelty may invite percolation.** The "class rostering" procedure is
  self-described as unprecedented; the Court sometimes lets a novel procedure
  play out (or the en banc process elsewhere sharpen the conflict) before
  intervening. Rehearing en banc was denied below without a published dissent
  from denial that the petition quotes, which slightly weakens the
  intra-circuit alarm signal.

Net: this reads as roughly a 3x-over-segment-baseline petition — comparable to
an average petition that eventually reaches the `elevated` band (pooled reached
rate ≈ 20%), which is where I land: **0.20**.

## Claim-level rationale

- `disposition` 0.20 — restates the top-level probability.
- `relist-increment` 0.97 — from a zero-distribution arrival state, this
  resolves true on the *first* distribution. A paid, professionally
  prosecuted petition in an ongoing certified class action essentially always
  reaches a conference; residual 3% covers settlement/withdrawal/dismissal
  before distribution.
- `cvsg-increment` 0.03 — CVSGs run ~1.3% of the paid scored segment
  (statpack CVSG cut: 173 of ~13.6k). Private Title VII/Rule 23 dispute, no
  federal party; slightly above base because the accommodation issue has
  federal enforcement salience, but the SG's views would more naturally be
  sought in Detwiler.
- `summary-disposition-route` 0.30 — conditional on a grant. Mostly the GVR-
  in-light-of-Detwiler route the petition itself requests; a summary reversal
  of a long published opinion is unlikely. Below the corpus-wide GVR share of
  the grant family (~46%) because Detwiler's SCOTUS petition is unconfirmed and
  this petition's primary pitch is plenary.
- `dissent-from-denial` 0.07 — conditional on denial. Above the low background
  rate for the Willett-hook and LabCorp-dissenters reasons in
  `predicted_reasoning.md`, held down by the valence problem. No published
  baseline exists for this claim; the number is banked.

## Uncertainties / where to discount me

- **No BIO yet.** The single largest unresolved input. A waiver or a weak
  response would move me up; a strong vehicle-fault BIO (e.g., showing the
  commonality holding is interlocutory-posture-bound) would move me down.
- **Detwiler status.** If a Detwiler petition is docketed and granted this
  fall, both the disposition and summary-route numbers rise materially; my
  inability to confirm it (no SCOTUS docket found on CourtListener) may just be
  coverage lag.
- **Valence weighting is judgment, not data.** I have no cut quantifying how
  ideological cross-currents move grant rates; the -adjustment is qualitative.
- The pooled 6.5% anchor uses the nine Term rows the committed table renders
  (its caption says 10 of 10 Terms rendered; OT2026's row is empty), which is
  the full available window.

Inputs used: the provisioned snapshot (2026-08-16), `questions-presented.txt`
and `petition.txt` (both fetched cleanly, `empty_text: false`; no BIO exists
yet), `record/context.json`, the committed `metrics/statpack.md`, one
`fedcourts query` for recent granted-petition shape, and CourtListener searches
for the Detwiler companion (see `retrieval.md`). MCP was available; nothing
outcome-revealing about this case was surfaced (none exists — forward cell,
petition pending).
