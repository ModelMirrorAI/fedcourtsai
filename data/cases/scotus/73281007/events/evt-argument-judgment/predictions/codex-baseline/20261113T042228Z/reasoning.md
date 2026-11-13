# Rationale

## Call and information set

I predict **affirmed, 5–4**, with **P(the judgment below is disturbed) = 0.32**. This is not a probability of granting certiorari: review was granted on April 27, 2026. An affirmance here favors Sun Valley, not the Department of Labor. My point lineup is Roberts, Thomas, Gorsuch, Kavanaugh, and Barrett to affirm; Alito, Sotomayor, Kagan, and Jackson to dissent.

This is the forward-mode, argued merits cell. I used the provisioned case-level `record/snapshots/2026-11-11.json`, `context.json`, the event definition, `documents/documents.json`, `questions-presented.txt`, `decision-below.txt`, `lower-court-docket.txt`, the substantive summaries and relevant argument sections of `merits-brief-petitioner.txt`, `merits-brief-respondent.txt`, and `merits-reply-petitioner.txt`, and the argument transcript and argument-features file. The briefs and transcript are nonempty, nontruncated, and not marked OCR-derived. The petition is marked truncated, but this forecast does not depend on its omitted appendix. No separate United States merits amicus is listed: the government is itself the petitioner, represented by the Principal Deputy Solicitor General. I follow its statutory reading more than its constitutional position. I did not independently analyze the cert-stage opposition or reply; merits briefing and argument supply the competing positions used here.

The snapshot ends after the November 10, 2026 argument. Although forward retrieval could go beyond that baseline, I retrieved no additional material about this case. I have no known disposition of this case and encountered no other forecast. External retrieval concerned Jarkesy only; web attempts supplied no visible results, and the useful precedent verification came from CourtListener MCP.

## Baseline and adjustment

The April 27 grant falls in **OT2025**. I pooled the committed merits table over the prescribed ten-grant-Term window, **2015–2024**, rather than using the pack-level rate or the cert salience band. The pack supplies rows for 2017–2024 within that window: **376 disturbed judgments / 534 parsed judgments = 70.41%**, with **534 parsed / 549 granted** coverage, and **19 separately excluded cert-order dispositions**, which are outside the 549. The pool clears the 30-judgment floor and each included row publishes an exclusion count. Missing 2015–2016 rows are not additional observed zero-disposition samples. Selection on parseability remains a caveat, and recent grant cohorts can overrepresent quick dispositions because pending cases are not yet parsed. OT2025's own partial cohort is excluded entirely.

The 70.41% figure is a strong initial reversal/vacatur prior, not a conclusion about this issue. I move substantially below it because the government must preserve a binding executive monetary judgment against a Court that has recently insisted on a historically bounded public-rights exception, and the argument supplies identifiable resistance from a plausible five-Justice coalition. The favorable general grant-stage selection has already occurred; the actual question and bench exchanges now carry more information than that unconditional prior. I do not use the frozen `federal` cert band, distribution count, or pre-grant signals as merits evidence.

My rough judgment allocation is affirmance 0.65, reversal 0.22, vacatur 0.08, mixed affirmance/reversal 0.02, DIG 0.025, and equally divided affirmance 0.005. Thus the disturbed outcomes total 0.32 and the undisturbed outcomes total 0.68. The tiny equally divided allowance represents an unforeseen nonparticipation, not a recusal shown in this record.

## Competing merits arguments

The provisioned Third Circuit opinion is the correct decision below: No. 23-2608, July 29, 2025, matching the Supreme Court docket and the petition's description. It treats DOL's employment-obligation claims as contract-like private-rights adjudication and reverses the district court with instructions to enter judgment for Sun Valley. It does not decide the alternative statutory, Article II, or Eighth Amendment grounds. The lower-court docket extract corroborates identity but lacks a recorded panel and does not independently establish the rehearing disposition. I rely on the opinion, not those missing docket fields, for its holding.

The grant order adds a second, statutory question to the original constitutional question. The government's opening merits brief, summary at printed pages 16–19 and statutory argument, makes a substantial textual case: Section 1188(g)(2) permits the Secretary to impose appropriate penalties but to seek injunctive relief, naturally distinguishing agency action from relief sought in court. Its reply, printed pages 3–6, explains why Congress's omission of detailed hearing procedures does not necessarily omit adjudicatory authority. This is the strongest reason not to predict a statutory-only resolution too confidently.

On the constitutional issue, the government argues that H-2A enforcement combines two public-rights traditions: sovereign control of immigration and enforcement of conditions attached to government-granted privileges. The regulated terms originate in federal law, and collecting a monetary remedy need not convert a genuine public right into a private one. These are serious answers, not merely an appeal to administrative convenience. The respondent's merits brief, printed pages 14–17 and its public-rights argument, instead emphasizes the adjudication of job-order obligations, back wages and penalties, including obligations toward domestic workers. Its statutory section, printed pages 45–52, alternatively argues that authority to impose a penalty does not necessarily authorize binding in-house adjudication.

