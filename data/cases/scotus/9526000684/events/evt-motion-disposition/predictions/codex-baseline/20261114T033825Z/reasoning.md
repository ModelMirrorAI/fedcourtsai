# Rationale

## Target and information set

I predict denial of application 26A684, with **P(relief granted in whole or in part | not dismissed or denied as moot) = 0.02**. This is an interim application, not a certiorari petition. The number is not discounted for possible mootness and includes partial substantive relief. A temporary administrative hold would not, by itself, establish that the ultimate requested stay was granted.

The baseline is the case-level `record/snapshots/2026-11-11.json`, read with `record/context.json` and `events/evt-motion-disposition/event.yaml`. Its sole entry is the November 10, 2026 application submitted to the Chief Justice. The arrival-position boundary is entry zero. The frozen record shows no requested response, no referral to the full Court, and zero amicus entries. Submission to the Chief Justice is not referral to the Court. The mode is forward; I nevertheless did not retrieve the live docket, the application's outcome, or another forecast. The null salience band is appropriate to this stage and was not replaced with a cert baseline.

The substantive input is `record/documents/application.txt`, particularly printed pages 1–2, 12–16, 19–29, and 39–40. `documents.json` identifies a 63-page, OCR-derived, nontruncated application. The document supplies the applicant's argument and an appendix table of contents, but not the underlying appendix orders themselves; its closing notice says additional material is available in the Clerk's Office. I therefore treat descriptions of lower-court findings as the applicant's account, not independently verified findings. The snapshot/event spell the respondent BOFK; the application spells it BOKF. I treat these as the same respondent, without drawing substantive conclusions from the transposition.

## Stage-specific anchor

I read `metrics/statpack.md`, section "The interim docket (applications)," and computed the applicable pool from the `interim.terms` records in `metrics/statpack.json`. For application Term 2026, the contract uses Terms 2016–2025 inclusive and the finer-reading counts, not the older substantive counts:

| Term | finer granted | finer resolved |
| --- | ---: | ---: |
| 2016 | 9 | 107 |
| 2017 | 13 | 124 |
| 2018 | 14 | 113 |
| 2019 | 13 | 119 |
| 2020 | 27 | 133 |
| 2021 | 17 | 107 |
| 2022 | 9 | 103 |
| 2023 | 17 | 124 |
| 2024 | 18 | 189 |
| 2025 | 19 | 218 |

The scored anchor is **156/1,337 = 11.6679%**. Every pooled Term has `finer_unread = 0`; the pool clears the floor of 50. The markdown table's legacy grant/resolution columns differ from these finer counts, so I use the JSON finer fields. Parse coverage remains imperfect: 2016 has 15 unparsed applications and 2017 has one. The OT2026 row is excluded. Terminal escalation counts are descriptive, right-censored population summaries, not calibrated hazards from this arrival state.

Paul Schultz is a private applicant and the case is not marked capital. The descriptive private/unmarked cut is **63/906 = 6.9536%**, comfortably above the 30-case reporting floor. I lean on that exact cut rather than the broader private margin, 73/1,194, or the unmarked margin, 126/1,021. This moves my starting assessment from roughly 11.7% to roughly 7%; it does not replace the whole-pool scoring yardstick. The remaining downward adjustment, to 2%, reflects the application-specific weaknesses below, not a measured conditional grant rate.

## Why below the private-applicant rate

The requested relief has two components: prevent a district judge from entering a bankruptcy-appeal merits judgment while a prospective recusal challenge remains pending, and prevent a December 17, 2026 foreclosure authorized by bankruptcy stay-relief order Dkt. 625. The application alternatively requests an injunction against consummation of the sale if a stay cannot reach it. Its proposed duration is through action on a pending Fourth Circuit preservation motion or rehearing petition. These are the applicant's stated requests, not evidence that any requested relief was awarded. (Application, printed pp. 12–16, 27–29, 39–40.)

