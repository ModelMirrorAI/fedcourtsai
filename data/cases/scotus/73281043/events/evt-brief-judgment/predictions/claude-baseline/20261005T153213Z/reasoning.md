# Reasoning — Guerrero v. Johnson, No. 25-1003 (evt-brief-judgment)

**P(disturbed) 0.83; judgment `reversed`; 7–2.** Forward merits cell at the
`briefed` moment; argument is set for November 4, 2026 and nothing I consulted
contained a disposition.

## What I worked from

- The provisioned snapshot `record/snapshots/2026-09-19.json` (cutoff
  2026-09-19, `date` cut): docketed February 23, 2026 as a paid capital case;
  three distributions (conferences of 5/28, 6/4, 6/11); petition granted
  June 15, 2026; petitioner's merits brief and joint appendix July 30; amicus
  briefs of the United States, Louisiana et al., and Protasio Aparece on
  August 6; argument set August 11 for November 4; respondent's merits brief
  September 18, the entry that opened this event.
- `record/documents/`: `questions-presented.txt`, `petition.txt` (117 pages,
  `truncated: true`, cut off before the petition's vehicle section),
  `brief-in-opposition.txt`, `merits-brief-petitioner.txt` (55 pages), and
  `merits-brief-respondent.txt` (49 pages). None was `empty_text`. Both merits
  briefs are inside the cutoff, which is the rule for a `briefed` cell, so I
  read and relied on them. I had subagents summarize the three long documents
  and worked from those summaries plus the QP text; I did not reproduce the
  briefs.
- `metrics/statpack.md`, merits section, for the baseline.
- CourtListener MCP (four searches) to locate the Fifth Circuit's 2019
  authorization opinion (*In re Johnson*, 935 F.3d 284) and the Eleventh
  Circuit's *In re Bowles*; I did not read either body, since the briefs
  describe them consistently. The index did not return the July 2025
  unpublished panel opinion or the en banc denial.
- One `fedcourts query` call, which cannot filter by doctrine and contributed
  nothing beyond confirming the tool works.

## The baseline

Grant date June 15, 2026, so the grant Term is OT2025 and the pool is grant
Terms 2015–2024. The merits table publishes an `excluded` column, so it is
quotable. Terms 2015 and 2016 are not rendered (no parsed judgment), so the
pool is the rendered 2017–2024 rows:

| pooled Terms | parsed | disturbed | rate |
| --- | --: | --: | --- |
| 2017–2024 | 516 | 360 | 69.8% |

Coverage: 2024 is 73 parsed of 75 granted, and the older rows are near
complete, so censoring is slight. That is the yardstick my Brier skill is
scored against, and it is my starting point. The context's `band: high` is a
cert construct and plays no part here.

## Adjustments from the baseline

Up, substantially, for four reasons.

1. **Who sought review.** A state petitioner won certiorari against a
   prisoner-favorable Fifth Circuit ruling in a capital AEDPA case, over an
   interlocutory-posture objection. The Court grants a state's AEDPA petition
   to correct, not to affirm, far more often than the pooled rate suggests.
2. **The text.** Johnson's own brief concedes that "previously unavailable"
   modifies "rule." *Atkins* was decided in 2002, before his crime, his 2007
   conviction, and his 2011 federal petition. Once availability is a property
   of the rule, the Fifth Circuit's *Cathey* "some possibility of merit" test
   has to be defended as an account of what "available" means, and the
   structural point that it lets new-evidence claims evade § 2244(b)(2)(B)'s
   innocence gate is one this Court has found persuasive in *Jones v.
   Hendrix* and the rest of its recent AEDPA line.
3. **The Solicitor General.** The United States filed on the petitioner-side
   amicus deadline (August 6) and is listed on the docket; the parallel
   § 2255(h)(2) language gives the federal government a direct stake in
   Texas's reading. I did not fetch the brief and infer its side from the
   filing date.
4. **The Court's record on § 2244(b).** *Rivers v. Guerrero* (2025) was
   unanimous for Texas on the successive-petition bar, and the Court's recent
   habeas decisions (*Shinn*, *Shoop*, *Brown v. Davenport*, *Edwards v.
   Vannoy*, *Jones v. Hendrix*, *Thornell v. Jones*) have gone the state's way
   by at least 6–3.

Down, modestly, for three reasons.

1. **The DIG argument is real.** Johnson shows that the Director's framing
   moved from "judicially created exceptions" below, to "could have asserted a
   claim" in the petition, to "when this Court announced the rule" in the
   merits brief. The Court rarely DIGs on party-presentation grounds once it
   has heard argument, but this one is cleaner than most. I put it at about
   0.05, and a DIG counts as undisturbed.
2. **Johnson's reading has a respectable pedigree.** *Ross v. Blake* and
   *Booth v. Churner* read "available" in the PLRA as "capable of use,"
   and the Director concedes a practical test for a rule announced while a
   prior petition is pending, which Johnson turns into an internal
   inconsistency. A majority could accept that framing and still affirm.
3. **Equities.** The underlying claim is that a possibly intellectually
   disabled prisoner will be executed without any court assessing the claim
   under current criteria. That matters to at least two Justices and could
   pull a third, which affects the lineup more than the judgment.

Netting these: P(reverse or vacate) ≈ 0.83, P(affirm) ≈ 0.12, P(DIG) ≈ 0.05.
I chose `reversed` over `vacated` because the Director asks for outright
reversal of the judgment affirming the denial of dismissal and the Court's
ruling would dispose of the gatekeeping question itself; a "vacated and
remanded" label is a live alternative and would score the same on the
disturbed axis.

## The vote block

Six conservative Justices in the majority at high confidence. Kagan is the
swing on the lineup, not on the judgment; I place her in the majority at a
little above even odds for the textual-concession and *Rivers* reasons above.
Sotomayor and Jackson in dissent. The block is banked rather than scored
today, and I have not forecast writing roles in it.

## Big case score

0.42. The question governs the gate for every successive federal habeas
petition under (A) and (h)(2), and it is a capital case with the SG and a
multistate coalition as amici, but it is technical and the cert-stage docket
shows only one private amicus. Stakes, not odds.

## Where to discount me

- I did not read the Fifth Circuit's 2025 opinion, the en banc denial, or any
  amicus brief directly; the parties' summaries agree on the history, but a
  reader with the SG's brief in hand could sharpen the argument-3 inference.
- The petition text was truncated before its vehicle section; the BIO's
  vehicle arguments were read in full, so the asymmetry favors Johnson
  slightly in what I saw.
- My P(DIG) rests on general experience with party-presentation DIGs, not on
  a committed base rate; the statpack pool shows 12 DIGs in 540 parsed
  judgments (about 2%), and I have roughly doubled that for this record.
- The Kagan vote is close to a coin flip and I have said so.
