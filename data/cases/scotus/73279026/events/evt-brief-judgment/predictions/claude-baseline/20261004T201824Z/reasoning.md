# Reasoning — why P(disturbed) = 0.90, judgment `reversed`, 6–3

## What I worked from

- `record/context.json`: mode `forward`, `date` cut at 2026-08-18, band `high` under `sal-v4` (a cert construct; not used as an anchor on this merits cell, per the stage rule), term 2025, three distributions, no CVSG.
- Snapshot `record/snapshots/2026-08-18.json` (70 docket entries, `snapshot_provenance: truncated`). It shows: petition docketed November 17, 2025; respondents tried to waive a response and the Court called for one on December 31, 2025; the United States filed as amicus for petitioners at the cert stage (January 30, 2026) and again on the merits (July 2, 2026); three conference distributions (January 9, April 2, April 17, 2026); **cert granted April 20, 2026 limited to Questions 1 and 2**, so the question whether to overrule Smith is out of the case; petitioners' merits brief June 25, respondents' merits brief August 17, argument set for November 3, 2026. Fifty docket entries recite amicus filings across both stages; the merits-stage amici include 43 Members of Congress, West Virginia and other States, the USCCB, and the Orthodox Union, all on petitioners' side as far as the entry text shows.
- Provisioned documents (`documents.json`): the QP section, the petition (truncated), the brief in opposition (truncated), and **both merits briefs in full** (`merits-brief-petitioner.txt`, 67 pages; `merits-brief-respondent.txt`, 74 pages; neither truncated, neither empty). This is a `briefed` cell and the respondents' brief sits exactly on the opening date, inside the cutoff, as the stage rule expects. I read both merits briefs (via delegated summaries of the full text) and the QP section directly; I did not read the cert-stage petition and BIO beyond confirming their presence, since the merits briefs supersede them.
- Committed `metrics/statpack.md`, merits-docket section.
- No reply brief and no argument transcript exist within my record, and the argument postdates today, so the forecast is from the two principal merits briefs and the docket.

## Anchor

The merits section publishes an `excluded` count, so it is quotable. The grant date is April 20, 2026, grant Term 2025, so the pool is grant Terms 2015–2024, strictly before. The table renders Terms 2017–2024 within that window (2015 and 2016 carry no parsed judgment). Pooling `disturbed` over `parsed` across 2017–2024:

| Terms pooled | parsed | disturbed | rate |
| --- | --: | --: | --- |
| 2017–2024 | 516 | 360 | 69.8% |

Coverage is near-complete for 2017–2023 (parsed within a few rows of granted) and still good for 2024 (73 of 75). That 69.8% is the baseline the cell's Brier skill is scored against, so it is the bar rather than a mere prior.

## Adjustments, up from 0.70 to 0.90

1. **The claimant class.** Since Trinity Lutheran (2017) the Court has ruled for the free-exercise claimant in every argued case of this shape: Trinity Lutheran, Espinoza, Carson, Fulton, Kennedy, Mahmoud, Catholic Charities v. Wisconsin, all reversals of judgments against the religious party. I know of no argued Free Exercise claim by a religious institution against a government condition that this Court has rejected in that span. That history is the largest single adjustment.
2. **The grant itself.** The petition framed an acknowledged 7–4 split in which the Tenth Circuit took the minority view, the Court called for a response after the State tried to waive, and it granted on the two questions that resolve the split while declining the invitation to overrule Smith. A Court that wanted to affirm a minority-position circuit on a question it has twice recently unsettled (Fulton, Tandon) would have had no reason to take this vehicle. The Solicitor General's support at both stages, after Mahmoud and Catholic Charities, is consistent with the Court's own recent direction rather than against it.
3. **The briefs.** Petitioners' brief (Becket) builds two independent routes to strict scrutiny and argues strict scrutiny in detail, and its general-applicability case has concrete hooks in this record: categorical income- and disability-based enrollment preferences, a discretionary "programmatic preference" catchall, the program director's testimony that a provider could favor secular subgroups, and a now-repealed congregation preference that implicated religion. Respondents' brief (Colorado AG) is competent and leans on the strongest material available to it, the bench-trial findings that the agency has no authority to waive the equal-opportunity rule and that the preferences are applications of the rule rather than exceptions to it. But the Court's recent cases treat the *availability* of individualized consideration, not its exercise, as the trigger (Fulton), and judge comparability against the asserted interest (Tandon). Respondents' position depends on the Court accepting a narrow reading of both, which is the reading the Court granted cert to examine.

