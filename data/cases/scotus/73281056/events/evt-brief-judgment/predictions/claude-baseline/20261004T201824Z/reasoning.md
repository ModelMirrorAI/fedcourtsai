# Why these numbers

**P(disturbed) = 0.90, judgment `reversed`, 6–3.**

## What I worked from

- The provisioned snapshot `2026-08-29.json` (docket as of the August 28, 2026
  filings), `context.json` (mode `forward`, cutoff 2026-08-29, `date` cut), and
  `event.yaml` (stage `merits`, moment `briefed`).
- `record/documents/`: the petition and questions presented (February 2026), the
  concatenated briefs in opposition (DNC, the AANHPI/LUCHA coalition, and a
  truncated Mi Familia Vota brief), the RNC's brief on the merits
  (`merits-brief-petitioner.txt`, 65 pages, read in full), and
  `merits-brief-respondent.txt`, which is **not** an adverse brief: it is the
  State of Arizona and its Attorney General's brief *in partial support of
  petitioner*, read in full. I delegated a close read of the petition and the
  BIOs to a subagent and read the two merits briefs myself.
- The committed statpack's merits section and two corpus `query` calls (none
  on point; see `retrieval.md`). Three CourtListener MCP calls looking for the
  Ninth Circuit panel composition, which did not surface it.

**The adverse respondents have not yet briefed.** The docket shows their merits
briefs due October 13, 2026. The August 28 "respondent" filings are all aligned
with the petitioner (United States in support, the Arizona legislative leaders
in support, Arizona in partial support). So this `briefed` cell is forecasting
from the petitioner's side of the merits briefing plus the cert-stage BIOs,
not from "both sides' merits arguments" as the event description assumes. I
have flagged that in `flags.json`. A reader should discount the semantic
claims accordingly: the respondents' best merits-stage framing is one I have
inferred from their BIOs rather than read.

## Anchor

The statpack's "The merits docket (granted cases)" section publishes an
`excluded` count (66), so it is quotable. The grant date is June 29, 2026,
which is October Term 2025, so the pool is grant Terms 2015–2024. The table
renders only Terms with a parsed judgment; within that window it holds 2017
through 2024 (2015 and 2016 are absent). Pooled `disturbed` over `parsed`:

| Term | parsed | disturbed |
| --- | --: | --: |
| 2024 | 73 | 50 |
| 2023 | 55 | 34 |
| 2022 | 73 | 50 |
| 2021 | 65 | 46 |
| 2020 | 69 | 57 |
| 2019 | 54 | 42 |
| 2018 | 75 | 50 |
| 2017 | 52 | 31 |
| **pool** | **516** | **360** |

That is a baseline disturbed rate of **69.8%** on 516 parsed judgments, well
above the 30-judgment floor. Coverage is high in every pooled Term (2024: 73 of
75 granted parsed, with 34 cert-order grants excluded; 2023: 55 of 55), so the
pool is not pendency-censored in any way that matters. This is the bar my Brier
skill is scored against. I did not use the salience band (`elevated`) in
`context.json`; it priced grant likelihood, which is settled.

## Adjustments up from 0.70 to 0.90

1. **The Court has already acted on both questions on the emergency docket.**
   In August 2024 it stayed the district court's injunction precisely as to the
   state-form proof-of-citizenship requirement (24A164, 5–4 on that portion), and
   in October 2024 it stayed a Fourth Circuit-affirmed order that applied the
   90-day provision to Virginia's noncitizen cancellation program (Beals, 6–3).
   Both rulings predate the snapshot and are public; both are cited in the
   petition and the BIOs. A stay requires a fair prospect of reversal, and the
   petition's own framing of "a stay on each issue" is why I treat the grant here
   as a grant to reverse rather than to affirm.
