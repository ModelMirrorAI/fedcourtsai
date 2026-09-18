# Rationale for the numbers

**P(any grant) = 0.70, modal disposition `gvr`, `granted` = 1.**

## What I read

Provisioned inputs: `record/snapshots/2025-10-15.json` (nine proceedings entries through the CVSG), `record/context.json` (forward mode, band `high` under sal-v4, Term 2025, `distribution_count` 2, `cvsg_date` 2025-10-14, cutoff 2025-10-15 under a `date` cut), and all three provisioned documents: `questions-presented.txt`, `petition.txt` (217 pages, `truncated: true`, text present through the preemption argument) and `brief-in-opposition.txt` (32 pages, complete). I had a subagent digest the petition and BIO; the digest's claims I relied on (Gospel Light not a petitioner, preliminary-injunction posture, pending state-court appeal, the BIO's no-split argument on *We the Patriots* and *Spivack*) I cross-checked against the SG's brief, which makes the same points.

## Anchor

Cert-stage cell, `moment: cvsg`. The statpack's "Segment base rate by salience band (sal-v4)" table matches my context's `salience_version`, so the anchor is the `high` band's bracketed `reached` rate pooled over Terms strictly before OT2025 (OT2017 to OT2024, all eight rows the table renders): weighting each row's rate by its n gives about 35% on n of roughly 900. The CVSG cut of the paid scored segment says the same thing from the other side: granted 29.4% plus gvr 5.5% (grant family about 35%), denied 62.0%, dismissed 3.1%, on 163 resolved. The relist-count cut's bucket 2 (this docket's snapshot state) reads granted 27.8% plus gvr 13.1%. So the pre-adjustment number is about 0.35.

## Adjustments, and why the number is double the anchor

The adjustment is almost entirely forward docket information the cell is allowed to use (forward mode: "this docket's own entries outside that baseline included"). The snapshot is eleven months old and the decisive event has happened since:

1. **The SG recommended a hold**, not a grant or a denial (brief of 2026-05-26). The CVSG base rate blends grant, deny and hold recommendations; a hold recommendation keyed to a case the Court has *already granted* from the *same circuit* on the *same doctrinal question* shifts the disposition distribution toward GVR. Held petitions in this posture are disposed of by GVR when the lead case comes out the petitioner's way and by denial otherwise.
2. **The Court appears to have held it.** Distributed for the 2026-06-25 Conference, no order, no relist entry since (supremecourt.gov docket read 2026-09-18; SCOTUSblog lists it as a pending petition). A held petition gets no docket entry, so silence here is the expected shape. I put P(held) at about 0.97, the residual being a stale page.
3. **P(*St. Mary Catholic Parish* reverses) about 0.85**, from the Court's Free Exercise record and the fact that it granted at the religious petitioners' request from a Tenth Circuit loss.
4. **P(GVR | *St. Mary* reverses) about 0.85.** The SG's brief states the overlap explicitly: the Tenth Circuit in *Renteria* used the same "different purpose / not in a similar way" comparability reasoning as its *St. Mary* panel. The main leak is *St. Mary* being decided on its second question only, which petitioners themselves flag, or a narrow opinion the Court does not think "may affect" the judgment below.
5. **P(grant | *St. Mary* affirms) about 0.10**: plenary review of a PI ruling whose regulated party is not before the Court, over the BIO's and SG's vehicle objections, is unlikely.

Arithmetic: 0.97 × (0.85 × 0.85 + 0.15 × 0.10) + 0.03 × 0.3 ≈ 0.72. I round down to 0.70 for unmodelled paths (mootness via the state-court appeal, a denial resting on the Tenth Circuit's separate neutrality holding, a dismissal).

## Claim-by-claim

- `disposition` 0.70: as above.
- `relist-increment` 0.98: the snapshot shows 2 distributions; a third (2026-06-25) is already on the docket, and disposal of a held petition brings another. Not 1.0 only because the resolver reads the corpus row, not my browser.
- `cvsg-increment` 0.01: the CVSG is on the docket; vacuous, harness-masked.
- `summary-disposition-route` 0.93: conditional on grant, nearly all of my grant mass is a GVR in light of *St. Mary*; a plenary grant is the residual.
- `dissent-from-denial` 0.25: a denial most likely means *St. Mary* went against religious claimants, which raises the odds of a written dissent from Justices Thomas, Alito or Gorsuch, and the state counsel's remarks in the record are quotable; but hold-then-deny dispositions are usually silent.

## What would move me

If the docket shows a relist entry or an order before *St. Mary* is decided, the hold reading is wrong and the number should fall toward the CVSG base rate. If *St. Mary* is argued and the argument suggests a disposition on the *Carson* question alone, P(GVR) drops materially. Vehicle problems (PI posture, Gospel Light absent, state-court appeal pending, one preemption argument unpreserved) matter little on the GVR route and a lot on the plenary route, which is why `gvr` rather than `granted` is the modal label.

## Where to discount me

- The whole lift above the anchor rests on public docket material fetched from supremecourt.gov and read through PDF text extraction; the CourtListener MCP returned zero docket entries for this SCOTUS docket, so it could not serve the current state. The SG brief and supplemental brief texts I quote are from those PDFs.
- The P(hold) and P(GVR | reversal) figures are judgment, not statpack cuts; the pack has no cut for CVSG petitions by SG recommendation or for held petitions.
- Corpus freshness: the statpack is the committed `metrics/statpack.md`; `fedcourts corpus-info` is not available in the cell, so I cannot quote the blob's vintage. The `fedcourts query` I ran returned nothing usable for this cell (its top rows were unrelated substantive applications and OT2025 grants) and did not shape the number.
- No outcome of this petition surfaced anywhere; the cell is genuinely forward. Nothing under `data/qp-topics/` was read, and I did not read the other predictors' or my own earlier cell's outputs on this event.
