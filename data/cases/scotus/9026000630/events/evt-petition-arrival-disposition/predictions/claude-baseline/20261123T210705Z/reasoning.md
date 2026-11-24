# Reasoning for my numbers

**P(any grant) = 0.60; label `gvr`.**

## What I had
- Snapshot `2026-11-14.json`: petition filed Nov 10, 2026, docketed Nov 13; Solicitor General for federal petitioners (DHS Secretary et al.); respondent Jose Arnulfo Guerrero Orellana represented by the ACLU; from the First Circuit (Nos. 25-2152, 26-1094, judgment Aug 13, 2026); paid; response due Dec 14, 2026. No distribution, no CVSG, which is the arrival moment's definition.
- `paper_only_filings: true` (Rule 34.6 entry). No documents were staged, not even the government's petition, so I have **not read the questions presented**. `same-question.json` has `petitions: null` for the same reason. What the petition asks is inferred from the case's public history, not from its text.
- Context: band `federal`, sal-v9, `cert_anchor.rate` 0.731; amicus line (`none` arm) 0.689, n=151.

## Anchor
The frozen anchor for a federal petitioner is 0.731. The statpack table rendered is headed sal-v8 while my context says sal-v9; I used the frozen `cert_anchor` (pooled under my own version) rather than the table, and read the table only for shape (federal column 48%–96% by Term, small n per Term).

## Case-specific adjustment
Public history (web search, see `retrieval.md`): *Guerrero Orellana v. Moniz* is the D. Mass. class action in which the district court held that noncitizens arrested in the interior after entering without inspection are detained under 8 U.S.C. 1226(a) (bond-eligible), not 1225(b)(2)(A), and certified a New England class. That is the *Matter of Yajure Hurtado* question, on which the circuits have split (Fifth and Eighth for the government; most others against).

The decisive fact, which predates my snapshot: the Court **granted the government's petition on that question on October 1, 2026** in *Rhoney v. Barbosa da Cunha*, No. 26-104 (from the Second Circuit). I confirmed this on the corpus row for 26-104 and on the Court's docket page. Petitioner's merits brief there is due Nov 30, 2026 and respondent's Jan 13, 2027. This petition was filed six weeks after that grant, with the same counsel on both sides, so it is almost certainly a hold-for-*Rhoney* petition, possibly with class-specific questions added.

So the forecast is mostly a forecast of *Rhoney*'s merits:
- P(government wins *Rhoney*, or the Court vacates on a ground that touches this judgment) about 0.52. For the government: the Court took the government's petition, the textual argument ("applicant for admission") has persuaded two circuits, and the Court's majority has generally read the detention provisions in the government's favour (*Jennings*, *Johnson v. Arteaga-Martinez*). Against: a large majority of circuits and district courts rejected the reading, *Jennings* itself described 1226 as covering those already in the country, and the agency followed the opposite practice for decades. I treat it as close to a coin flip with a slight lean to the government.
- Given that, P(GVR here) about 0.95.
- Given a clean government loss, P(grant of any kind here) about 0.15: a GVR anyway because the opinion bears on class relief, or a plenary grant on a class-relief or 1252(f)(1) question that I cannot see because the petition is on paper.
- Small allowance (about 0.03 in total) for a plenary grant before *Rhoney* is decided, and a small discount for dismissal or mootness (Rule 46, a change of policy).

0.52 × 0.95 + 0.48 × 0.15 + adjustments gives about 0.58–0.62. I wrote 0.60, below the 0.73 anchor, because this petition's fate is tied to a single merits case that I rate as near even, whereas the anchor pools SG petitions that the Court takes on their own strength.

## Other claims
- `relist-increment` 0.97: from zero distributions, any distribution resolves it true; only a pre-distribution dismissal would not.
- `cvsg-increment` 0.003: the United States is the petitioner.
- `summary-disposition-route` 0.90: conditional on a grant, a GVR is the dominant route.
- `dissent-from-denial` 0.04: a post-*Rhoney* denial of a held government petition rarely draws a writing.
- `order-writers`: small for everyone; slightly higher for Sotomayor and Jackson (dissent from a GVR) and Thomas and Alito (dissent from a denial).

## Where to discount me
- I did not read the petition. If it presents an independent question the Court wants (class-wide relief against detention policy), the plenary-grant path is larger than I allow.
- My *Rhoney* merits estimate is a judgement from general knowledge, with no merits briefs or argument read.
- No prediction or forecast of this case by anyone else was sought or seen. The search results were news and legal summaries of the split and of the *Rhoney* grant.
