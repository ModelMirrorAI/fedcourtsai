# Rationale

## Forecast and information set

I assign **2.5% to any grant**, including GVR or summary reversal, and predict denial. This is a cert-stage petition-disposition cell; the legacy event has no explicit stage or moment. I use the supplied identifiers and the forward-mode record, not another prediction or any realized outcome.

The baseline is `record/snapshots/2026-09-17.json` [S1]. Its creation-date field is September 15, 2026, and its latest proceeding is the September 14 reply submission. The frozen context supplies Term 2025, `sal-v4`, `baseline`, one distribution, and no CVSG. The snapshot has two distribution entries, July 1 and September 9, but both name the same September 28 conference. I retain the harness's count of one and do not treat the repeated scheduling entry as a completed conference or substantive relist. The July 14 response request after initial waivers is a real attention signal; it is not a CVSG. Both oppositions were filed August 24. [S1, S2]

The provisioned manifest contains only the petition and QP extraction, fetched July 18; both have usable, untruncated text [S3]. I read the questions presented, the petition's account of the decision below and procedural history, and selected arguments. To avoid a one-sided assessment, I retrieved both August 24 opposition PDFs and the September 14 reply directly from the exact Supreme Court document URLs already present in the snapshot. I read selected relevant pages, not every cited authority or the entire appellate record. Details and page locations are in `retrieval.md`.

## Base-rate anchor

The committed statpack's matching `sal-v4` table is the quantitative anchor [S4]. Using every displayed Term strictly before the frozen Term 2025, I pool the **bracketed baseline reached rates**, not the terminal baseline rates:

| Term | Reached rate | Weighted resolved n |
| --- | ---: | ---: |
| 2024 | 5.7% | 1271 |
| 2023 | 5.9% | 1312 |
| 2022 | 5.8% | 1192 |
| 2021 | 5.6% | 1500 |
| 2020 | 4.5% | 1739 |
| 2019 | 4.6% | 1399 |
| 2018 | 4.6% | 1524 |
| 2017 | 4.7% | 1643 |

The executed weighted calculation yields approximately **5.12%, n=11,580**. This is approximate because the displayed percentages are rounded. I exclude Terms 2025 and 2026 and use the frozen baseline band, without reclassifying private employee petitioners as government petitioners merely because the Governor is a respondent.

For shape, the paid-segment terminal relist-0 bucket has a 1.7% grant family, versus 13.3% at relist-1; the CVSG bucket has a 34.9% grant family versus 6.3% without a CVSG. These mixed-Term terminal cuts are descriptive context only, not prospective hazards or substitute anchors. The originating-circuit and whole-modern-cert sections likewise do not supersede the matching band. [S4]

Freshness limitation: these are figures from the committed statpack read on September 17, not a claim about a freshly queried corpus. Its JSON has no build timestamp. `fedcourts corpus-info` could not report corpus-wide freshness because this cell uses the service backend without a client-side connection. I did not pull or query the case's current corpus row; its individual `last_pulled` is unavailable. Case observations are expressly limited to the dated provisioned snapshot and identified pre-decision filings.

## Adjustments from the anchor

**Upward:** The requested response distinguishes this petition from a wholly unattended filing. QP1 raises the interaction between federal drug-consent rules and state employment conditions; QP2 attacks conditioning employment on exposure to PREP Act immunity. The petition frames these as constitutional and federal statutory questions rather than simply an employment grievance. [S1, S3]

**Downward:** The petition itself describes an unpublished affirmance controlled by the published Curtis decision [S3, petition pp. 1, 6-8]. The State asserts no circuit split, identifies preservation objections, and argues that qualified immunity independently defeats the damages claims [S5, pp. 1-2, 22-24]. Shriners adds its private-actor defense and alternative immunity argument [S6, pp. 18-20]. These are respondents' arguments, not independently verified findings about preservation; nevertheless, multiple potential independent grounds make this a less clean vehicle for a broad constitutional ruling.

The reply is not silent on those problems: it identifies pleaded allegations in response to forfeiture, argues that contracted governmental duties establish state action, and characterizes honoring refusal as ministerial rather than discretionary. It also asks for consolidation with three other petitions. [S7, pp. 11-12] That preserves a nonzero review path, but in my assessment does not demonstrate a square appellate conflict or remove the threshold obstacles.

Both BIOs report that the Court already declined review of Curtis; Shriners dates that denial to **June 1, 2026** [S5, pp. 1-2; S6, p. 1]. This is particularly informative because the petition identifies Curtis as controlling its own affirmance. I use that prior, related-case signal as reported in the pre-decision briefs, not as proof about this petition. I did not retrieve the present petition's disposition or independently search Curtis's subsequent history. The decisive related-case context is disclosed in `flags.json`.

Balancing a genuine response request against the reported lead-case denial, absent demonstrated split, unpublished disposition, and vehicle defenses takes my grant estimate below the roughly 5.1% anchor to **2.5%**. This is a judgmental adjustment, not an estimated regression effect. The largest uncertainty is whether a Justice sees a materially different federal-consent issue here despite the related litigation and threshold defenses.

## Other probabilities and stakes

- **Further distribution: 18%.** The forecast starts at the frozen one-distribution state. A hold or one further conference is plausible, but prompt disposal is my modal path; repeated notice of the same September conference does not itself justify a high relist forecast. [S1, S2; predictor assessment]
- **New CVSG: 2%.** The federal regulatory interest gives a possible reason to seek views, but I expect vehicle objections to dominate. There is no existing invitation in the record. [S1; predictor assessment]
- **Summary route given grant: 35%.** Conditional on the rare grant, plenary review remains more likely. Related petitions create a possible coordinated route, but I identified no intervening merits decision requiring a GVR. This is not a 35% unconditional chance of summary relief. [S7, p. 12; predictor assessment]
- **Separate writing given denial: 5%.** I expect an unexplained denial, rather than a statement or noted dissent. This is an aggregate conditional forecast, not a per-Justice vote prediction. [Predictor assessment]
- **Stakes: 0.45.** The QPs have potentially broad implications for healthcare workers, consent, and remedies, but the past-mandate damages posture limits this particular vehicle's practical reach. This score is not grant likelihood. [S3, QPs; S5, p. 1]

I have no known outcome for this petition. No outcome, later case history, other predictor output, or topic-label artifact was consulted. Missing provisioned opposition text was recovered through permitted forward retrieval; the retrieval did not update or replace the common baseline.
