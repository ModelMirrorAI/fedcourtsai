# Why 0.44, and not another number

## What I worked from

Forward cell, `moment: briefed`, cutoff 2026-09-15 under a `date` cut. I read the
provisioned snapshot `record/snapshots/2026-09-15.json` (33 proceedings entries,
ending with respondent's merits brief on 14 Sept 2026) and every provisioned
document: `questions-presented.txt`, `petition.txt` (29 pp.),
`brief-in-opposition.txt` (40 pp.), `merits-brief-petitioner.txt` (63 pp.) and
`merits-brief-respondent.txt` (65 pp.), none flagged `empty_text` or truncated. The
two merits briefs were read in full by subagents and summarized to me; I read the
petition's and BIO's argument sections directly. Beyond the provisioned inputs
(forward mode, retrieval unrestricted) I read the Eighth Circuit opinion (132 F.4th
1058, Stras, J.) via CourtListener, the public supremecourt.gov docket, and the two
briefs of the United States: the CVSG brief of 22 May 2026 and the merits amicus
brief of 21 Sept 2026 supporting respondent. Nothing I retrieved contained or hinted
at a disposition; the case is set for argument on 9 Nov 2026.

## The anchor

Grant Term is OT2025 (Petition GRANTED 29 June 2026), so the pool is grant Terms
2015–2024. The statpack's merits section publishes an `excluded` column, so it is
quotable. The table renders only Terms with a parsed judgment, which here are
2017–2024; pooling those eight rows gives 360 disturbed over 516 parsed = **69.8%**
(coverage: parsed 516 of 539 granted in those Terms; the 2024 row is 73 of 75 and
2023 is 55 of 55, so censoring in this pool is modest). That is the baseline my
Brier skill is scored against, and I moved a long way below it, so the reader should
know why.

## Adjustments down from 0.70

1. **The Solicitor General supports respondent on the merits.** Invited at the cert
   stage, the SG said the Eighth Circuit was correct and recommended a grant to
   resolve the split; at the merits stage the United States filed supporting
   respondent and moved for divided argument. An invited SG who sides with the court
   below is the strongest single pull toward affirmance available at this moment, and
   the SG's position is doctrinally tight rather than policy-driven (Kohl/Miller/Bodcaw,
   the 1946 General Bridge Act contrast, the "practice and procedure" clause, the
   American Rule).
2. **The dispute is only attorney's fees.** The constitutional floor and the American
   Rule both exclude fees, and this Court has recently reaffirmed the American Rule
   (Lackey v. Stinnie, 2025). An affirmance can be written as an unexceptional
   fee-shifting case, which lowers the cost to any Justice of siding with a lone
   circuit against four.
3. **The lone circuit's opinion is the first-principles one.** The four-circuit
   consensus rests on Kimbell Foods gap-filling that the current Court treats
   skeptically; the Eleventh Circuit judges who felt bound by Georgia Power
   (Jordan, Grant) said they would have gone the Eighth Circuit's way on a clean
   slate, as did dissenters in the Third and Fifth Circuits. The grant after a
   three-relist-then-CVSG trajectory, with the SG recommending grant and affirmance,
   is at least as consistent with a Court minded to bring the circuits into line with
   the Eighth as with one minded to reverse it.
4. **PennEast.** The 2021 majority's "categorical delegation" language is the Eighth
   Circuit's and the SG's lead authority and is now settled precedent.

## Adjustments back up toward 0.5

1. **Reversal is the Court's default and this is a one-against-four split.** The
   Court more often grants to correct the outlier than to vindicate it.
2. **Petitioners' best argument is one this Court likes.** The Fifth Amendment is a
   floor on government, not a rule that a private condemnor pays only the minimum;
   a pipeline company is ordinarily subject to state law; the Rules of Decision Act
   defaults to state law; and treating the federal measure as self-executing against
   a private party looks like the federal common law Rodriguez v. FDIC (unanimous,
   Gorsuch) rejected. Forty years of state-law practice produced no obstruction the
   respondent could point to in the BIO.
3. **Property-rights trend and cross-ideological appeal.** Institute for Justice is
   counsel; Tyler, DeVillier, Sheetz, and Knick show a Court receptive to landowners,
   and the liberal Justices have no love for private eminent domain by pipelines.
   This is why I do not put P(affirm) above about 0.6.
4. **The forum clause.** § 717f(h) allows the action in state court too; a state
   court applying its own compensation law is awkward for the federal-uniformity
   story, and petitioners will press it.

Netting these, I land at **P(disturbed) = 0.44**: an affirmance is somewhat more
likely than not, with real weight on the other side. The vote block (7–2) is a
modal lineup, not a confident one; my confidence in the 0.44 is 0.35, and a 6–3 or
a reversal 5–4 the other way would not surprise me.

## Base rates I did not use

`band: high` is in my context, but this is a merits cell: the salience band scores a
grant likelihood that is already settled, and I did not anchor on it or the cert
tables. The two `fedcourts query` calls (recorded in `retrieval.md`) returned either
nothing (the citation column is sparse, as the tool's note said) or recent granted
dockets with no doctrinal similarity, so they contributed nothing to the number.

## Where to discount me

- The SG-as-amicus and one-versus-many adjustments are from general knowledge of the
  Court's behavior, not from a committed table; the pack publishes no such cut.
- I have not read the merits-stage amicus briefs (eight for petitioners, two for
  respondent) or any argument preview; I know their filers from the docket only.
- Whether North Dakota law treats fees as part of just compensation is contested
  (BIO; respondent's footnote preserving it for remand). If the Court finds that
  question dispositive it could affirm on a ground neither side briefed as primary,
  or DIG; I put the DIG at about 0.03 and folded the alternative affirmance into
  the 0.56.
- My vote lineup for the liberal Justices is the least-grounded part: Sotomayor
  joined the PennEast majority and Kagan joined Barrett's dissent, and neither
  datum speaks directly to the compensation question.
