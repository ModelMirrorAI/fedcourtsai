# Robinson v. Freeman, No. 25-1296 — cert prediction

**Prediction: denied. P(grant, GVR included) ≈ 0.002.**

## The case

Samuel Collin Robinson, proceeding pro se (paid docket), petitions from an
unpublished Colorado Court of Appeals decision (2025CA0306, Aug. 14, 2025)
affirming the summary denial of his motion to modify parenting time; the
Colorado Supreme Court denied review on Nov. 24, 2025. The questions presented
attack Colo. Rev. Stat. § 14-10-124(1.5)(a)(I)–(XI) — the best-interests
parenting-time factors — as void for vagueness under the Fourteenth
Amendment's Due Process Clause: the factors allegedly give parents no notice
of what earns equal parenting time and invite arbitrary enforcement (relying
on *Kolender v. Lawson* and *Sessions v. Dimaya*), so his motion could not
lawfully be denied for failing to address them.

## Why this is a near-certain denial

1. **Base rates.** The statpack's modern discretionary-cert slice grants ~2.5–3%
   overall; paid petitions run ~5–7%, but petitions never relisted grant at
   ~0.8%, and this one was distributed once, for the September 28, 2026 long
   conference — the summer-list posture where weak petitions go to die. No
   BIO is on the docket (response was due June 22, 2026 and the case was
   distributed without one), no CVSG, no amici.

2. **No split, and the theory proves too much.** The petition concedes that
   all 50 states use materially similar best-interests factors and cites no
   conflicting authority anywhere holding such factors void for vagueness.
   There is nothing to resolve — the ask is that the Court strike down, in
   the first instance, the organizing standard of American child-custody law
   on a criminal-vagueness framework (*Kolender*, *Dimaya*) that has never
   been extended to discretionary civil custody standards. Flexible,
   multi-factor best-interests determinations are the historical norm the
   Court itself has described approvingly (e.g., in *Troxel v. Granville*'s
   recognition of broad state authority in custody matters).

3. **Vehicle defects.** The state court of appeals treated the constitutional
   argument as conclusory and inadequately developed (an independent,
   arguably adequate state-law ground of waiver); the ruling under review is
   a procedural affirmance of a denial for failure to comply with a state
   particularity rule, not a merits application of the factors; the claim is
   partially moot (the elder child turned 18, leaving only the 16-year-old,
   and the remaining controversy will age out); and the opinion below is
   unpublished and fact-bound.

4. **History of the dispute.** This is the petitioner's third cert petition
   arising from the same custody case — Nos. 19-356 (denied Nov. 18, 2019)
   and 23-1244 (denied Oct. 7, 2024), per the petition's own statement. The
   Court denied both without recorded dissent; nothing material has changed.

## Calibration

The zero-relist bucket's ~0.8% grant rate is the ceiling for this cell, and
every case-specific feature (pro se, family law, state intermediate court,
unpublished opinion, no split, no BIO, waiver/mootness vehicle problems, two
prior denials on the same dispute) pushes well below it. No GVR candidate
exists — there is no intervening decision touching this theory. I set
P(grant) = 0.002, disposition **denied**. Expected path: denied at or shortly
after the September 28, 2026 conference. A dismissal (e.g., withdrawal or
settlement) is possible but rarer than outright denial (~2% of dockets
overall), and denial dominates the distribution.

## Inputs used

- Snapshot `record/snapshots/2026-07-17.json` (docket 25-1296: filing,
  distribution, paid fee class, Term 2025, no BIO).
- Provisioned `record/documents/petition.txt` (23 pages, full text —
  questions presented, procedural history, merits argument).
- `metrics/statpack.md` base rates: modern cert disposition split, relist and
  CVSG cuts, per-Term paid/IFP grant rates (paid 2025: ~5.4%; 2024: ~6.9%);
  no salience-band table is present in the committed statpack, so I anchored
  on the relist-count cut instead.
- Two `fedcourts query` corpus pulls (see `retrieval.md`); the `--era modern`
  filter matched nothing (era labels are decade strings like `2020s`), and
  the unfiltered pull confirmed corpus rows carry no pro se/family-law facet
  close enough to this cell to sharpen the base rate further.
