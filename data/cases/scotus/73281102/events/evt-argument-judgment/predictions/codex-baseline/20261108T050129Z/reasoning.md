# Forecast rationale

## Call and information set

P(the judgment below is disturbed) is **0.86**. The modal judgment is **vacated**, with a **7–2** division: Roberts, Sotomayor, Kagan, Gorsuch, Kavanaugh, Barrett, and Jackson against Thomas and Alito. This is a prediction about the procedural vehicle, not a prediction that Maxwell has proved entitlement to immediate transfer or correctly calculated his credits.

I read the case-level `record/context.json`, `record/snapshots/2026-11-03.json`, the document manifest, the questions presented, the decision below and lower-court docket, substantive portions of both merits briefs and both replies, and the November 2 argument transcript, checked against `record/argument-features.json`. Context identifies a forward, argued merits cell with a November 3, 2026 date cutoff. The baseline includes the November 2 argument and nothing indicating a Supreme Court judgment. I do not know this case's outcome and retrieved neither its current docket nor its disposition.

The June 1, 2026 grant is expressly limited to whether an earned First Step Act time-credit claim seeking earlier halfway-house or home confinement can proceed under 28 U.S.C. §2241. That is the question I forecast, not the pro se petition's additional exhaustion question. The grant falls in **October Term 2025**, notwithstanding the argument's placement in the next Term. The cert salience band, distributions, and grant probability supply no merits prior.

## Eligible historical anchor

The merits section of `metrics/statpack.md` publishes an excluded count and is therefore quotable. Applying its ten-grant-Term window, 2015 through 2024, yields available rows for 2017–2024: **376 disturbed judgments / 534 parsed judgments = 70.4%**. Coverage is **534 parsed / 549 granted = 97.3%**; another **19 excluded** cert-order dispositions are outside that granted cohort, not an additional subset of it. No 2015 or 2016 row is supplied. I did not use the 2025 row, any later Term, or the all-Term aggregate. These counts were pooled directly from `metrics/statpack.json`.

The 15 unparsed grants mix pendency and parse gaps, and the nearest eligible Term can favor quicker dispositions. This is a selected parsed cohort, not an exact unconditional reversal frequency for all argued cases. It supports a disturb-leaning starting point; the agreement between the parties on cognizability and the actual questioning then moves the forecast upward. Procedural risks prevent a move toward certainty.

For the vote reference, the eligible complete-lineup section supplies decision Terms 2020–2024: **238 complete lineups / 275 opinion documents**. Its pooled counts for sitting Justices are:

| Justice | With judgment / sat | Disturb / eligible whole-side votes |
| --- | ---: | ---: |
| Roberts | 224 / 238 | 161 / 230 |
| Thomas | 187 / 238 | 140 / 229 |
| Alito | 188 / 235 | 139 / 224 |
| Sotomayor | 172 / 238 | 151 / 224 |
| Kagan | 181 / 238 | 154 / 225 |
| Gorsuch | 183 / 236 | 153 / 224 |
| Kavanaugh | 227 / 238 | 167 / 230 |
| Barrett | 211 / 232 | 152 / 222 |
| Jackson | 112 / 147 | 96 / 140 |

The second column is not a case-specific vote forecast. The third excludes mixed judgments, DIGs, and equally divided decisions, while unseatable lineups and per curiams are absent from these complete-lineup samples. I do not equate these fractions with the merits anchor or simply assign the ideological blocs their historical average votes.

## Why disturb is substantially likelier

The provisioned April 3, 2025 Fifth Circuit decision is the correct case, number 23-40699, matching the Supreme Court snapshot and petition. It affirmed dismissal because neither halfway-house nor home-confinement relief would constitute accelerated release under its reading of Melot. It expressly bypassed exhaustion. Its footnote characterizes the claim as arising under the elderly-offender program; the Supreme Court's limited grant and counseled merits submissions instead frame the issue as earned-time-credit cognizability. I forecast that framed legal issue without assuming the Court has established all underlying eligibility facts.

Maxwell's merits brief, especially the summary at printed pages 11–15 and the custody discussion at pages 34–37, argues from §2241's custody language, historical habeas remedies short of unconditional freedom, and the analogy to parole. His reply at pages 9–12 explains why continued agency custody does not settle the immediate custodian's authority. The government's merits brief at pages 14–16 and 40–42 agrees the claim is cognizable but requests vacatur, preserving alternative defenses. Its reply at pages 18–21 maintains both the judicial-review-bar argument and a possible DIG. **The respondent is supporting vacatur, not defending the Fifth Circuit's habeas rule.** There is no separately provisioned United States amicus brief; the United States participates through the respondent's briefs.

The strongest point is the narrow shared position: prison-to-community release can qualify for habeas although the prisoner remains legally restrained. The record supplies an adversary through Barnes, the Court-appointed amicus, but his brief itself was not provisioned. I assess his defense from his argument and the parties' descriptions, not from an imagined reading of that filing. At argument he relied on continuing BOP control, escape liability, and similarities between prison camps and halfway houses. Kagan and Kavanaugh pressed why the identity of the supervising executive agency should change the remedy; Sotomayor and Jackson stressed the statutory entitlement rather than comparisons between buildings. Those exchanges weaken the defense of affirmance.

