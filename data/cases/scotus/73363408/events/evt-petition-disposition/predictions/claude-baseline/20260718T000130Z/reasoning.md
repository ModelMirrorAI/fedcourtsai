# Schmidt v. City of Omro, Wisconsin, et al. (No. 25-1293) — cert disposition

## The case

Dan Schmidt, proceeding pro se (paid docket, booklet-format petition), sued the
City of Omro, city officials, a bank, and the city's insurer (EMC) in Winnebago
County Circuit Court over water damage he attributes to a neighboring bank's
rebuilt concrete parking lot. The circuit court dismissed EMC and its adjuster
with prejudice in July 2023 under *Kranzush v. Badger State Mut. Cas. Co.* (no
third-party bad-faith claim against an insurer). Schmidt noticed an appeal only
in January 2025; the Wisconsin Court of Appeals dismissed it as untimely, and
the Wisconsin Supreme Court denied review on October 6, 2025.

## The questions presented

1. Whether the Fourteenth Amendment requires a state trial judge to inform a
   civil tort litigant of the state-created right to appeal, at the hearing and
   in the written dismissal order; and
2. if so, whether an "equitable exception" applies when the court merely says
   the dismissal is "with prejudice."

## Why this petition will almost certainly be denied

- **No genuine conflict.** The petition's own footnote string-cites show state
  courts uniformly holding that civil trial judges need not advise litigants of
  appeal rights. Uniformity against the petitioner is the opposite of a
  certworthy split; the ask is to create a new constitutional rule.
- **The claim runs against settled doctrine.** *McKane v. Durston* holds there
  is no federal constitutional right to appeal at all; the advisement cases the
  petition relies on (*Rodriguez*, *Peguero*, *Garza*) are criminal-procedure
  rules rooted in Fed. R. Crim. P. 32 and counsel's Sixth Amendment duties, and
  *Peguero* itself requires prejudice even there. The analogy to *Hunter v.
  United States* (a criminal appeal-waiver case) is superficial.
- **Vehicle defects.** The state-court dismissal of the appeal rests on a state
  procedural timeliness ground (Wis. Stat. § 808.03(1) finality rules), an
  adequate-and-independent-state-ground problem; the federal question was never
  passed on below; and the underlying merits dispute is a fact-bound drainage
  tort.
- **Docket signals are all negative.** The named respondents waived response;
  the Court distributed the petition on July 1, 2026 for the September 28, 2026
  long conference without requesting a response — the Court essentially never
  grants plenary review without first calling for a response. No CVSG, no
  amici, no relists (zero-relist petitions grant at ~0.8% in the corpus
  statpack; the modern overall grant rate is ~2.5–3%).
- **Pro se petitions**, even paid ones, grant at rates far below the paid-docket
  average.

No plausible GVR hook exists: *Hunter* (if decided this coming Term) concerns
criminal appeal waivers, not a civil-advisement duty, so an intervening-decision
GVR is a remote possibility at best and does not move the number materially.

## Probability

Starting from the modern discretionary-cert anchor (~2.5–3% grant), then
adjusting sharply down for: no split, no response requested, zero relists,
state-court civil posture with an independent state procedural ground, and pro
se presentation. I put **P(grant, including GVR) at 0.003** and predict
**denied**, most likely shortly after the September 28, 2026 long conference.

## Inputs used

- Snapshot `record/snapshots/2026-07-17.json` (docket, parties, proceedings).
- `record/documents/questions-presented.txt` and `record/documents/petition.txt`
  (full 42-page petition text; no brief in opposition exists — respondents
  waived).
- Committed base rates in `metrics/statpack.md`; corpus priors via
  `fedcourts query` (see `retrieval.md`).
