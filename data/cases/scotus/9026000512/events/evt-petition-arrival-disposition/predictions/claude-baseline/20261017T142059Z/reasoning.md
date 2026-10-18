# Reasoning — P(grant) = 0.005

**Inputs read.** Snapshot `record/snapshots/2026-10-17.json` (one proceedings
entry: petition filed Aug 5, 2026, response due Nov 16, 2026; paid docket, not
capital; counsel a small Tucson criminal-defense practice), `record/context.json`
(forward mode, band `baseline` under `sal-v4`, distribution_count 0, no CVSG,
Term 2026), `questions-presented.txt`, and `petition.txt` (QPs, jurisdiction
statement, statement of the case in part, and the full Reasons for Granting).
`documents.json` marks the petition truncated; the cuts fall inside the appendix
(pipeline notes), not the petition body, so I read the argument in full. No BIO
exists yet (arrival moment).

**Anchor.** This is an arrival-moment cert cell with a private petitioner
(an individual criminal defendant v. Arizona), so the anchor is the private
class floor — the `baseline` band's bracketed `reached` rate in the statpack's
"Segment base rate by salience band (sal-v4)" table — pooled over the Terms
strictly before 2026 that the table shows (2017–2025). Weighting each Term's
reached rate by its n gives about 644 grants over n ≈ 12,877, i.e. **≈ 5.0%**.
That matches the context's frozen band and version, so no mismatch to flag.
(The OT2026 row is excluded as not strictly prior, and is thin anyway.)

**Adjustments — all downward, and large.**
- **No split is alleged.** The Reasons for Granting cite no conflicting
  decisions; the argument is a policy case for extending *Abney v. United States*
  to a post-verdict, pre-sentence window for *Ashe v. Swenson* collateral-estoppel
  claims.
- **Vehicle / jurisdiction problems.** QP 1 asks about relief under 28 U.S.C.
  § 2241, but the petition seeks review of a state trial court's denial of a
  Rule 24.2 motion to vacate (the Arizona Court of Appeals declined review and the
  Arizona Supreme Court denied review). No federal habeas ruling is under review.
  The petitioner has been convicted but not sentenced, so the state judgment is
  not obviously "final" under 28 U.S.C. § 1257(a) — the Court would likely see
  a finality obstacle before reaching the question. QP 2 is mostly a question of
  Arizona procedural law.
- **Population signals.** Paid but not elite counsel; no amici; no government
  petitioner; unpublished, discretionary state-court denials below. These are
  the features that keep the large majority of baseline-band arrivals at zero
  distributions past the first conference.

The reached rate (5%) prices in petitions that later climb to `elevated`/`high`
through relists; I see little chance this one does. I land at **0.5%**, about a
tenth of the anchor. My main uncertainty is that I may be underweighting the
chance of an unusual summary action on the interlocutory posture; that tail is
very small.

**Claims.** `relist-increment` 0.96 is P(the petition is distributed at all from
its current zero), which nearly every paid petition is unless withdrawn.
`cvsg-increment` 0.002 — state respondent, no federal interest.
`summary-disposition-route` 0.25 is conditional on a grant. `dissent-from-denial`
0.01 — nothing here invites a separate writing.

**big_case_score 0.08.** A narrow procedural question about one defendant's case.

**Retrieval.** None beyond the provisioned inputs and the committed statpack.
I did not use the CourtListener MCP server or `fedcourts query`; the provisioned
petition was enough for an arrival-moment call.
