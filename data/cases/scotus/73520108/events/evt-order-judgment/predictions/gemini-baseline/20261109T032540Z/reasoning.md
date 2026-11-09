# Predictor Rationale (`reasoning.md`)

## Summary of Call
- **Stage / Moment:** `merits` / `grant` (`evt-order-judgment`, opened `2026-11-06`, forward mode, cutoff `2026-11-07`)
- **`probability` (P(judgment below disturbed)):** `0.79` (`granted = 1`, `predicted_disposition = "other"`)
- **`judgment`:** `reversed`
- **Expected Vote Split:** 7–2 (`Roberts`, `Thomas`, `Alito`, `Kagan`, `Gorsuch`, `Kavanaugh`, `Barrett` in the majority; `Sotomayor` and `Jackson` in dissent)
- **`big_case_score`:** `0.58`

## Provisioned Inputs Consulted
I read the provisioned snapshot `data/cases/scotus/73520108/record/snapshots/2026-11-07.json`, `record/context.json`, and all staged documents listed in `record/documents/documents.json`:
1. `questions-presented.txt` (the petition's single question presented on whether and under what circumstances a bankruptcy court may override the FAA with respect to 11 U.S.C. § 362(k) claims).
2. `petition.txt` (Goldman Sachs Bank USA's certiorari petition and appendix, including the Fourth Circuit majority and dissenting opinions, the Fourth Circuit order denying a stay of the mandate with Judge King's dissent, the district court opinion, and the bankruptcy court opinion; truncated only at the very end of the statutory appendix on PDF page 106).
3. `brief-in-opposition.txt` (Respondents Rhea Ann Brown and Gregory Kevin Maze's brief in opposition).
4. `cert-reply.txt` (Petitioner's cert-stage reply brief).
5. `supplemental-brief.txt` (Respondents' September 14, 2026 supplemental brief reporting the bankruptcy court's September 10, 2026 dismissal of the original complaint without prejudice for failure to adequately allege actual damages, with 21 days' leave to amend, and reiterating their reliance on 11 U.S.C. § 105(a)).
6. `decision-below.txt` and `lower-court-docket.txt` (the published March 18, 2026 Fourth Circuit decision in No. 25-1439, *Brown v. Goldman Sachs Bank USA*, authored by Judge Niemeyer and joined by Judge Berner, with Judge King dissenting).

Because this is a `moment: grant` cell with `cutoff: "2026-11-07"`, no merits briefs (`merits-brief-petitioner.txt`, `merits-brief-respondent.txt`, or `merits-amicus-united-states.txt`) or oral argument transcript exist yet or were provisioned on disk. In keeping with the stage rules, I did not anchor on `context.json`'s cert-stage salience `band` (`high`) or `distribution_count` (`4`), which are spent cert-stage signals.

## Base-Rate Anchor (`metrics/statpack.md`)

### 1. Merits Disturbed Rate
Per the prompt contract, a merits cell anchors on the **"The merits docket (granted cases)"** section of `metrics/statpack.md`, which publishes an `excluded (not in granted)` column (28 excluded grants across all Terms) and is therefore quotable and serves as the registered Brier baseline.
- **Grant Term:** Certiorari was granted on November 6, 2026 (`Nov 06 2026: Petition GRANTED`, `opened_at: "2026-11-06"`), placing this case in **grant Term OT2026** (`grant_term = 2026`), even though the petition bears an OT2025 docket number (`25-1408`).
- **Strictly-Prior 10-Term Pool (`2016 <= T < 2026`):** Pooling `disturbed` over `parsed` across the grant Terms in `[2016, 2025]` present in the statpack table (OT2017 through OT2025; OT2016 has 0 parsed rows and is omitted from the table):
  - **OT2025:** 19 disturbed / 26 parsed (`73.1%`, coverage `26/53 = 49.1%` granted, `9` excluded)
  - **OT2024:** 52 disturbed / 77 parsed (`67.5%`, coverage `77/79 = 97.5%` granted, `1` excluded)
  - **OT2023:** 35 disturbed / 56 parsed (`62.5%`, coverage `56/56 = 100.0%` granted, `0` excluded)
  - **OT2022:** 51 disturbed / 73 parsed (`69.9%`, coverage `73/73 = 100.0%` granted, `1` excluded)
  - **OT2021:** 43 disturbed / 62 parsed (`69.4%`, coverage `62/62 = 100.0%` granted, `3` excluded)
  - **OT2020:** 60 disturbed / 73 parsed (`82.2%`, coverage `73/80 = 91.3%` granted, `3` excluded)
  - **OT2019:** 46 disturbed / 58 parsed (`79.3%`, coverage `58/60 = 96.7%` granted, `2` excluded)
  - **OT2018:** 54 disturbed / 78 parsed (`69.2%`, coverage `78/81 = 96.3%` granted, `3` excluded)
  - **OT2017:** 35 disturbed / 57 parsed (`61.4%`, coverage `57/58 = 98.3%` granted, `6` excluded)
- **Pooled Baseline (`2016 <= T < 2026`):** `395 / 560 = 70.54%` (**`70.5%`**), well above the 30-parsed-judgment floor, with overall parse coverage across those nine grant Terms of `560 / 602 = 93.0%` (and `28` excluded rows removed by the pool guard). Note that the nearest grant Term in the pool, OT2025, has `26 / 53 = 49.1%` coverage because half of OT2025 grants are still pending decision; excluding OT2025 (i.e., pooling OT2017–OT2024, `2016 <= T < 2025`), the pooled disturbed rate is nearly identical at `376 / 534 = 70.41%` (**`70.4%`**) with `534 / 549 = 97.3%` coverage.
- **Breakdown by Judgment Class (`n=560`):** `252` reversed (`45.0%` of parsed, `63.8%` of disturbed), `131` vacated (`23.4%` of parsed, `33.2%` of disturbed), `12` affirmed in part (`2.1%`), `149` affirmed (`26.6%`), `12` DIG (`2.1%`), and `4` equally divided (`0.7%`).

### 2. Per-Justice Merits Votes (Complete Lineups)
Pooling the **"Per-Justice merits votes (complete lineups)"** tables in `metrics/statpack.md` across all six published Terms strictly before grant Term OT2026 (**OT2020–OT2025**, comprising `289` complete documents out of `345` total documents, and `280` with a plain judgment; for Justice Jackson, **OT2022–OT2025**, `198` complete documents out of `237`, `192` with a plain judgment):
- **Roberts:** With judgment `273 / 289` (`94.5%`); Disturb `193 / 280` (`68.9%`) (OT2025: `49/51 = 96.1%` with judgment, `32/50 = 64.0%` disturb).
- **Kavanaugh:** With judgment `274 / 289` (`94.8%`); Disturb `196 / 279` (`70.3%`) (OT2025: `47/51 = 92.2%` with judgment, `29/49 = 59.2%` disturb).
- **Barrett:** With judgment `257 / 283` (`90.8%`); Disturb `182 / 272` (`66.9%`) (OT2025: `46/51 = 90.2%` with judgment, `30/50 = 60.0%` disturb).
- **Alito:** With judgment `229 / 285` (`80.4%`); Disturb `164 / 273` (`60.1%`) (OT2025: `41/50 = 82.0%` with judgment, `25/49 = 51.0%` disturb).
- **Thomas:** With judgment `229 / 289` (`79.2%`); Disturb `166 / 279` (`59.5%`) (OT2025: `42/51 = 82.4%` with judgment, `26/50 = 52.0%` disturb).
- **Gorsuch:** With judgment `227 / 287` (`79.1%`); Disturb `183 / 274` (`66.8%`) (OT2025: `44/51 = 86.3%` with judgment, `30/50 = 60.0%` disturb).
- **Kagan:** With judgment `218 / 289` (`75.4%`); Disturb `180 / 274` (`65.7%`) (OT2025: `37/51 = 72.5%` with judgment, `26/49 = 53.1%` disturb).
- **Jackson (OT2022–OT2025):** With judgment `147 / 198` (`74.2%`); Disturb `120 / 189` (`63.5%`) (OT2025: `35/51 = 68.6%` with judgment, `24/49 = 49.0%` disturb).
- **Sotomayor:** With judgment `210 / 289` (`72.7%`); Disturb `176 / 273` (`64.5%`) (OT2025: `38/51 = 74.5%` with judgment, `25/49 = 51.0%` disturb).

## Adjustments from the Base Rate

Starting from the **70.5%** (`395/560`) pooled disturbed base rate, I adjust upward to **0.79** (`79%`) for the following case-specific reasons:

1. **Doctrinal strength under *Epic Systems* and *McMahon* (+11%):**
   - In *Epic Systems Corp. v. Lewis*, 584 U.S. 497, 510–16 (2018), the Court emphasized that it has rejected every modern attempt to invoke implied statutory conflicts to override the FAA's mandate in 9 U.S.C. § 2, demanding a "clear and manifest" congressional intention in the statutory text.
   - Here, the Fourth Circuit majority relied on five generalized policy factors—centralization, protecting the debtor's "breathing spell," appellate uniformity, specialized bankruptcy-judge expertise, and the public deterrent value of punitive damages under § 362(k). Almost every one of those rationales has been squarely rejected in prior Supreme Court FAA decisions (*McMahon* rejected complexity, judicial expertise, and RICO treble/punitive damages; *Mitsubishi Motors* and *Gilmer* rejected public-deterrence and statutory-purpose arguments; *Epic Systems* rejected purposive overrides of text).
   - Furthermore, the Fourth Circuit refused arbitration even as to respondent Gregory Maze, whose Chapter 7 bankruptcy was fully administered and closed before this adversary proceeding began, and whose recovery under § 362(k) would go strictly to him personally without touching any bankruptcy estate or creditor distribution. Even under the Second Circuit's functional estate-interference test in *MBNA America Bank, N.A. v. Hill*, 436 F.3d 104 (2d Cir. 2006), Maze's claim is clearly arbitrable. Because reversing or vacating as to either debtor or rejecting the Fourth Circuit's categorical reasoning disturbs the judgment below, the likelihood of disturbance is substantially above the 70.5% baseline.

2. **Countervailing risks keeping P(disturbed) at 0.79 rather than higher (-2.5%):**
   - **Substantive affirmance risk (~17.5%):** Every federal court of appeals to address arbitration in bankruptcy has recognized that *some* core bankruptcy proceedings inherently conflict with the Bankruptcy Code's centralized, in rem scheme. Respondents' best argument—developed effectively in their BIO—is that the automatic stay under § 362(a) is a statutory injunction equivalent to a court order, that Goldman itself concedes § 105(a) civil contempt proceedings to enforce the stay are non-arbitrable, and that Congress enacted § 362(k) as a supplemental statutory damages remedy for the very same stay violations. If a majority of the Court concludes that enforcing the automatic stay via § 362(k) is an exercise of in rem court-enforcement authority akin to contempt (especially where, as here, respondents pleaded both § 362(k) and § 105(a) and Ms. Brown's Chapter 13 case remains open), the Court could affirm.
   - **Residual DIG risk (~3.5%):** Respondents' September 14, 2026 supplemental brief informed the Court that on September 10, 2026, the bankruptcy court dismissed the original complaint without prejudice for failing to adequately plead actual damages (giving 21 days to amend), and stated that their forthcoming amended complaint would foreground § 105(a) as an independent basis for monetary relief. Because the Court had that supplemental briefing before it across four conferences before granting certiorari on November 6, 2026, the vehicle risk was already vetted and discounted at the grant stage; however, a small (~3.5%) chance remains that post-grant developments in the bankruptcy court or a clean-vehicle problem around the interaction of § 105(a) and § 362(k) in the amended complaint could prompt a DIG (which scores as undisturbed).

3. **Choice of `judgment: "reversed"` over `"vacated"`:**
   - Among disturbed judgments in the 10-Term pool (`395`), `252` (`63.8%`) are `reversed`, `131` (`33.2%`) are `vacated`, and `12` (`3.0%`) are `affirmed-in-part-reversed-in-part`.
   - Because the Fourth Circuit affirmed the denial of Goldman's motion to compel arbitration on a categorical rationale that failed even to send Mr. Maze's closed Chapter 7 § 362(k) claim to arbitration, the Court's judgment is most likely to reverse the Fourth Circuit ("reversed and remanded"), though a vacatur and remand ("vacated and remanded") to apply a narrower estate-interference standard to Ms. Brown's open Chapter 13 case is a plausible secondary disturbed outcome.

## Rationale for Vote Lineup and Authorship Distributions

- **Vote Lineup (`votes`):**
  - The six conservative Justices (`Roberts`, `Thomas`, `Alito`, `Gorsuch`, `Kavanaugh`, `Barrett`) have consistently enforced bilateral arbitration clauses under the FAA in federal-court proceedings absent express statutory text to the contrary. (Unlike state-court FAA cases where Justice Thomas dissents based on his view that the FAA does not apply in state courts, this case arises in federal bankruptcy court, where Justice Thomas regularly joins FAA enforcement majorities, e.g., *Epic Systems* and *CompuCredit*.)
  - Justice `Kagan` joins the judgment in `75.4%` (`218/289`) of complete lineups over OT2020–OT2025 and frequently joins textualist bankruptcy and statutory opinions where the text contains no exception, making her more likely than not (`0.72`) to join the majority, particularly if the opinion preserves bankruptcy courts' § 105(a) contempt authority and focuses on private § 362(k) damages claims.
  - Justices `Sotomayor` (`210/289 = 72.7%` with judgment) and `Jackson` (`147/198 = 74.2%` with judgment) have been the most skeptical of compelling arbitration of statutory protection claims involving consumers and debtors and are the likeliest to credit respondents' argument that § 362(k) stay enforcement should remain centralized in the bankruptcy court alongside § 105(a). I therefore place `Sotomayor` and `Jackson` in `dissent` with modest confidence (`0.54`), reflecting a close split between a 7–2/6–3 division and a near-unanimous 8–1/9–0 remand.
- **Authorship (`claim_distributions`):**
  - For `majority-author`, starting from a near-uniform bench baseline (~`0.11` per Justice), I assign slightly higher weight to Justices `Gorsuch` (`0.130`, author of *Epic Systems* and *Purdue Pharma*), `Barrett` (`0.130`, frequent writer in bankruptcy and civil procedure), `Kavanaugh` (`0.125`, author of *Coinbase v. Bielski*), `Thomas` (`0.120`), `Roberts` (`0.115`), and `Kagan` (`0.110`), and slightly lower weight to `Alito` (`0.100`), `Jackson` (`0.085`), and `Sotomayor` (`0.080`), with `0.005` on `per-curiam`.
  - For `separate-writers`, I assign the highest separate-writing probabilities to the likeliest dissenters (`Sotomayor` `0.30`, `Jackson` `0.28`) and the most frequent concurring writers on FAA/statutory theory (`Thomas` `0.24`, `Gorsuch` `0.20`), moderate probabilities to `Alito` (`0.16`), `Kagan` (`0.14`), `Barrett` (`0.12`), and `Kavanaugh` (`0.12`), and the lowest to `Roberts` (`0.06`), who sits in the majority `94.5%` of the time and rarely authors separate concurrences.

## Main Uncertainties
1. **How the Court handles Brown's open Chapter 13 posture vs. Maze's closed Chapter 7 posture:** While Maze's closed Chapter 7 case is a textbook candidate for arbitration under *Hill*, Brown's Chapter 13 case remains open until her payment plan concludes. Whether the Court announces a bright-line rule that *all* private § 362(k) damages claims are arbitrable (`reversed`) or announces an estate-interference standard that reverses as to the Fourth Circuit's categorical rule while remanding for closer examination of Brown's Chapter 13 plan (`reversed` or `vacated`) is the main doctrinal uncertainty.
2. **No merits briefing yet (`moment: grant`):** At the grant moment, neither the parties' merits briefs nor any amicus brief from the United States (which often participates at the merits stage in bankruptcy cases via the Solicitor General and the U.S. Trustee Program) has been filed.