2. **The petitioner's text is close to Inter Tribal Council's.** Justice
   Scalia's 2013 opinion, joined by seven Justices, described state forms as
   able to "require information the Federal Form does not," named proof of
   citizenship as the example, and raised "serious constitutional doubts" about a
   reading that stops a State enforcing its qualifications. The Ninth Circuit's
   NVRA holding did not cite that passage. The current Court will not let a
   lower court read around a textual signal of its own.
3. **The United States switched sides and supports the petitioner**, and
   Arizona itself, through a Democratic Attorney General, argues the NVRA
   question for the petitioner. Only the consent-decree holding has a defender
   among the governmental respondents, and even Arizona's defense is "binding
   until modified under Rule 60(b)" rather than "correct forever."
4. **The Ninth Circuit split badly below**: a 2–1 panel, a unanimous motions
   panel that had stayed the ruling, and eleven dissenters from the denial of
   rehearing en banc. That is the usual shape of a reversal.

## Why not higher

- **Affirmance (~7%).** Leaving the judgment undisturbed requires the Court to
  uphold *both* the first-question injunction (on either the consent decree or
  the NVRA) *and* the 90-day holding. Arizona's brief gives the consent-decree
  ground a credible, moderate defence (Celotex/GTE Sylvania: obey until
  modified), and the "any program ... ineligible voters" text is not frivolous;
  the DNC's enumerated-exceptions argument has force. But Beals makes it hard to
  see six votes against the petitioner on the 90-day question, and the NVRA
  alternative holding has to survive Inter Tribal Council. I put the joint
  probability of affirming everything at under a tenth.
- **DIG / jurisdictional exit (~3%).** The AANHPI respondents lead with the
  RNC's standing to appeal the 90-day ruling alone; no state party appealed it
  and no stay was ever sought on it. The Court granted without adding a
  standing question, and the RNC's standing was accepted below, so I treat this
  as a small risk of a partial vacatur (which would still count as disturbed) or
  a DIG (which would not).
- **Partial affirmance.** If the Court holds the consent decree binds the
  Secretary until modified while rejecting the NVRA grounds, the label is
  "affirmed-in-part-reversed-in-part," still disturbed. That is why `judgment`
  is `reversed` at roughly 45% rather than higher, while `probability` stays
  at 0.90: the label uncertainty is mostly among disturbed outcomes.

## Votes

The 2024 stay split the Court 5–4 on the state-form question, with Justices
Sotomayor, Kagan, Barrett, and Jackson voting to deny all relief (as the AANHPI
BIO reports). Beals was 6–3 with the three liberal Justices dissenting, so
Justice Barrett joined the majority on the 90-day question in that posture. On
full briefing, with Inter Tribal Council's text in front of her, I expect her to
join the majority on the first question too; the stay denial is better explained
by the emergency posture and the Ninth Circuit's procedural tangle than by a
merits view. My alternative is a 5–4 judgment with Barrett splitting. I list no
writing roles because no artifact records them; authorship speculation is in
`predicted_reasoning.md`.

## Semantic claims

The `majority-ground` claim is that the Court rests on the NVRA text (and the
Inter Tribal Council / avoidance frame) rather than deciding the case on the
consent decree alone. The `ground-breadth` claim is that the rule is stated
categorically for all States rather than through Arizona's own eligibility
statutes (Arizona's brief offers that narrower, Arizona-specific route: proof of
citizenship is "necessary" because Arizona law makes it an eligibility
requirement). Those are the two forks a competent reader of this record could
take the other way.

## Where to discount me

- I know the 2024 and Beals stay orders from public record and training, not
  from retrieval; they predate the snapshot and are proper forward signal, but
  they are also the bulk of my adjustment above the base rate.
- I have not read the adverse respondents' merits briefs (not yet filed) or the
  United States' and legislative leaders' August 28 briefs (not provisioned; only
  one row per side is fetched).
- I could not confirm the Ninth Circuit panel's majority composition from the
  record or CourtListener; the forecast does not depend on it.
- `confidence` 0.70 reflects that the direction is clear but the label and the
  lineup carry real spread.
