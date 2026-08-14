# Rationale for the numbers — claude-baseline, run 20260814T175421Z

**P(grant family) = 0.52.**

## Anchors

- **Salience band.** The context freezes `band: high` under sal-v2, so the
  scored yardstick is the high band's bracketed `reached` rate. Pooling the
  statpack's "Segment base rate by salience band" rows over Terms 2017–2024
  (strictly before this Term-2025 case) gives a weighted ~40.3% (n≈1,059);
  recent Terms sit at 42–45%.
- **CVSG cut.** The paid scored segment's CVSG bucket resolves granted 30.1% +
  gvr 5.5% ≈ 36% grant family (n=163 resolved). This is a terminal-status cut
  and broadly agrees with the band anchor, which is the one the evaluator
  scores against.
- The relist cut (this docket sits at two distributions, i.e. one relist:
  ~13% grant family) is dominated here by the CVSG signal — the moment's own
  definition — so I did not anchor on it.

## Adjustments from ~0.40 up to 0.52

Upweights, all from the provisioned record: the petitioner is a **State
defending its own election statute** after federal invalidation — a posture
the Court grants at well above base rates; the en banc denial drew **two
published dissents** expressly asserting a deepened 7–4 circuit split on
Anderson-Burdick step two; there is a **companion petition (25-962)** from the
RNC respondents, who filed a brief *in support* of this petition, so the
usual adversarial cert posture is half-absent; several county-board
respondents also filed in support; and the Court has already invested two
conferences, a requested response, and a CVSG. Election-law petitions with
this alignment and the current Court's demonstrated appetite for
Anderson-Burdick questions sit above the pooled high-band case.

One further upweight specific to this pipeline's vocabulary: the outcome
resolver counts a Munsingwear vacatur as `gvr`, i.e. grant family, and this
litigation lineage has already produced one at the Court (Ritter v. Migliori,
143 S. Ct. 297 (2022), vacating the Third Circuit's Migliori decision as
moot). So the mootness scenario is not a pure loss for the grant-family
number.

## Adjustments down, and the main uncertainty

The BIO's vehicle argument is genuinely strong: **Baxter v. Philadelphia Board
of Elections**, argued in the Pennsylvania Supreme Court on September 10,
2025, may strike the date requirement under the state constitution's Free and
Equal Elections Clause on independent state grounds. My web retrieval (see
`retrieval.md`) found no decision as of today — eleven months post-argument —
but the CVSG timeline gives it roughly another year to land before this
petition is disposed of. Lower Pennsylvania courts ruled for the voters, and
the BIO calls affirmance likely. If Baxter strikes the requirement, the
likeliest dispositions here are denial (moot) or Munsingwear vacatur, roughly
evenly split in my estimate. My scenario arithmetic: P(Baxter strikes first)
≈ 0.5; in that branch grant family ≈ 0.45 (mostly vacatur); in the live
branch, P(SG recommends grant) ≈ 0.6 with grant family ≈ 0.8 conditional, and
≈ 0.25 if the SG recommends denial — netting ≈ 0.52 overall.

Where to discount me: the Baxter timing and outcome estimates are judgment
calls with no committed base rate behind them, and my P(SG recommends grant)
rests on a political-alignment read, not data. A reader who thinks Baxter is
certain to strike the requirement before mid-2027 should sit closer to 0.45;
one who thinks the Pa. court will duck or uphold should sit nearer 0.60.

## Claims

- `disposition` 0.52 — equals the top-level probability by construction.
- `relist-increment` 0.97 — the snapshot shows **two distributions**; after
  the SG files, redistribution is all but mechanical, and even a mootness
  disposition would come via a conference. The residual 0.03 covers
  withdrawal or an anomalous summary path before any further distribution.
- `cvsg-increment` 0.02 — the CVSG is already on the docket (6/29/2026); the
  claim is vacuous for this cell and the harness masks it. Stated per the
  contract.

## Inputs used

Full provisioned set: the 2026-08-14 snapshot, `questions-presented.txt`,
`petition.txt` (45 pp.), and the consolidated `brief-in-opposition.txt`
(94 pp., five respondent briefs; none flagged `empty_text`). The petition's
lead ask is a GVR in light of Coalfield Justice, with plenary review on the
Anderson-Burdick split in the alternative; the Eakin BIO leads with Purcell
and the Baxter mootness overhang. Corpus `fedcourts query` retrieval added
little here (the structured filters surface no election-law topical slice for
SCOTUS rows); the statpack carried the quantitative anchors. Forward-mode web
retrieval was used only to check the status of the *related* Baxter case —
public, pre-decision context for this petition — and surfaced nothing about
this petition's own disposition, which does not yet exist.
