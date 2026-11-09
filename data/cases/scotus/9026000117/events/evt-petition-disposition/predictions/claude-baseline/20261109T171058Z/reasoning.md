# Reasoning — Allen v. Milligan, No. 26-117 (forward, distribution moment)

**P(any grant-family disposition) = 0.85; most likely label `gvr` (vacate and remand, most plausibly a Munsingwear vacatur or remand with instructions).**

## What this docket is
It is a **mandatory appeal** under 28 U.S.C. §1253 from a three-judge district court, filed as a jurisdictional statement. It is not a cert petition. The Court must dispose of it in one of these ways: note probable jurisdiction, summarily reverse, vacate and remand, summarily affirm, or dismiss. The usual cert base rate therefore understates action here. The appeal is from the May 26, 2026 preliminary injunction against Alabama's 2023 congressional plan. That injunction came on remand after *Louisiana v. Callais*, 146 S.Ct. 1131 (2026), and after the Court had vacated the earlier injunction (No. 25-274). The corpus records that earlier vacatur as `gvr`, which is how I calibrate the label for a vacatur on an appeal. On June 2, 2026 the Court **stayed** this injunction with a reasoned order (*Allen v. Milligan*, 146 S.Ct. 1377). According to the jurisdictional statement, that order said the district court failed to presume legislative good faith and departed from *Callais*.

## Inputs used
- Snapshot `2026-11-09.json`. Docketed July 24. Motion to dismiss or affirm filed Sept 18. Opposition filed Sept 29. Distributed for 10/16, 11/6 and 11/13. That is 3 distributions, consistent with `context.json`. The petition was carried past at least one conference, which signals that something is being written or held. The live supremecourt.gov docket matched the snapshot exactly.
- Provisioned `questions-presented.txt`, `petition.txt` (the jurisdictional statement) and `appendix.txt`. The jurisdictional statement asks for summary reversal, or alternatively for noting probable jurisdiction.
- The motion to dismiss or affirm was **not provisioned**. I fetched it from supremecourt.gov (forward mode) and read it through `fedcourts pdf-text`. Its lead argument is **mootness**. The injunction by its terms covered only the 2026 elections. Those elections went forward under the 2023 Plan because of the stay. Appellees cite *Honig* and *Camenisch*, and in the alternative ask for summary affirmance or plenary review.
- `same-question.json` lists 26-116 (Caster, cert before judgment) and 26-118 (Singleton) as identical companions, both pending.

## Anchors
- `cert_anchor.rate` = 0.348 (band `high`, sal-v8, ten-Term pool). This is the scored baseline. My number sits well above it for three reasons:
  1. Mandatory jurisdiction removes the "deny" option. Outright dismissal or summary affirmance is the only non-grant route.
  2. A majority already signalled its merits view in a reasoned stay.
  3. The Court has twice-plus carried the case past conference.

## Why 0.85 and `gvr`
The mootness argument looks strong on its face, because the injunction was time-limited to an election that has now passed. When an appeal becomes moot through the passage of time and not through the appellant's own act, the Court's customary course is a **Munsingwear vacatur**: vacate and remand with instructions to dismiss. That is a grant-family `gvr`, and it is what Alabama would want as the fallback. Summary reversal on *Callais* grounds is the other live route (~25%), with *Abbott v. LULAC*'s 2026 summary reversal as a template. Noting probable jurisdiction is less likely (~10%) because the injunction has expired.

Non-grant routes add up to about 15%:
- a plain dismissal as moot without vacatur (~10%);
- summary affirmance (very unlikely given the stay);
- holding the case or other residual outcomes.

## Claims
- **relist-increment 0.45.** The next conference is 11/13. The relists suggest a per curiam or a dissent is being written, and either could push the case past 11/13.
- **cvsg-increment 0.01.** It is an appeal, and the United States already participates as amicus.
- **summary-disposition-route 0.8.** Conditional on a grant, I expect a vacatur or summary reversal, not plenary review.
- **dissent-from-denial 0.6.** Conditional on a non-grant (a dismissal or affirmance), Thomas or Alito, possibly with Gorsuch, would likely write.

## Uncertainty
- I cannot tell whether the relists reflect a per curiam on the merits or only the mootness disposition.
- The Court could also simply dismiss. *Honig* itself dismissed without vacatur in one posture.
- Whether the outcome pipeline labels a vacatur-with-instructions-to-dismiss as `gvr` or `dismissed` is a capture risk. I have noted it in flags.json.