The relevant distinction in **SEC v. Jarkesy, 603 U.S. 109, 127–132 (2024)** is between presumptively private common-law-type claims and historically established public-rights categories. Jarkesy expressly preserves immigration-related administrative penalties; it does not hold that every civil penalty requires an Article III court. CourtListener MCP verified the case and supplied the pertinent discussion through opinion **11066634**, particularly the immigration and public-rights passages. The forecast therefore turns on the *scope* of that exception, not on denying its existence. The employment dispute here can be separated from deciding who may enter or remain, while Oceanic Steam remains applicable to its historically grounded immigration setting.

## What argument changes

The transcript makes the likely division more specific than a generic six-conservative-versus-three-liberal forecast:

- **Roberts:** His opening exchanges with Harris repeatedly distinguish conditions of entry from later workplace regulation and question whether immigration authority is being leveraged beyond its justification. His later concern for individual rights reinforces an affirmance lean.
- **Gorsuch:** His imported-goods and domestic-wage hypotheticals press the absence of a limiting principle. Near the end he reconstructs a narrow route for Sun Valley: contract-like employment adjudication, including American workers, whose outcome admits or deports nobody. This is the clearest pro-affirmance signal.
- **Thomas:** His two short lines of inquiry distinguish decertification from monetary enforcement. They are consistent with requiring a court for the latter, but his sparse questioning makes this inference less secure than Roberts's or Gorsuch's.
- **Kavanaugh:** He emphasizes Tull and Jarkesy's treatment of punitive penalties, then minimizes the operational novelty of meaningful judicial adjudication because judicial review already exists. His demand for an administrable rule nevertheless gives the government a real opening.
- **Barrett:** She tests whether Oceanic Steam permits a freestanding monetary judgment or only an exaction linked to clearance, and resists combining distinct public-rights traditions indiscriminately. Her late suggestion that the parties' narrower positions resemble each other is an important counter-signal. I still marginally place her with a bounded affirmance, not a categorical ban on administrative penalties.
- **Alito:** He challenges the government's willingness to concede the common-law analogy and challenges Sun Valley's historical stopping point as insufficiently principled. These are reasons to predict a government vote despite his Jarkesy alignment. This is the least conventional feature of my lineup and a significant source of vote uncertainty.
- **Sotomayor, Kagan, Jackson:** Their questions defend the program as immigration enforcement, expose the weakness of a border-only rule, and challenge the respondent's remedy-based test. They are strong government leans. Kagan's extended defense of the statutory scheme is particularly clear.

Questions are evidence about concerns, not promises of votes. Barrett and Kavanaugh could find the respondent's exceptions unadministrable and join Alito and the three liberals, producing reversal. Conversely, Alito could accept a sufficiently narrow employment-rights rationale and make affirmance 6–3. I reserve meaningful probability for both rather than treating speaking time as a roll call.

As a check, `argument-features.json` reports **102 Justice turns / 3,257 words** to petitioners and **108 / 3,939** to respondent. Coverage is **210 of 211 Justice turns attributed to a side**, with one outside the three segments; all three segments are attributed, there are no unresolved Justice labels, and zero unrecognized label lines. Gorsuch's **33 turns / 772 words** to petitioners versus **8 / 111** to respondent fit the directional reading above. Barrett's **11 / 821** versus **12 / 460** shows why raw turn counts miss substantive asymmetry. These figures include petitioners' rebuttal where applicable and are corroboration of where exchanges occurred, never a mechanical vote predictor.

## Vote and writing reference points

Only OT2020–2024 are available before the grant Term in the per-Justice table. Pooled counts are:

| Justice | Sat | With judgment | Disturb / eligible |
| --- | ---: | ---: | ---: |
| Roberts | 269 | 253 | 181 / 257 |
| Thomas | 269 | 212 | 159 / 257 |
| Alito | 266 | 211 | 158 / 251 |
| Sotomayor | 269 | 196 | 167 / 250 |
| Kagan | 269 | 206 | 169 / 252 |
| Gorsuch | 267 | 211 | 173 / 252 |
| Kavanaugh | 269 | 254 | 185 / 257 |
| Barrett | 257 | 232 | 165 / 245 |
| Jackson | 162 | 121 | 101 / 152 |

These are selected complete signed lineups, not all dispositions. Their disturb axis excludes mixed judgments and procedural exits and cannot be substituted for the merits baseline. The high with-judgment frequency of Roberts and Kavanaugh is weak background support for placing them in the controlling coalition, not an issue-specific probability. The transcript and doctrinal positions drive the individual calls.

For authorship, the same strictly prior Terms show Roberts with **32 majority opinions and 9 separate writings in 269 sittings**, Gorsuch **32 and 62 in 267**, Barrett **29 and 31 in 257**, Kagan **31 and 22 in 269**, and Alito **28 and 49 in 266**. I tilt the lead-author distribution toward Roberts, given his Jarkesy authorship and the institutional Article III question, with substantial Barrett and Gorsuch alternatives. I have no current sitting-assignment evidence and do not infer an unfilled assignment. Alito's case-specific disagreement with the respondent and Kagan's sustained defense of the scheme raise their separate-writing chances above their general history. The distributions are unconditional, not certainties conditional on my exact 5–4 scenario.

The stakes score of **0.79** reflects an important separation-of-powers boundary and potentially consequential spillovers, while recognizing that a disciplined decision could leave most public-rights adjudications intact. No provisioning gap prevents completion; the web-tool limitations and corrected uv cache path are tooling limitations, not missing case evidence.
