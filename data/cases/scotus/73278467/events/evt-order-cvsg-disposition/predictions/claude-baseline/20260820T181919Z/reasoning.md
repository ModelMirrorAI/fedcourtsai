# Rationale — P(grant family) = 0.45

## Anchors

Two committed anchors from `metrics/statpack.md`, read against my frozen
context (`band: high`, `salience_version: sal-v3`, matching the statpack
table's version; `distribution_count: 2`; `cvsg_date: 2026-06-30`; Term 2025):

- **Scored baseline — high-band bracketed `reached` rate, pooled over Terms
  strictly before 2025** (OT2017–2024, all rendered rows preceding this
  case's Term): **40.9%** (n=1074, denial-reweighted). This is the yardstick
  the evaluator scores skill against for a cell carrying a frozen band.
- **CVSG cut (paid scored segment):** among CVSG'd petitions, granted 29.4% +
  gvr 5.5% ≈ **34.9% grant family**, denied 62.0%, dismissed 3.1% (n=163
  resolved). This is the moment-specific population.

The relist cut (2 distributions = 1 relist → grant family ~12.7%) is
dominated here: those buckets are terminal counts and a CVSG'd petition will
mechanically accrue further distributions; the CVSG cut and the frozen band
carry the signal.

## Adjustments

**Up from the anchors:**
- **The hold-then-CVSG sequence.** The petition was distributed 12/12/2025,
  then held ~6 months and redistributed 6/29/2026 — the day before the Court
  decided West Virginia v. B.P.J. (No. 24-43, decided 6/30/2026, the same day
  as this CVSG). The Court plainly held this case for B.P.J./Hecox and, with a
  costless GVR or denial available the day those cases came down, chose
  instead to invite the SG's views. That is a deliberate signal that the
  prison-context question is regarded as live and distinct from B.P.J.
- **Salience and support:** a 23-state amicus brief (plus the Arizona
  Legislature) supported the petition at the cert stage; paid petition;
  experienced counsel both sides.
- **Likely SG alignment.** The federal government runs the largest prison
  system in the country and the current administration has a strong declared
  policy interest in sex-based prison housing and search policies, so a
  recommendation supporting review is more likely than not; the Court follows
  SG grant recommendations at high rates.

**Down from the anchors:**
- **Vehicle defects, per the BIO** (all three provisioned documents were
  fetched with text; I read the QP section, the petition's reasons for
  granting, and the BIO's reasons for denying): petitioners **conceded
  intermediate scrutiny** in the Tenth Circuit, and the panel expressly
  resolved QP1 on party-presentation grounds — so the question presented was
  arguably not decided below. The case is at the Rule 12(b)(6) stage,
  interlocutory, with penological-deference arguments open on remand. The BIO
  also contests the split's ripeness. A preservation concession is exactly
  the ground on which the SG's office recommends denial even when it shares a
  petitioner's merits view.
- QP2 is factbound and split-free; it adds little independent grant pressure.

Netting: the revealed-interest signals justify sitting above both anchors,
but the vehicle problems are serious enough that I stop below 0.5. **0.45.**
With P(any grant) = 0.45, the coherent binary is `granted: 0` and the modal
single disposition is `denied` (~0.51), against ~0.36 plenary grant, ~0.06
gvr, ~0.02 dismissed/withdrawn.

## Claim-level rationale

- `disposition` 0.45 — restates the top-level probability.
- `relist-increment` 0.97 — the record shows **2 distributions**; a CVSG'd
  petition is redistributed once the SG files, so a further distribution
  fails only on a pre-brief dismissal/withdrawal.
- `cvsg-increment` 0.02 — the docket already shows a CVSG (6/30/2026), so
  this claim is vacuous for my cell and the harness will mask it; the number
  states the residual chance of a further invitation issuing after
  prediction time.
- `summary-disposition-route` 0.15 — conditional on a grant. The Court
  declined the free GVR moment on 6/30/2026, so a plenary grant is the
  likely route; the residual is a post-SG-brief GVR in light of
  B.P.J./Hecox.
- `dissent-from-denial` 0.35 — conditional on denial; no published baseline
  exists, so this banks rather than scores. High ideological salience and a
  ready-made en-banc dissent template cut up; the better-vehicle-awaited
  dynamic of a post-CVSG vehicle denial cuts down.

## Uncertainty and discounts

- **The SG's brief does not exist yet** and is the dominant unresolved
  variable; my number is effectively a mixture over the SG's recommendation
  (roughly 0.55–0.6 weight on a grant-side recommendation). A reader with a
  view on that recommendation should move my number accordingly.
- **I could not read what B.P.J. held.** CourtListener records the decision
  (2026-06-30, Kavanaugh listed on the cluster) but serves no opinion text
  yet, so my use of it is limited to its existence and timing relative to
  this docket's hold/CVSG sequence — which is the part that carries forecast
  weight. If B.P.J.'s reasoning reaches sex-based custody classifications
  more directly than I assume, the GVR share of my grant mass should be
  higher and the plenary share lower.
- My knowledge cutoff (January 2026) predates the second distribution, the
  CVSG, and B.P.J.'s decision; everything after that date comes from the
  provisioned snapshot and the logged CourtListener retrieval, not from
  training knowledge. I carry no knowledge of this petition's disposition
  (none exists — forward mode) and did not search for one.
- Base rates are from the committed `metrics/statpack.md` as committed at run
  time; I did not read the corpus blob directly, so no corpus vintage is
  quoted.
