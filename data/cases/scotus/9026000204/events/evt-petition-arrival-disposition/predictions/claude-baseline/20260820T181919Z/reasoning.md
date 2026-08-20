# Rationale — why P(grant) = 0.90

**Cell posture.** Forward-mode, cert-stage, `moment: arrival`: the petition was
docketed August 18, 2026 and the snapshot (2026-08-19) shows exactly one docket
entry — the petition filing, response due September 17, 2026. Zero
distributions, no CVSG, no BIO yet. That absence is the moment's definition,
and I forecast from it rather than waiting for docket signals.

**Anchor.** `record/context.json` freezes `band: federal` under `sal-v3`, which
matches the committed statpack's segment table version, so the bracketed
`reached` rate is the scored yardstick. Pooling the `federal` column's
bracketed figures over the nine Terms strictly before this case's (OT2017–
OT2025, n = 21+15+29+19+11+40+26+23+17 = 201, grants ≈ 143) gives roughly
**71%**. The pooled salience-band cut agrees: federal band, granted 48.8% +
gvr 22.4% ≈ 71% any-grant over n = 201 resolved.

**Adjustments up from 71% to 0.90.** The federal band pools every
federal-petitioner paid petition; this one carries, on the provisioned record,
essentially every additional grant signal the band does not condition on:

1. **A federal statute held unconstitutional below.** The Fifth Circuit
   invalidated 26 U.S.C. 5178(a)(1)(B); the Court's stated "usual" practice is
   to grant in that posture (*Iancu v. Brunetti*), and the SG's petition
   documents the recent pattern (*Sun Valley Orchards*, *Braidwood*, *Fuld*,
   *Jarkesy*). This is the single strongest cert factor and most of the
   federal band lacks it.
2. **A square, acknowledged circuit split on the identical question.** The
   Sixth Circuit upheld the same provision against the same challenge in
   *Ream*, 174 F.4th 480 (2026), with reasoning the petition shows diverging
   from CA5's at every step; a companion petition in *Ream* (No. 26-93) is
   already pending.
3. **Clean vehicle.** Final judgment, rehearing en banc denied, a single QP, a
   facial constitutional question with no preservation or standing wrinkle
   visible in the provisioned petition text.

**Adjustments holding it below ~0.95.** (a) The BIO is not yet filed; a
vehicle defect I cannot see could surface, though respondents won below on the
merits so a defect would have to be structural. (b) A mooting event — Congress
legalizing home distilling has recurring legislative support — could produce a
dismissal or silent denial. (c) Vehicle choice: the Court could take *Ream*
instead and hold this petition; a later GVR still lands in the grant family,
so this mostly moves probability between `granted` and `gvr`, not out of the
grant family, but a hold that outlasts the scoring window or resolves oddly is
residual risk. Net: **0.90**.

**Claims.**
- `disposition` 0.90 — restates the top-level probability.
- `relist-increment` 0.97 — from the frozen zero-distribution state, this is
  P(ever distributed). A paid SG petition heading to conference is distributed
  in the ordinary course; the complement is pre-conference withdrawal/mooting.
- `cvsg-increment` 0.01 — the United States is the petitioner; a CVSG calls
  for the views of a non-party SG. Structurally near-zero.
- `summary-disposition-route` 0.12 — conditional on a grant: the hold-for-
  *Ream*-then-GVR path. Plenary review of the government's own petition is the
  likelier vehicle; no intervening decision exists to GVR against otherwise.
- `dissent-from-denial` 0.25 — conditional on the unlikely denial: a denial
  leaving an Act of Congress invalidated in one circuit and valid in another
  would plausibly draw a statement or dissent, but the most probable denial
  worlds (post-mooting cleanup) pass silently, which caps this.

**Base-rate sources and freshness.** All rates are from the committed
`metrics/statpack.md` in the repo at run time (live/historical slice,
denial-reweighted); the sal-v3 segment table matches my context's
`salience_version`, so the band anchor is quotable as scored. Corpus `query`
retrieval returned generic granted priors only — the query surface cannot
filter on federal-petitioner or statute-invalidation — so the quantitative
anchor is the statpack, and the case-specific adjustment is qualitative.

**Where to discount me.** The petition text is provisioned truncated (110
pages, `truncated: true`), so I read the QP, the reasons-for-granting section,
and the split discussion but not the appendices; my read of the Fifth
Circuit's reasoning is through the SG's characterization plus quoted excerpts,
not the opinion itself. No BIO exists yet, so the respondent side of the
vehicle question is unexamined by construction. My CourtListener lookups for
the companion *Ream* docket returned nothing (SCOTUS dockets are thin there),
so the companion-case posture rests on the petition's own statements.
