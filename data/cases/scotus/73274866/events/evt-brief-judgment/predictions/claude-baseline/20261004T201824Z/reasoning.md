# Reasoning: why P(disturbed) = 0.42, judgment `affirmed`

## Cell and inputs

Forward merits cell, `moment: briefed` (`evt-brief-judgment`, opened
2026-08-17 when respondents' merits brief was filed). `record/context.json`:
`mode: forward`, `cut_kind: date`, `cutoff: 2026-08-18`, `snapshot_date:
2026-08-18`, `band: high` under `sal-v4`, `distribution_count: 4`, `cvsg_date:
2025-12-08`, `term: 2025`. I read `record/snapshots/2026-08-18.json` (the
provisioned baseline, named as `input_snapshot`). The band and the cert
signals are spent on a merits cell and were not used as an anchor.

Provisioned documents read (all `empty_text: false`):
`questions-presented.txt`; `petition.txt` (203 pp., truncated — the joint
petition with appendix, including the Eleventh Circuit panel caption);
`brief-in-opposition.txt` (41 pp.); `merits-brief-petitioner.txt` (70 pp.,
filed 2026-07-10); `merits-brief-respondent.txt` (67 pp., filed 2026-08-17).
Both merits briefs fall inside the cutoff, as the briefed moment's rule says
they should, so this forecast was made from both sides' merits arguments, not
from the docket skeleton. I skimmed the summaries of argument, tables of
contents and the passages that characterize the United States' position; I did
not read either brief end to end.

Retrieval beyond the record (forward mode, unrestricted; see `retrieval.md`):
the SCOTUSblog case page, the live supremecourt.gov docket page, and the text
of the Solicitor General's CVSG brief (filed 2026-04-09), which was not
provisioned although it is a filed document on this docket. No MCP or corpus
query was made.

## Baseline

The committed `metrics/statpack.md` carries "The merits docket (granted
cases)" with an `excluded` count (66 grants removed by the pool guard), so it
is quotable and is the bar this cell's skill will be scored against.
Certiorari was granted 2026-05-18, so the grant Term is OT2025 and the pool is
grant Terms 2015–2024. The table renders every Term the pack holds and the
earliest row is 2017, so the pool is the eight rendered rows 2017–2024:

| window | parsed | disturbed | rate |
| --- | --: | --: | --- |
| grant Terms 2017–2024 (strictly before 2025) | 516 | 360 | 69.8% |

Coverage behind that: `parsed` runs close to `granted` for 2017–2023 (52/56,
75/77, 54/56, 69/79, 65/67, 73/74, 55/55) and 73/75 for 2024, so censoring in
the pool is slight; the 2025 row (24 parsed of 50, 70.8%) is my own Term and
is excluded by the strictly-prior rule. The pooled figure clears the
30-parsed-judgment floor by a wide margin. Note the pool is dominated by
reversals and vacaturs because the Court mostly grants to correct error, which
is the population this case is drawn from — but the composition of *which*
side the error ran against varies, and that is where the adjustment below
comes from.

## Adjustment from the baseline

I move from ~0.70 to **0.42**, a large downward adjustment, on five
considerations. The first two carry most of the weight.

1. **The Solicitor General is against the petitioners, after switching
   sides.** At the Court's invitation the SG recommended grant but said the
   Eleventh Circuit is *correct*: Title IX "does not provide employees ... a
   private right of action," and the Court should not "expand" Cannon to a
   new remedial context. The brief expressly repudiates the government's own
   position in Lakoski (1996) and Doe v. Mercy (2017), where it had urged the
   opposite. At the merits stage the United States filed in support of
   respondents on 2026-08-24 and moved for divided argument time. An SG
   recommending grant *to affirm* against an eight-circuit consensus is a
   signal that the government expects a receptive majority, and the SG's
   side as amicus wins well more often than not. This is the single biggest
   driver below the baseline. I discount it somewhat because the current
   SG's positions on civil-rights remedies are collinear with the
   conservative Justices' priors rather than independent evidence about
   them, and because the SG has lost text-driven Title VII/IX cases before
   (Bostock).

