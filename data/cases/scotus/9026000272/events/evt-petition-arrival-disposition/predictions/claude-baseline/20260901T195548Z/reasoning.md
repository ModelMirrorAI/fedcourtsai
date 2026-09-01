# Rationale — why P(grant) = 0.93

**The cell.** Arrival-moment cert cell, forward mode: the petition (No.
26-272) was docketed September 1, 2026 and the snapshot shows only the filing
entry ("Petition for a writ of certiorari filed. (Response due October 1,
2026)"). Zero distributions, no CVSG — that absence is the moment's
definition. `record/context.json` freezes `band: federal` under `sal-v4`,
which matches the committed statpack's band-table version, so the band table
is quotable for this cell.

**Anchor.** Per the arrival-moment rule, I anchored on the caption class's
floor: the `federal` band's bracketed `reached` rate, pooled over every prior
Term the statpack's "Segment base rate by salience band (sal-v4)" table
renders (2017–2025; the 2026 row is empty). That pool is ≈143 grants over
n=202, ≈ **71%**. The two most recent Terms sit lower (52.4% and 60.0% on
n=21 and n=15), which I read partly as right-censoring — a live Term's
strongest federal petitions are disproportionately still pending — but the
71% pooled figure is the anchor, per the pooling rule.

**Adjustments up (71% → 93%).** This petition is far stronger than the median
federal-band petition on every signal visible in the provisioned documents:

1. **The Court already intervened in this controversy.** It stayed the
   parallel Shilling injunction in full "pending further review" (145 S. Ct.
   2695 (2025)), a step that (as the petition argues via *Hollingsworth*)
   embeds a majority's judgment that the question likely warrants certiorari.
   It also stayed the injunctions against the predecessor Mattis policy
   (*Trump v. Karnoski*, 2019).
2. **A circuit held a signature federal policy likely unconstitutional and
   the injunction stands as to serving members.** Invalidation of a major
   federal policy at the SG's request is the classic near-automatic grant,
   and denial here would leave that ruling in place against a policy the
   Court's own stay allowed into effect.
3. **The Court's demonstrated appetite for the doctrinal area** (*Skrmetti*
   2025; *Chiles* 2026; *B.P.J.* 2026), and the petition's claim that the
   decision below conflicts with the reasoning of *Skrmetti* and *B.P.J.*
4. **The vehicle is clean by the SG's design**: full merits ruling below
   after two panels, a dissent (Judge Walker) squarely presenting the
   military-deference ground, and the interlocutory posture is one the Court
   routinely accepts for major-policy injunctions.

**Why not higher.** Residual mass on: the Court holding for *Shilling* and
disposing by GVR after deciding that case first (a GVR still counts as a
grant here, so this mostly moves route, not disposition); the policy being
rescinded or the case settling before conference (small, but a change of
administration priorities or of the policy's terms before the likely
conference date is not zero); the Court preferring to await the Ninth
Circuit's post-*B.P.J.* reargument and denying without prejudice to a later
petition (~3–4%); and ordinary vehicle surprises in a 319-page record I read
only in part. Hence 0.93 rather than 0.97.

**Claim-level numbers.**
- `disposition` 0.93 — restates the top-level probability.
- `relist-increment` 0.97 — the snapshot shows **zero** distributions, so
  this is P(the petition is ever distributed). A paid SG petition with an
  institutional respondent will reach conference unless the case is
  withdrawn or settles first; the residual 3% is that exit.
- `cvsg-increment` 0.01 — the United States is the petitioner; the Court
  does not call for the views of the Solicitor General in the SG's own case.
- `summary-disposition-route` 0.12 (conditional on grant) — a GVR in light
  of *B.P.J.* is conceivable, but the SG seeks plenary review, the panel
  already engaged *Skrmetti*, and neither recent decision resolves the
  military-deference question; the statpack publishes no cert-order-share
  cut I could anchor this on, so it is judgment against the Court's practice
  of setting major-policy cases for argument.
- `dissent-from-denial` 0.35 (conditional on denial) — a denial would be a
  surprise reversal of the Shilling-stay signal; conditional on one, a
  statement or dissent from the Justices who supported that stay is
  plausible but not a majority expectation, and the statpack publishes no
  baseline for this claim.

**What I used.** The provisioned petition text (319 pages, `truncated: true`
per `documents.json` — I read the QP, introduction, statement, procedural
history, and reasons-for-granting sections; the appendix beyond was not
needed), the QP file, the snapshot, `record/context.json`, and the committed
`metrics/statpack.md` (band table, relist and CVSG cuts, modern-cert
section). Two `fedcourts query` citation lookups (for the *Skrmetti* and
*Goldman v. Weinberger* rows) returned empty — the citation column covers
only 159 of ~590k SCOTUS rows — so no corpus priors informed the number; I
did not retry sparse filters. No CourtListener MCP or web retrieval: the
petition postdates any coverage the corpus would hold, and the provisioned
record was rich. Statpack vintage: the committed pack at HEAD (corpus
refreshed 2026-09-01 per the repo's latest pull commits); snapshot provenance
is `truncated` per context.json.

**Where to discount me.** I carry background knowledge of this litigation
(the Shilling stay, *Skrmetti*) from training rather than retrieval — it is
all pre-decision material for this undecided petition, so it is legitimate
forward signal, but my confidence in the surrounding posture (e.g. the Ninth
Circuit reargument timing) rests on the petition's own account. The
relist-count expectation (one to two relists) is shape-reading from the
statpack's terminal-count buckets, which do not give a forward hazard from
the zero state. The 0.93 is a judgment call above a 71% anchor; reasonable
readers could sit anywhere in 0.85–0.95.
