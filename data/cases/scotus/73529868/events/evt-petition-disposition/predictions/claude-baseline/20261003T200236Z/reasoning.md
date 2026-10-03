# Why 0.54, and why `gvr`

## What I read

- Provisioned snapshot `record/snapshots/2026-10-03.json` (as-stored; no cutoff). `record/context.json`: mode `forward`, band `federal` under `sal-v4`, `distribution_count` 1, no CVSG, Term 2025, paid docket.
- **No documents were provisioned** (no `record/documents/` directory). The docket carries a Rule 34.6 paper-only directive, so the petition, BIO and reply have no supremecourt.gov PDF links for the pipeline to fetch. I read the Solicitor General's petition from justice.gov instead (forward mode permits it) and did not read the BIO, so my account of respondents' arguments is inferred from their two docketed letters and the Second Circuit record, not from the BIO's text.
- The Sixth Circuit opinion (CourtListener opinion 11324612, published, Clay J. for Cole J.; Murphy J. dissenting at length). Holding: § 1225(b)(2)(A) does not reach noncitizens present after an unlawful entry, who are detained under § 1226(a) with bond hearings; and, as a **freestanding alternative**, procedural due process independently requires a bond hearing. Every respondent had been released by the government after the district court rulings, without a bond hearing.
- The Solicitor General's petition in this case (both questions, "best vehicle for resolving both issues") and the SG's petition in *Rhoney v. Barbosa da Cunha*, No. 26-104, which asked the Court to **hold** *Rhoney* pending *Putra*. Respondents' September 25 letter (docketed PDF) urged that if the Court grants anything it grant only the statutory question. The Court's October 1, 2026 order list (609 U.S.) granted *Rhoney* in full and did not mention this petition. SCOTUSblog's case page for 25-1415 still shows it pending; the supremecourt.gov docket as of October 3 shows no entry after September 25.

## Anchor

The context's band is `federal` under `sal-v4`, which matches the statpack's "Segment base rate by salience band (sal-v4)" table. Pooling the **bracketed `reached`** figures over the Term rows strictly before OT2025 (OT2017–OT2024) gives roughly 132 grants over n=181, about **73%** grant-family for a federal petitioner. The pack-level federal band splits that family as granted 48.5%, gvr 22.3%, denied 25.7%, dismissed 3.5%. The relist cut (bucket 0, our state) and the CVSG cut (none) are population shape only; the SG's own petitions are not what they describe.

## Adjustments

**Down from 73% to the mid-50s**, for one reason that dominates everything else: the Court has already chosen its vehicle for this question and it is not this petition. Had the Court wanted to decide both questions it would have granted *Putra* on October 1 as the SG asked; it granted the statutory-only companion instead. For a companion SG petition the ordinary consequence is a hold, and a held companion's fate tracks the merits:

| branch | P | P(grant family within branch) |
| --- | --- | --- |
| held pending *Rhoney* | 0.83 | government wins statute (0.55) → ~0.90 (GVR 3:1 over plenary on QP2); government loses (0.45) → ~0.04 |
| relisted and granted this fall (likely with *Genalo v. D.C.*, 26-379, on due process) | 0.12 | 1.0 |
| denied this fall | 0.05 | 0 |

That yields P(any grant) ≈ 0.55, P(GVR) ≈ 0.32, P(plenary) ≈ 0.22, P(denied) ≈ 0.45. I report **0.54**.

**Why 0.55 for the government on the statute.** For: § 1225(a)(1) deems these noncitizens applicants for admission; *Jennings* (583 U.S. at 287) called § 1225(b)(2) a "catchall" for all applicants for admission not covered by (b)(1); the current majority has sided with the government in nearly every recent detention-statute case (*Jennings*, *Preap*, *Thuraissigiam*, *Arteaga-Martinez*, *Aleman Gonzalez*); the Fifth and Eighth Circuits and Judge Murphy have given the reading a textualist pedigree. Against: thirty years of contrary practice; the "seeking admission" surplusage point; the Laken Riley Act's addition of § 1182(a)(6)(A) inadmissibles to § 1226(c), which is pointless if they were already under mandatory § 1225 detention; the lopsided wave of lower-court rulings by appointees of both parties; constitutional avoidance. I treat it as a little better than a coin flip for the government, and that single number is where most of my uncertainty lives.

**Why `gvr` with `granted = 1`.** The binary is P(any grant) and I hold it above one half, so `granted` is 1. Within the grant family the cert-order route (a GVR after *Rhoney*) carries more mass than a plenary grant, so `gvr` is the consistent label even though `denied` is the single most likely label overall (≈0.45). A reader who wants the modal label should read the table, not the field.

## The claims

- `disposition` 0.54 — restates the above.
- `relist-increment` 0.93 — a held petition is redistributed for the conference at which it is disposed of, and a fall grant would follow a relist; only the early-denial branch leaves the count at one. If the harness's distribution parser does not count a post-hold redistribution the claim will resolve against me; I state it on what the docket will show.
- `cvsg-increment` 0.01 — the Solicitor General is the petitioner.
- `summary-disposition-route` 0.58 — P(cert-order disposition | grant) = P(GVR)/P(grant) from the table.
- `dissent-from-denial` 0.06 — the dominant denial branch is a routine post-merits companion denial.

## Where to discount me

- The whole structure rests on a hold inference drawn from one order list two days old. If the Court instead relists this petition for October 9 and grants it with *Genalo v. D.C.*, the number should have been ~0.85; if it denies on October 5, ~0.
- I did not read the BIO. Respondents' vehicle arguments (released respondents, a due-process holding the Court may not want) are inferred from the SG's reply posture, the Sixth Circuit opinion, and respondents' letters.
- The federal-band anchor pools thin rows (n between 11 and 41 per Term) and is a grant-family rate that already includes GVRs; I did not separate GVR share by Term because the pack says the split is not comparable across Terms.
- I know nothing about this petition's outcome; nothing retrieved postdates the docket's September 25 entry except the October 1 order in the companion case, which is a legitimate forward signal and is flagged.