The strongest favorable fact is the concrete threatened loss of an occupied residence. The applicant reports a dated foreclosure notice, a $950,000 appraisal, and a lower-court acknowledgment that foreclosure favors him on irreparable harm. He also describes attempts to obtain relief below, including bankruptcy- and district-court denials, so this is not simply an application that ignored the lower courts. I assign meaningful, but limited, weight to these assertions because the cited source orders and valuation exhibits are not reproduced in the available text. (Application, printed pp. 19, 27–32.)

That harm does not by itself answer the probability-of-review and merits requirements. A stay pending Supreme Court review generally requires a reasonable probability that four Justices would grant review, a fair prospect of reversal by a majority, and likely irreparable harm; Nken likewise emphasizes likely success and irreparable injury. *Hollingsworth v. Perry*, 558 U.S. 183, 190 (2010); *Nken v. Holder*, 556 U.S. 418, 434 (2009). The application itself states these standards on printed pp. 20–21. I do not equate the availability of All Writs authority with satisfaction of the standards for using it.

My main negative adjustment is vehicle quality. The requested intervention lies within a multilayered bankruptcy, recusal, mandamus, and rehearing dispute. The application reports that the Fourth Circuit denied mandamus on October 22, 2026, and that rehearing and preservation requests remain pending. It does not establish a developed inter-circuit conflict or a cleanly presented question demanding immediate Supreme Court intervention. Recasting numerous adverse procedural rulings as a process-wide constitutional defect still requires the Court to accept contested, record-specific premises. This is my assessment of the submitted argument, not an inference that the applicant's allegations are false. (Application, printed pp. 1–11, 13, 21–25.)

The proposed recusal theory also faces a substantial legal obstacle: adverse judicial rulings almost never independently establish disqualifying bias, although extreme circumstances can matter. *Liteky v. United States*, 510 U.S. 540, 555–56 (1994). The applicant expressly argues that his cumulative appearance-of-impartiality theory is different and that the judge improperly substituted a bias inquiry. I considered that distinction, but an unopposed recusal motion does not in my assessment establish entitlement to recusal or emergency Supreme Court protection. The required connection between the alleged procedural pattern, mandatory disqualification, and a clear prospect of Supreme Court reversal remains weak on the available material. (Application, printed pp. 1–2, 21–25.)

Finally, the sale is scheduled more than a month after the November 10 submission. That leaves some opportunity for the pending lower-court processes to operate, unlike an execution or removal scheduled within hours. The application does assert a separate risk of an intervening district-court merits ruling, but does not identify a fixed imminent date for that judgment in the material I read. These considerations reduce the case for an immediate extraordinary intervention without eliminating the practical foreclosure risk. (Application, printed pp. 19–20, 27–29.)

Balancing those factors, **2%** preserves a real possibility of narrowly tailored relief, especially if the lower-court record strongly confirms the applicant's account, while recognizing that irreparable property harm alone is not enough. My principal uncertainty is the unavailable primary appendix record and the possibility that a short preservation order would be attractive despite the weak broader vehicle. This is not a judgment on the ultimate validity of any loan, lien, or bankruptcy claim.

## Procedural claims and limitations

From the frozen state of no response request, no referral, and no amici, I assign 8% to a later response request, 18% to referral, and 1% to any increase in the amicus-entry count. Referral can occur without a response and does not imply relief. The amicus forecast includes submitted briefs, not only accepted briefs. The independent order-writer probabilities are all very low because a short unexplained disposition is my central forecast; no per-Justice vote prediction is made.

The required corpus query returned three unrelated cert denials, not comparable emergency applications; I did not treat their outcomes as an interim base rate. A separate Nken reporter-citation query returned no rows and warned of sparse citation coverage; this is not evidence that Nken is absent as precedent. General legal-source retrieval concerned only stay and recusal law, not this application's history. No CourtListener lookup was needed, and no outcome or outside forecast of this application was encountered. The appendix limitation is disclosed in `flags.json`; tooling limitations appear in `tooling.json` and `retrieval.md`.
