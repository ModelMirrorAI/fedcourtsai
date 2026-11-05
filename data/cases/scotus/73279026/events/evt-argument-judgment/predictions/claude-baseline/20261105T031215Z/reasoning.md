# Reasoning — St. Mary Catholic Parish v. Roy (No. 25-581), argued moment

**P(judgment below disturbed) = 0.85; predicted judgment: reversed, 6–3.**

## What I worked from
- Mode `forward`, cutoff 2026-11-04, snapshot `record/snapshots/2026-11-04.json`. The docket shows cert
  granted 2026-04-20 **limited to Questions 1 and 2**. That means Question 3 (whether to overrule *Smith*)
  is off the table. The case was argued 2026-11-03, with the United States arguing as amicus for petitioners.
- Provisioned documents I read: the questions presented; the argument transcript, read in full for the
  questioning of each Justice; and `argument-features.json`. I also used the docket's record of the merits
  briefs, the U.S. amicus brief and the reply. The U.S. amicus brief supports **petitioners**, and its counsel
  at argument urged reversal on either ground, preferring the Carson/Sherbert public-benefits rule. My forecast
  follows that side, but it rests mainly on the bench, not on the SG.
- I did no web or CourtListener retrieval. The corpus query returned no useful doctrinal priors (see `retrieval.md`).

## Base rate
The statpack has a merits section that publishes an `excluded` column. The grant was 2026-04-20, so the grant
Term is OT2025. That makes the pool the grant Terms 2015–2024, and the table holds rows for 2017–2024:
disturbed 375 of 533 parsed, or **70.4%**. The pool is well above the 30-judgment floor, and those Terms are
fully parsed (parsed is close to granted). This is the bar I am scored against.

## Adjustment from the argument
I read questions as leanings, not votes, but the pattern was consistent:
- **Thomas, Alito, Gorsuch:** clearly for petitioners. Alito pressed Colorado on whether the State knew its
  condition would exclude these schools, on the lack of excluded families in the record, and on Colorado's
  record in *Masterpiece*, *303 Creative* and *Chiles*. Gorsuch said that a rule turning on express
  discrimination would gut *Sherbert*, *Thomas* and *Carson* ("substances, not shadows").
- **Kavanaugh:** posed the benefits-versus-ban "anomaly" to petitioners. But he pressed Colorado hard on its
  many secular preferences (parent involvement, STEM, vegetarian, single-sex schools), on the ban on
  co-religionist preference, and on the "win/win" point (34 Catholic schools out of about 2,000). That reads
  as a vote to reverse, probably on the general-applicability ground (Question 1).
- **Barrett:** pressed Colorado on imposing a condition it knows certain religious schools cannot meet, citing
  the post-*Carson* commentary that urged states to do exactly that. She also asked what problem the mandate
  solves other than the religious schools. On the petitioners' side she probed the limits of the Carson rule.
  I read her as leaning toward reversal, possibly on the narrower ground.
- **Roberts:** opened skeptical of extending *Carson* to facially neutral laws and worried about how far the
  rule would reach. Later, though, he told Colorado the law's effect is "pretty much the same as the effect
  of the law" in *Carson*, and that Colorado seemed "anxious to bury Sherbert," noting that nothing in the
  precedent has retreated from it. I read him as likely for reversal, but as the Justice most likely to
  insist on a narrow ground. He is the main source of my uncertainty.
- **Sotomayor, Kagan, Jackson:** strongly for Colorado. They framed petitioners' ask as a special exemption
  from a neutral antidiscrimination condition.

`argument-features.json` (coverage: 236 of 237 Justice turns attributed, 4 of 4 segments) is consistent with
this reading. Alito spoke about 647 words while respondent was at the lectern and about 219 while petitioners
were. Kavanaugh spoke about 721 words to respondent and about 425 to petitioners. Kagan and Jackson put most
of their words to the petitioner side. These counts measure who was questioned, not how anyone will vote.

I see five fairly firm votes to reverse plus a likely sixth (Roberts), and Question 1 offers an easy narrower
route. So I raise the 70% anchor to 0.85. The remaining 15% covers three things: Roberts or Barrett siding
with Colorado on a narrow reading of *Smith*; a vacatur-and-remand (which still counts as disturbed and does
not lower this number); and a small DIG risk, which is not live here.

## Votes
Predicted 6–3, split on ideological lines. Per-Justice disturb rates from OT2021–OT2024 (Terms strictly
before the OT2025 grant Term) are all in the 60–75% range, for example Roberts 38 of 51 in OT2024 and
Kavanaugh 39 of 51. Those rates do not separate the Justices, so the lineup rests on the argument.

## Authorship
Assignments for the November 2026 sitting are not yet known. Roberts wrote *Carson*, *Espinoza* and *Fulton*,
and he may keep a case decided on a narrow ground. Barrett and Kavanaugh are the next most likely authors.
For separate writings I expect: a Sotomayor dissent, probably joined by the others, with Jackson writing
separately at a high rate; concurrences from Gorsuch, Alito or Thomas pressing the Carson/Sherbert ground or
criticizing *Smith*; and possibly a Barrett concurrence like her *Fulton* concurrence.

## Where to discount me
The choice of ground (Question 1 or Question 2) is much less certain than the direction of the judgment.
The label `reversed` versus `vacated` is also uncertain: a remand to apply strict scrutiny could be phrased
either way, though the binary is unaffected.
