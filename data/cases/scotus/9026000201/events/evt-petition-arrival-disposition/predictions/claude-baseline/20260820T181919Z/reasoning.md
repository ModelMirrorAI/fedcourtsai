# Rationale — P(grant) = 0.95

## Anchor

This is an arrival-moment cell with a frozen `band: federal` under `sal-v3`,
matching the committed statpack's band table version, so the anchor is the
federal band's bracketed `reached` rate pooled over Terms strictly before this
case's (Term 2026). Pooling the table's rendered rows 2017–2025:
143.0/201 ≈ **71.2%** (per-Term reached rates range 43.5%–89.5%; the pooled
"Cert petitions by salience band" cut shows the same ~71% grant family:
granted 48.8% + gvr 22.4% on n=201 resolved). The band's two figures coincide
because federal is the strongest band. The zero-distribution state is the
arrival moment's definition, not a signal — I did not discount for it.

## Adjustments up from 71% to 0.95

Within the federal band this petition sits at the extreme favorable end on
every dimension the band does not condition on:

1. **A court of appeals facially invalidated an Act of Congress.** The Court's
   near-uniform practice is to grant the government review of such holdings.
2. **An acknowledged circuit split on the same statute** (CA5 here vs. CA6 in
   Oklahoma v. United States, 163 F.4th 294), leaving federal law
   non-uniform circuit-to-circuit.
3. **Demonstrated prior engagement by this Court in this very case**: a stay
   of the Fifth Circuit's mandate (24A287, Oct. 2024) and a GVR of the prior
   petition round in light of FCC v. Consumers' Research (Aug. 1, 2025). The
   Fifth Circuit reissued on remand, so percolation and GVR are exhausted
   options; five Justices already thought the invalidation warranted a stay.
4. **Clean vehicle**: final judgment after a bench trial, a single QP framed by
   the SG, a companion petition from the Authority (26-199) the SG asks to
   consolidate with.

The federal band's residual ~29% non-grants are mostly ordinary SG petitions
without an invalidated statute or a split; conditioning on both, historical
practice puts the grant-family probability well above 0.9.

## Why not higher

- **Companion-petition routing risk**: the Court could grant only the
  Authority's petition (26-199) and hold this one, later denying it as
  redundant. I weigh this low — when the SG petitions from the same judgment
  the Court virtually always grants the government's petition, and in the
  prior round it gave every petition the same (GVR) disposition — but it is
  the main path to a non-grant label on this docket.
- **Mootness by re-amendment**: Congress amended HISA once before (2023) in
  response to the first Fifth Circuit ruling. A repeat before disposition
  would likely produce a Munsingwear vacatur (gvr — still grant family) but
  could produce a dismissal.
- Generic tail risk (withdrawal, unforeseeable vehicle collapse).

Net: **0.95**, disposition `granted`.

## Claim numbers

- `disposition` 0.95 — as above; equals the top-level probability.
- `relist-increment` 0.98 — from zero distributions, any live petition with a
  response due is distributed at least once unless withdrawn or dismissed
  first; the relist-count cut's relist-0 row is a terminal-state figure and
  does not describe an arrival's forward hazard, so this is essentially
  P(the petition survives to a conference), which for an SG petition on a
  live controversy is near 1.
- `cvsg-increment` 0.01 — the SG is the petitioner; a CVSG has no function.
- `summary-disposition-route` 0.08 — conditional on grant. A second GVR lacks
  an intervening decision (the Consumers' Research GVR already ran its
  course); summary reversal on a split of this substance is rare; residual
  covers a mootness vacatur riding a cert order.
- `dissent-from-denial` 0.2 — conditional on the (unlikely) denial, the modal
  denial-world is administrative (companion granted instead), drawing no
  writing; only an outright denial leaving the invalidation in place would
  likely draw one. No published baseline exists for this claim; the number is
  banked.

## Inputs and their limits

- Snapshot `2026-08-18.json` (provenance: truncated; cutoff 2026-08-18): the
  docket skeleton only — one proceedings entry. All substantive signal comes
  from the provisioned documents.
- `petition.txt` (137 pp., `truncated: true` — the appendix opinions are cut
  off mid-stream; the petition body through the conclusion is complete, which
  is what I relied on) and `questions-presented.txt` (complete). No
  brief-in-opposition exists yet — respondents' filing is due September 16,
  2026 — so I have only the petitioner's characterization of the decision
  below and of the split. I discount that asymmetry less than usual because
  the load-bearing facts (facial invalidation, the Sixth Circuit's contrary
  holding, the prior stay and GVR) are matters of record the BIO cannot
  contest, only recontextualize.
- Base rates: committed `metrics/statpack.md` (the repo's committed pack; no
  corpus-wide vintage claim is made beyond it). One `fedcourts query` for
  recent granted SCOTUS priors returned general context only — the query
  surface cannot filter on petitioner class or statute-invalidation posture,
  so the close comparators here come from the band table, not retrieved
  priors.
- CourtListener MCP lookups for the companion dockets 26-199 and 25-1325
  returned no results (current SCOTUS paid dockets are not in the RECAP
  index), so the companion posture rests on the petition's own related-
  proceedings statement, which is recent (August 2026) and reliable.
- I know this litigation's pre-2026 history from training (the 2022 and 2024
  Fifth Circuit decisions, the 2023 amendment, the stay). The event being
  predicted — this petition's disposition — postdates anything I could know;
  the case is genuinely pending and the forward-mode retrieval surfaced no
  disposition.

Main uncertainty: not whether the Court takes the question (it will, via this
petition or its companion) but whether *this docket number* carries the grant.
That routing risk is the gap between 0.95 and something higher.