## Why not higher

- **Record friction.** The Tenth Circuit and the district court found, as a matter of the regulation's text, that the catchall does not permit departures from the protected classes, and respondents repeatedly invoke deference to those findings. If the majority treats this as a factual finding about discretion rather than a legal characterization of the regime, the discretionary-exemption route weakens, leaving the categorical preferences, which respondents plausibly describe as serving the same equal-access goal. That is the path to an affirmance, and I give it real weight.
- **Standing and mootness noise.** One parish school closed in December 2024 and the Archdiocese was dismissed below for lack of standing. Neither threatens the whole case, but a Court looking for a narrow exit has one more handle than usual.
- **The disturbed axis.** A vacatur-and-remand still counts as disturbed, so the main residual mass in the 0.10 complement is a genuine affirmance (roughly 0.08) plus a small procedural tail (DIG or equally divided, roughly 0.02).

## Judgment label and votes

`reversed` rather than `vacated` because the Court in this line has consistently decided strict scrutiny itself on a developed record and entered a reversal (Fulton, Carson, Espinoza, Mahmoud); a remand for the lower courts to apply strict scrutiny afresh is possible but has been the exception. Within the disturbed mass I put roughly 0.70 on `reversed`, 0.18 on `vacated`, and a little on `affirmed-in-part-reversed-in-part` if the Court treats the two parishes differently.

The 6–3 lineup follows the LGBTQ-nondiscrimination cases (Mahmoud, 303 Creative) more than the funding-condition cases that drew Breyer or Kagan (Trinity Lutheran, Fulton), because the condition here is a sexual-orientation and gender-identity rule and the dissenters in Mahmoud have written separately on exactly this collision. Kagan concurring in the judgment is the most likely deviation; I would put 7–2 or wider at about one in four. Authorship is a low-confidence call (Roberts) based on his assignment of the funding-condition cases to himself; it is not scored.

## Semantic claims

Both claims are forecasts from the briefs and the Court's recent opinions, not from any post-decision material (none exists). `majority-ground` commits to Question 1 as the holding's basis and to a comparability-against-interest reading of Tandon plus Fulton's availability-of-exemption rule, with Carson treated as confirmatory at most. `ground-breadth` commits to a categorical statement of the general-applicability test that reaches past this program, with the Question 2 extension left for another day. The main way the breadth claim fails is if the Court writes a narrow opinion keyed to the director's testimony alone; the main way the ground claim fails is if the Court decides on Question 2 (Carson) instead and never reaches comparability.

## Big-case score

0.80. The case pairs a Catholic-school free-exercise claim with an LGBTQ-inclusive funding condition, resolves a long-standing split over Smith's general-applicability test, drew the United States as amicus, roughly fifty amicus entries, and the Court's rare call for a response after a waiver. It is not at the very top only because the Court declined to reconsider Smith itself.

## Retrieval and its limits

Forward mode, so retrieval was unrestricted. Two `fedcourts query` calls (recorded in `retrieval.md`) returned nothing useful for merits priors: the citation filter is almost unpopulated on SCOTUS rows and the granted-disposition sweep returns recency-ranked cert dockets without merits judgments. Three CourtListener MCP searches for the Tenth Circuit opinion returned no results, so the panel composition and the lower court's reasoning come from the two briefs, which agree that the panel was unanimous and affirmed a bench-trial judgment under rational-basis review. I did not search for or encounter any disposition of this case; none exists, since argument is a month away. I carry pre-grant knowledge of this litigation from training (the district court's 2024 judgment and the Tenth Circuit's September 2025 affirmance), none of it outcome-revealing for the event forecast here.

Where to discount me: the 0.90 leans heavily on an institutional pattern rather than on anything respondents conceded, and respondents' trial-court findings on agency discretion are the kind of record fact that has occasionally produced a narrower result than the grant foreshadowed.
