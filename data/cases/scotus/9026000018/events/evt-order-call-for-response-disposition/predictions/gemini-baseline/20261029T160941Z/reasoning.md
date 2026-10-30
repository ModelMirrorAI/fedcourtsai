# Predictor Rationale — *Westcott v. Voice of the Experienced* (No. 26-18)

## Summary of Call

- **Event**: `evt-order-call-for-response-disposition` (`stage: cert`, `moment: response-requested`)
- **`probability` / `disposition`**: `0.28` (`granted: 0`, `predicted_disposition: "denied"`)
- **`relist-increment`**: `0.78`
- **`cvsg-increment`**: `0.01`
- **`summary-disposition-route`**: `0.45`
- **`dissent-from-denial`**: `0.18`
- **`big_case_score`**: `0.35`

## Inputs Read and Tooling Status

- **Provisioned snapshot**: Read `data/cases/scotus/9026000018/record/snapshots/2026-08-04.json` (`input_snapshot: "2026-08-04.json"`) and `data/cases/scotus/9026000018/record/context.json` (`mode: "forward"`, `term: 2026`, `band: "state"`, `salience_version: "sal-v4"`, `distribution_count: 1`, `cutoff: "2026-08-04"`).
- **Provisioned documents**: Read `data/cases/scotus/9026000018/record/documents/documents.json`, `questions-presented.txt`, and `petition.txt` (including the Petition for a Writ of Certiorari and the reproduced Fifth Circuit panel opinions in *VOTE II* and *VOTE III*, the Fifth Circuit en banc denial order with Judge Jones's six-judge dissent and Judge Wilson's separate statement at 168 F.4th 339, and the district court's preliminary injunction orders; `petition.txt` notes a routine 150,000-character cap truncation at the end of the district court appendix, which did not affect any appellate opinion or the petition body). No Brief in Opposition is on the record yet because the event is pinned to the August 3, 2026 Call for Response (response due September 2, 2026).
- **Corpus and MCP status**: Queried the local corpus (`uv run fedcourts query`) for 2020s granted and GVR SCOTUS priors. An attempted CourtListener MCP lookup for *Smith v. Edwards*, 88 F.4th 1119 (5th Cir. 2023), returned an HTTP 429 daily rate-limit error (`Rate limit exceeded: 1400/day`); per the prompt contract, I fell back to the corpus tooling and the extensive discussion and quotations of *Smith v. Edwards* in the provisioned petition and Fifth Circuit opinions.

## Base-Rate Anchor

In `metrics/statpack.md`, under **Segment base rate by salience band (`sal-v4`)**, because `context.json` carries a frozen salience band at prediction (`band: "state"`), the scored baseline is the bracketed risk-set (`reached`) grant-family rate for `state` pooled across the Terms strictly preceding OT2026 (OT2017–OT2025):

- **OT2025**: 32.3% (`n=31`, ~10 grants) | terminal: 15.8% (`n=19`, ~3 grants)
- **OT2024**: 31.6% (`n=38`, ~12 grants) | terminal: 23.1% (`n=26`, ~6 grants)
- **OT2023**: 18.8% (`n=32`, ~6 grants) | terminal: 8.3% (`n=24`, ~2 grants)
- **OT2022**: 13.9% (`n=36`, ~5 grants) | terminal: 7.7% (`n=26`, ~2 grants)
- **OT2021**: 22.7% (`n=97`, ~22 grants) | terminal: 28.3% (`n=53`, ~15 grants)
- **OT2020**: 41.3% (`n=46`, ~19 grants) | terminal: 32.4% (`n=37`, ~12 grants)
- **OT2019**: 17.0% (`n=53`, ~9 grants) | terminal: 9.5% (`n=42`, ~4 grants)
- **OT2018**: 23.8% (`n=42`, ~10 grants) | terminal: 9.7% (`n=31`, ~3 grants)
- **OT2017**: 21.6% (`n=51`, ~11 grants) | terminal: 14.6% (`n=41`, ~6 grants)

Pooling across OT2017–OT2025 yields **104 / 426 = 24.4%** for the `state` `[reached]` risk-set baseline (and **53 / 299 = 17.7%** for the terminal `state` band). Across the whole live slice for the `state` band (`n=302` resolved), the grant-family rate is `17.5%` (`9.6%` plenary grant + `7.9%` GVR). For the Fifth Circuit (`ca5`) in the paid scored segment (`n=5,399` resolved), the overall grant-family rate is `3.8%` (`1.7%` granted + `2.1%` GVR).

## Adjustments from the Base Rate

1. **Upward adjustments (doctrinal conflict, 11–6 en banc dissent, and CFR after waiver)**:
   - **Clear doctrinal tension on the "evading review" prong**: Under 18 U.S.C. § 3626(a)(2), preliminary injunctive relief in prison-conditions cases automatically expires after 90 days unless made final. Relying on *Smith v. Edwards*, 88 F.4th 1119 (5th Cir. 2023), the Fifth Circuit panels in *VOTE I*, *VOTE II*, and *VOTE III* held that 90 days is not too short to be fully litigated because an appellant can theoretically obtain expedited review in the Fifth Circuit within 90 days (and faults Louisiana for taking 21 days in *VOTE II* and 17 days in *VOTE III* to notice its appeals). That holding conflicts with this Court's decisions in *Turner v. Rogers*, 564 U.S. 431, 440 (2011) (periods of 12, 18, and 24 months are too short, and the question is whether the dispute can be litigated through the lower courts "and arrive here" prior to expiration), and *FCC v. Consumers' Research*, 606 U.S. 656, 671 n.1 (2025) ("three months is too short to complete judicial review"), as well as decisions from ten other circuits.
   - **Sharp en banc division below**: Six Fifth Circuit judges (Judge Edith Jones, joined by Judges Smith, Richman, Ho, Duncan, and Oldham) dissented at length from the 11–6 denial of rehearing en banc in *VOTE III* (`168 F.4th 339`), and a seventh judge—Judge Cory Wilson, the author of *Smith v. Edwards*—wrote a separate statement agreeing that "[n]inety days is not enough time for a PLRA case to be fully resolved on appeal" and that the district court's serial heat-mitigation injunctions raised issues that should have been reviewed.
   - **Call for Response**: Respondents initially waived a response on July 10, 2026, and the petition was distributed on July 29, 2026 for the Long Conference (`distribution_count: 1`). On August 3, 2026, the Court called for a response. A CFR confirms active interest by at least one chambers and puts summary reversal or plenary review genuinely in play.

2. **Downward adjustments (intervening post-trial remedial judgment and vehicle defects)**:
   - **Severe mootness / vehicle obstacle on the "capable of repetition" prong**: To invoke the "capable of repetition, yet evading review" exception, Louisiana must satisfy *both* prongs: that the challenged orders were too short to be fully litigated *and* that there is a reasonable expectation the same complaining party will be subjected to the same pre-trial 90-day preliminary injunction again. As Judge Wilson explained in concurring in the denial of rehearing en banc (App. 17a)—and as the Petition itself acknowledges on page 18—the underlying bench trial on permanent injunctive relief concluded in 2025, and on **May 26, 2026**, the district court entered a comprehensive post-trial remedial order (*Voice of the Experienced v. LeBlanc*, 2026 WL 1472248 (M.D. La. May 26, 2026)). Once Respondents' counsel (Paul, Weiss) details this post-trial posture in the Brief in Opposition, the Court is likely to see *VOTE II* and *VOTE III* as poor vehicles: even if 90-day PLRA preliminary injunctions categorically "evade review," the summer 2025 pre-trial injunctions have been superseded by final post-trial remedial orders that are appealable on a normal timeline without a 90-day expiration clock.
   - **Zero cert-stage amicus briefs (`cert_amicus: 0`)**: Despite being a state-petitioner PLRA appeal with a published 6-judge en banc dissent, no state coalition or outside amicus filed a brief supporting certiorari within the 30 days after docketing. In the statpack's paid scored segment, petitions with `0` amicus briefs (`n=11,109` resolved) grant at `3.8%` (`2.0%` granted + `1.8%` GVR), versus `22.9%` (`18.4%` granted + `4.5%` GVR, `n=1,449`) for `2+` amici.

Balancing the strong doctrinal argument on "evading review" and explicit summary-reversal pitch against the formidable post-trial vehicle obstacle that the forthcoming BIO will emphasize, I place `probability` (`disposition`) at **0.28**—modestly above the `24.4%` `state` `[reached]` base rate, but still favoring denial (`72%`).

## Auxiliary Claims and Distributions

- **`relist-increment` (`0.78`)**: Because the first distribution (`2026-07-29`) occurred on a waiver before the August 3, 2026 Call for Response, the petition will almost certainly either be re-distributed for an October/November conference once the BIO is filed (especially if Respondents take a routine 30-day extension past September 2) or be relisted at least once after the BIO arrives while chambers circulate a potential summary disposition or separate writing on denial.
- **`cvsg-increment` (`0.01`)**: No federal agency or federal statutory program administered by the Executive Branch is implicated; a CVSG is virtually out of the question.
- **`summary-disposition-route` (`0.45`)**: In the statpack's `state` band (`n=302`), GVRs/summary dispositions account for `7.9% / (9.6% + 7.9%) = 45.1%` of all grants, and in `ca5` (`n=5,399`) GVRs (`2.1%`) exceed plenary grants (`1.7%`). Here, Louisiana explicitly asks for summary reversal as its primary relief, and the error on whether 90 days is long enough for complete judicial review is facially clear under *Turner* and *Consumers' Research*. Conditional on a grant, summary reversal or vacatur in the cert order (`0.45`) is nearly as likely as plenary merits briefing and argument (`0.55`).
- **`dissent-from-denial` (`0.18`) and `order-writers`**: Even if the May 26, 2026 post-trial remedial order persuades a majority of the Court to deny review on vehicle grounds, the combination of a six-judge Fifth Circuit en banc dissent and an outlier circuit precedent (*Smith v. Edwards*) insulating 90-day PLRA injunctions from appellate review makes a separate statement respecting denial or dissent from denial substantially likelier than usual (`0.18` conditional on denial). In `order-writers`, I assign the highest authorship probabilities to Justice Alito (`0.08`, Circuit Justice for the Fifth Circuit), Justice Thomas (`0.07`), and Justice Gorsuch (`0.04`), with smaller probabilities for Justice Kavanaugh (`0.02`, statement respecting denial), Justice Sotomayor (`0.02`, potential dissent from summary reversal), and Justice Jackson (`0.02`, potential dissent from summary reversal).
- **`big_case_score` (`0.35`)**: While important for Fifth Circuit prison-conditions litigation and appellate mootness doctrine, the case involves a narrow procedural and jurisdictional question under Article III and 18 U.S.C. § 3626(a)(2) rather than a high-salience national constitutional or regulatory controversy.
