# Rationale

## Call and information set

I assign a 6% probability of a grant in whole or in part, conditional on a nonmoot disposition, and predict denial. This is the interim arrival event for Paul Schultz v. H. Jason Gold, application 26A658, not a prediction about certiorari.

I read the event definition, the case-level `record/snapshots/2026-11-03.json`, `record/documents/documents.json`, `record/documents/application.txt`, and `record/context.json`. The event opened on November 2, 2026. The snapshot contains just the November 2 submission of an application for a stay to the Chief Justice. The context describes an arrival-position cut, anchor index 0, cutoff November 3, and forward mode. It freezes no response request, no referral, and zero amicus entries. No later state of this application was retrieved. I do not know its disposition.

The snapshot identifies the lower tribunal as the United States Bankruptcy Appellate Panel for the Tenth Circuit, proceeding 26-2404. I treat that as provisioned metadata, not independent verification of the appellate route or jurisdiction. The docket marks the case noncapital. Paul Schultz is a private applicant under the caption rule and under my own classification.

## Document limitation

The application was fetched, but `documents.json` explicitly reports `empty_text: true`, 57 pages, no truncation, and no OCR-derived text. The staged text contains no usable application content. This is a content-unavailable filing, not an absent filing. Consequently I cannot identify the particular order to be stayed, the requested duration, the legal question, the alleged injury, the relief sought below, or any appendix reasoning. I do not infer that the applicant omitted these showings. No opposition or reply is staged. The forecast is predominantly a docket-and-priors forecast, not a merits assessment of the application. A capture-gap flag records the text limitation.

## Published anchor and adjustment

I consulted the interim section and applicant-class table in `metrics/statpack.md`, then computed the controlling pool from `metrics/statpack.json`. For an OT2026 application the applicable window is OT2016–OT2025 and the controlling counts are `finer_granted` and `finer_resolved`, not the older substantive reading or the OT2027 widened reading.

| Application Term | Finer grants | Finer resolved | Unparsed applications |
| --- | ---: | ---: | ---: |
| 2025 | 19 | 218 | 0 |
| 2024 | 18 | 189 | 0 |
| 2023 | 17 | 124 | 0 |
| 2022 | 9 | 103 | 0 |
| 2021 | 17 | 107 | 0 |
| 2020 | 27 | 133 | 0 |
| 2019 | 13 | 119 | 0 |
| 2018 | 14 | 113 | 0 |
| 2017 | 13 | 124 | 1 |
| 2016 | 9 | 107 | 15 |
| Total | 156 | 1,337 | 16 |

Every pooled Term has `finer_unread = 0`; the pool clears the 50-resolution floor. The scored anchor is therefore 156/1,337 = 11.668%. It excludes this application's own Term and counts partial relief as granted and moot outcomes outside the denominator. Coverage remains uneven: 16 applications in those Terms were never parsed. The Markdown section's main grant-rate table describes the older reading; I did not substitute those numbers for the finer counts.

The directly relevant applicant cell, private/unmarked, is 63/906 = 6.954%, comfortably above its 30-resolution descriptive floor. This is more informative about this applicant than the private all-cases margin, 73/1,194 = 6.114%, which mixes capital and noncapital matters. I lean primarily on the private/unmarked cell: it reduces the whole-pool anchor by about 4.7 percentage points. I make only a further modest adjustment to 6%, reflecting that this record supplies no affirmative basis for an unusually grant-worthy emergency. That is uncertainty under an unavailable filing, not a finding that the filing lacks merit. A roughly 7% estimate would also be reasonable; the final one-point adjustment is judgment, not a fitted effect.

The absence of a response request or referral at arrival is not evidence of a considered judicial rejection. Those signals can arise later. I have not treated terminal escalation counts as arrival-conditioned grant rates. The published cohort also differs from the predictor-selected population, which favors escalated cases. No cert salience band or caption-floor cert rate enters this forecast.

## Legal and procedural context

For a stay pending certiorari, the Court's historical formulation requires a reasonable probability of certiorari, a fair prospect of reversal, and likely irreparable harm; relative harms and equities matter in close cases. See *Hollingsworth v. Perry*, 558 U.S. 183, 190 (2010), verified through CourtListener's historical opinion text, opinion 9413203. This is conditional legal context because the unavailable application prevents confirmation of the precise procedural route. I cannot test any of these requirements against the actual arguments and do not assume a particular bankruptcy issue or merely monetary injury.

The structured corpus query returned five denied cert petitions, not comparable stay applications. I used that result only to assess retrieval relevance; it supplies no interim rate and causes no additional downward adjustment. The two web attempts returned no usable content. CourtListener did supply the historical stay standard. No search sought this application's disposition, later history, or current docket.

## Other forecast quantities

From the frozen state of no request, no referral, and zero amicus entries, I assign 10% to a future response request, 25% to a future full-Court referral, and 1.5% to any additional counted amicus entry or distinct submitted amicus brief. These are subjective arrival-stage hazards; the pack does not publish the corresponding conditioned baselines. Referral without a grant is entirely possible. I expect no separate writing; each Justice's independent authorship probability is very small. The small differences are weak generic judgments, not an inference about ideological alignment on an unknown issue.

I leave the significance score explicitly null: the unavailable application prevents a defensible assessment of substantive reach or newsworthiness. An apparently private caption alone does not justify assigning low stakes. No mootness discount is embedded in the 6% grant probability.