As a limited external check, I consulted the historical **Preiser v. Rodriguez, 411 U.S. 475, 478–481 (1973)** opinion through CourtListener. The factual account confirms that restoration of the credits at issue led to release on parole, not necessarily freedom from every legal restraint. That supports the analogy advanced in the staged filings, but extending it to First Step Act prerelease custody remains my inference, not something Preiser itself decided. No additional case-specific evidence came from external retrieval.

## What argument adds, and what it cannot establish

The transcript's printed pages 3–18 show a relatively untroubled presentation for Maxwell apart from threshold questions and requests to narrow his general level-of-custody test. The most discriminating exchanges are later: Kavanaugh asks why §3621(b) cannot await remand; Barrett explicitly outlines deciding the granted question while reserving the review bar; Jackson repeatedly challenges the government's belated DIG request. Sotomayor resists treating the review bar as nullifying the statutory command, while Kagan tests the parole distinction. These are substantive, not merely numerical, reasons to expect a merits majority.

The deterministic features report **21 Justice turns / 652 words** during petitioner's opening and rebuttal, **61 / 1,511** during the government's argument, and **34 / 1,085** during Barnes's argument. Coverage is **4/4 segments attributed, 116/117 Justice turns inside attributed segments, one outside, zero unresolved Justice labels, zero unattributed segments, and zero unrecognized labels**. The counts are not vote estimates. In particular, the parser labels the respondent's alignment as `neither` even though that advocate supports vacatur, and labels Barnes `amicus-supporting-respondent` even though he defends a judgment the respondent attacks. I use the actual positions expressed, not those nominal alignment buckets.

Thomas's distinction between prerelease custody and parole, and Alito's sustained argument for waiting or dismissing, make them my dissenters. Gorsuch's medium-to-minimum-security hypothetical creates a real third-dissenter risk, but also appears answerable by reserving ordinary prison-transfer cases. Roberts says too little substantively to justify strong individual confidence. A question is not a vote: the two largest lineup uncertainties are whether Gorsuch joins and whether Thomas accepts a very narrow disposition. Unanimity and a 6–3 decision remain credible alternatives to 7–2.

## Judgment class and remaining risk

My working allocation across the six judgment classes is: **vacated 0.50; reversed 0.35; mixed 0.01; DIG 0.11; affirmed 0.03; equally divided 0.00**. Thus the three disturbed classes sum exactly to 0.86. Zero for an equally divided outcome reflects no disclosed nonparticipation and no affirmative reason to predict one, not a claim that an unexpected recusal is impossible.

Vacatur narrowly leads reversal because the district court relied on exhaustion and the parties dispute additional barriers the Court need not resolve. The government's requested vacatur and remand supplies a natural way to remove the appellate threshold ruling without deciding whether the district court's ultimate dismissal can stand. However, Maxwell requests reversal, and a categorical legal error often produces reversal with a remand despite unresolved defenses. This label distinction is materially less certain than disturbance itself. Some vacatur probability also covers a later mootness-based disposition, not agreement with the forecast doctrinal opinion.

The projected **January 22, 2027** transfer is future relative to both the argument and this run, not an accomplished release. It gives the Court a reason to act promptly but creates genuine risk of a procedural exit. The government's §3621(b) theory and Alito's concerns keep DIG at 11%, despite five Justices' questions favoring proceeding. I do not assume the proposed supervised-release collateral consequence will ultimately defeat mootness. Nor do I infer that exhaustion is satisfied or that all four §3624(g) prerequisites have been adjudicated merely because counsel asserts them. All can remain for remand.

## Authorship, separate writing, and stakes

The prior-Term authorship pack supplies 247 decisions and 238 observed lineups for 2020–2024. Barrett has 28 majority writings and 23 separate writings over 232 sittings; Kavanaugh has 28 and 32 over 238. Alito's separate-writing reference is 40/235 and Thomas's is 64/238. These are historical references, not the harness's shrunk baselines and not assignment information for the November sitting.

I modestly favor **Barrett (20%)** and **Kavanaugh (18%)** to deliver a narrow procedural opinion because their exchanges supply the practical route through the case. The distribution remains diffuse: no current-sitting assignment evidence was consulted. The point forecast is an **Alito dissent joined by Thomas**; independent probabilities of writing separately are 55% and 45%, respectively, allowing either to author instead. Gorsuch's 24% separate-writing probability reflects a possible limiting concurrence or dissent over line-drawing. I forecast no other separate opinion in the modal scenario; joining a dissent is not writing one.

The stakes score of 0.48 reflects a recurring and consequential remedy question for prisoners, with broader habeas/civil-rights implications, discounted because the likely holding concerns a narrow category of community placement and leaves actual credit entitlement and agency defenses unresolved.