2. **The question sits squarely in a doctrinal line where six Justices are on
   record.** The respondents' and SG's framing — scope of an implied remedy
   is a question of remedial intent distinct from the prohibition's reach
   (Sandoval, Gonzaga, Virginia Bankshares, Gebser) — is the Court's current
   framework, and the recent decisions the respondents lean on (Cummings
   2022, Medina 2025 with its footnote retreating from Cannon's reasoning,
   and the 2026 decisions in FS Credit and Cisco they quote for the Court
   having "virtually eliminated" judicially created causes of action) all ran
   against implied remedies with the six Republican appointees in the
   majority. Kavanaugh's Cummings concurrence, joined by Gorsuch, said in
   terms that "Congress, not this Court, should extend" Title IX's implied
   cause of action; the SG's brief quotes that line as its thesis. The Title
   VII structural argument (Congress extended Title VII to educational
   employers three months before Title IX; Novotny; Brown v. GSA) gives the
   majority a "no remedial gap" story that makes affirmance look modest.
   Every one of the Court's close Title IX implied-right cases (Gebser 5–4,
   Davis 5–4, Jackson 5–4, Cummings 6–3) split on ideological lines, and
   Jackson's four dissenters' successors are all more skeptical of implied
   rights than Rehnquist and Kennedy were.

3. **The petitioners' textual and ratification argument is strong enough to
   keep this well above a lopsided number.** North Haven v. Bell (1982) holds
   section 901 covers employment, and the respondents concede it. Sandoval's
   own rule — "A Congress that intends the statute to be enforced through a
   private cause of action intends the authoritative interpretation of the
   statute to be so enforced as well" — plus 42 U.S.C. 2000d-7's express
   reference to suits "for a violation" of Title IX, enacted four years
   after Bell, is exactly the sort of argument that moves Gorsuch and
   Barrett. Jackson v. Birmingham already let an employee sue, framing the
   test as whether the conduct "falls within the statute's prohibition of
   intentional discrimination on the basis of sex," and Fitzgerald (2009,
   unanimous) rejected treating Title IX as displaced by or displacing a
   parallel remedy. Eight circuits over three decades read the statute the
   petitioners' way; the Court sides with the majority of circuits more often
   than not, though far from always. This is why I stop at 0.42 rather than
   0.30.

4. **The Court's reason for granting is ambiguous.** The petition was
   distributed three times before the CVSG and granted at the first
   conference after the SG's brief. An 8–3 split on a recurring question is a
   grant either way, so the grant itself tells me little about direction; the
   CVSG having been issued at all, and then the SG's recommendation being
   followed, tilts slightly toward the Court being interested in the SG's
   answer, not just the split.

5. **Lower-court and advocacy signals.** The decision below is a Chief Judge
   Pryor opinion that the SG describes as "faithfully appl[ying]" Sandoval,
   with a Pryor statement respecting denial of rehearing — the kind of
   methodical conservative opinion this Court tends to affirm rather than
   summarily correct. Respondents are represented by WilmerHale and the
   Georgia Solicitor General and are supported by 21 states, the Chamber of
   Commerce and the school-board associations; petitioners by Holwell
   Shuster with NEA, NWLC, CAC and Lambda Legal. That alignment is the
   ordinary ideological one and adds little beyond consideration 2.

Net: the base rate says 0.70; the case-specific evidence says this is a case
the current majority was likely invited to take in order to prune, not to
restore. I put P(disturbed) at 0.42, which makes `affirmed` the modal
judgment and sets `granted = 0`. I hold the number with moderate confidence
(0.5): the gap between my 0.42 and the 0.70 bar is the measurement of how much
I trust the SG-plus-doctrine reading over the text-plus-consensus reading, and
a reader who weights the latter more should move toward 0.55.

## Vote block

Scored intersection-only and currently banked, so I list all nine. 6–3 to
affirm (Roberts, Thomas, Alito, Gorsuch, Kavanaugh, Barrett / Sotomayor,
Kagan, Jackson). Gorsuch and Barrett are the uncertain votes; the lineup I
give is the single most likely one, not a confident one. I left `writing`
null for every Justice rather than forecasting authorship.

## Semantic claims

`majority-ground` states the remedial-intent / Title VII-structure ground the
respondents and SG argue; `ground-breadth` states a categorical rule covering
all employees regardless of their Title VII access, with Cannon, Jackson and
the funding remedy preserved. Both are conditional on the judgment being
affirmed; if the Court reverses, both will grade poorly, which is the honest
consequence of a single-proposition forecast.

## Where to discount me

- I know this case only from the record and the briefs; I have no knowledge of
  its outcome (argument is 2026-11-30), and nothing I retrieved revealed one.
- The 2026 decisions the respondents quote (FS Credit, Cisco, Landor, B.P.J.)
  postdate my training and I know them only as characterized in the briefs.
  If they are less hostile to implied remedies than the respondents' quotes
  suggest, consideration 2 is overstated.
- I did not read the respondent-side amicus briefs or the petitioners' reply
  (2026-09-16), both of which postdate the cutoff and are legitimate forward
  material I chose not to retrieve to stay within the retrieval budget.
- No corpus query was run, so the "ideological split in close Title IX cases"
  claim rests on my own knowledge of the reported decisions, not on
  retrieved priors.
