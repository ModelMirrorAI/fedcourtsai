# Predictor Reasoning: *Shosh Yonay, et al. v. Paramount Pictures Corporation* (No. 26-61)

## Summary of Forecast
- **Predicted Disposition:** `denied` (`granted = 0`)
- **P(grant) (`probability` / `disposition`):** `0.06`
- **Declared Claims (`cert-v3`):**
  - `disposition`: `0.06`
  - `relist-increment`: `0.98`
  - `cvsg-increment`: `0.02`
  - `summary-disposition-route`: `0.08`
  - `dissent-from-denial`: `0.03`
- **Big Case Score:** `0.42`

## Base-Rate Anchoring (`metrics/statpack.md` and `record/context.json`)

From `record/context.json`, this cell is in `forward` mode at `moment: response-requested` (`event_id: evt-order-call-for-response-disposition`), with `snapshot_date: "2026-08-17"`, `cutoff: "2026-08-18"`, `cut_kind: "date"`, `term: 2026`, `band: "baseline"`, `salience_version: "sal-v4"`, `distribution_count: 1`, and `cvsg_date: null`.

1. **Salience Band Anchor (`sal-v4`, `baseline` `[reached]` over strictly prior Terms OT 2016–2025):**
   In `metrics/statpack.md`, the "Segment base rate by salience band (paid scored segment, `sal-v4`)" table matches `context.salience_version` (`sal-v4`). Pooling the bracketed `reached` grant rates for the `baseline` band across all 10 strictly prior Terms (OT 2016–2025, total `n = 11,751`):
   - OT 2016: 6.1% (`n=1254`)
   - OT 2017: 9.7% (`n=1185`)
   - OT 2018: 8.4% (`n=1227`)
   - OT 2019: 7.4% (`n=1180`)
   - OT 2020: 9.0% (`n=1285`)
   - OT 2021: 6.2% (`n=1157`)
   - OT 2022: 5.5% (`n=1100`)
   - OT 2023: 5.9% (`n=1119`)
   - OT 2024: 6.7% (`n=1058`)
   - OT 2025: 5.4% (`n=1186`)
   The sample-weighted 10-Term pooled `baseline` `[reached]` grant rate is **7.1%** (830.6 / 11,751), and the more recent 5-Term average (OT 2021–2025) is **5.9%**. This is my primary anchor.

2. **Signal and Population Cross-Checks (`metrics/statpack.md`):**
   - **Modern discretionary-cert petitions overall (`n = 51,697`):** 2.1% `granted` + 1.7% `gvr` = **3.8%** grant family (94.4% `denied`).
   - **Originating Circuit (`ca9`, `n = 10,334`):** 2.1% `granted` + 1.3% `gvr` = **3.4%** grant family (95.3% `denied`).
   - **Paid scored segment by CVSG status (`none`, `n = 12,350.8`):** 5.9% `granted` + 3.8% `gvr` = **9.7%** grant family (88.4% `denied`).
   - **Paid scored segment by relist count:** `0` relists (`n = 9,154.0`) has a 5.5% grant family (2.9% `granted`, 2.6% `gvr`); `1` relist (`n = 2,718.8`) has an 18.8% grant family (11.9% `granted`, 7.0% `gvr`), though that bucket reflects terminal relist counts and primarily captures conference relists rather than a pre-conference call for response.
   - **Paid scored segment by amicus-brief count:** `1` amicus brief (`n = 49.0`) shows 14.3% `granted` and 2.0% `gvr` (16.3% grant family), though as `statpack.md` notes, `(unknown)` is `n = 12,188.3`, so I place very limited weight on the amicus bucket rate itself.

## Case-Specific Adjustments from the Anchor

Starting from the **7.1%** 10-Term `baseline` `[reached]` anchor (and **5.9%** recent 5-Term rate), I weigh the upward procedural/advocacy signals against the severe vehicle and merits weaknesses revealed by the petition (`petition.txt`, `questions-presented.txt`) and the lower-court opinions (`appendix.txt`):

### Upward Factors
1. **Call for Response (CFR) after Waiver:** Respondent Paramount waived its response on July 23, 2026 (`2026-08-17.json`), and the petition was distributed on July 29, 2026 for the September 29 Long Conference. On August 17, 2026—three days after the Authors Guild et al. amicus brief was filed—the Court requested a response (due September 16, 2026). The CFR shows at least one chamber flagged the petition for a closer look after the waiver, removing the zero-chance tail of unexamined petitions.
2. **Sophisticated Counsel and Amicus Support:** Petitioners are represented by Jeffrey A. Lamken of MoloLamken LLP, a frequent Supreme Court advocate, and supported by a cert-stage amicus brief from five prominent creator organizations (The Authors Guild, Science Fiction and Fantasy Writers Association, Western Writers of America, American Photographic Artists, and Romance Writers of America).
3. **Salient Framing of Substantial-Similarity Methodology:** Petitioners highlight genuine rhetorical and doctrinal tension among the circuits—and within the Ninth Circuit itself, noting the pending en banc rehearing in *Sedlik v. Von Drachenberg*, 166 F.4th 1291 (9th Cir. 2026)—over how courts separate protectable expression from unprotectable elements at summary judgment versus how the Second Circuit applies its "more discerning ordinary observer" and "total concept and feel" formulations.

### Downward Factors (Decisive Against Grant)
1. **The Alleged Split Does Not Drive the Outcome Here:** Petitioners contend that the Second, First, and Seventh Circuits would not permit a court to grant summary judgment by filtering out unprotectable elements without applying an ordinary-observer "total concept and feel" test. Yet the Second Circuit routinely affirms summary judgment or Rule 12(b)(6) dismissal as a matter of law where the similarities between two works consist of historical facts, general ideas, or *scènes à faire*—indeed, Judge Miller's opinion and Judge Anderson's district court order explicitly cite Second Circuit landmarks including *Nichols v. Universal Pictures Corp.*, 45 F.2d 119 (2d Cir. 1930), *Sheldon v. Metro-Goldwyn Pictures Corp.*, 81 F.2d 49 (2d Cir. 1936), *Warner Bros. Inc. v. American Broadcasting Cos.*, 720 F.2d 231, 240 (2d Cir. 1983), and *Williams v. Crichton*, 84 F.3d 581, 589 (2d Cir. 1996) (`appendix.txt` at 10a, 18a, 36a). Under *Feist*, 499 U.S. at 348–50, no circuit permits a jury to find copyright infringement based on the "overall feel" of unprotectable facts about a real military training school.
2. **The Ninth Circuit Expressly Addressed Selection and Arrangement as a Whole:** Petitioners' central premise is that the Ninth Circuit atomized Ehud Yonay's 1983 article by filtering out every factual element in isolation and ignoring how the elements work together (`petition.txt` at 2–4, 24–27). However, Part II.B of Judge Miller's opinion (`appendix.txt` at 14a–18a) specifically analyzed Petitioners' selection-and-arrangement argument across both protectable and unprotectable elements under *Skidmore v. Led Zeppelin*, 952 F.3d 1051, 1074 (9th Cir. 2020) (en banc), and *Hanagami v. Epic Games, Inc.*, 85 F.4th 931, 943 (9th Cir. 2023). The panel explicitly agreed that "an original selection and arrangement could include both protectable and unprotectable elements, and in such cases, a court should compare the selection and arrangement of all the elements" (`appendix.txt` at 15a), but held that the two works share no coherent pattern, synthesis, or design.
3. **Poor Vehicle / Extreme Factual Dissimilarity:** On its facts, this case is a weak vehicle for recalibrating copyright summary-judgment standards. The asserted work is an 11-page 1983 *California Magazine* non-fiction article profiling real F-14 crewmen ("Yogi" and "Possum") at NAS Miramar and recounting the history of the Navy's Top Gun school. The accused work is the 2022 blockbuster sequel *Top Gun: Maverick*, a linear fictional story set decades later at NAS North Island in which an aging Captain Pete Mitchell trains F/A-18 graduates (including his late wingman's resentful son) for a strike on a foreign uranium-enrichment plant. No character, plot sequence, or dialogue (save the real two-word fighter-pilot phrase "fight's on") from the 1983 article appears in the 2022 film.
4. **Unanimous Panel and Zero En Banc Votes Below:** Not a single Ninth Circuit judge requested a vote on rehearing en banc (`appendix.txt` at 46a), even though the Ninth Circuit had just taken *Sedlik v. Von Drachenberg* en banc to examine the *intrinsic* test. That underscores that the Ninth Circuit viewed *Yonay* as an easy, fact-bound application of *Feist*'s fact/expression dichotomy at the summary-judgment stage.

Weighing the modest positive signal of the CFR and strong representation against the poor vehicle fit and unanimous, orthodox application of *Feist* below, I place `probability` (`disposition`) at **`0.06`** (6.0%), slightly below the 10-Term `baseline` `[reached]` rate of 7.1% and right in line with the recent 5-Term `baseline` `[reached]` average of 5.9%.

## Rationale for Auxiliary Claims, Order-Writers, and Big Case Score

- **`relist-increment` (`0.98`):** The snapshot (`2026-08-17.json`) shows 1 distribution (July 29, 2026, for the September 29 Long Conference) followed by the August 17, 2026 Call for Response (due September 16, 2026). Once the BIO is filed and the cert reply comes in, the Clerk will distribute the petition again for a later conference (`distribution_count` will rise from 1 to at least 2) unless the parties settle or dismiss under Rule 46 before re-distribution (~2% chance).
- **`cvsg-increment` (`0.02`):** Private copyright infringement litigation over substantial-similarity summary-judgment standards without a statutory interpretation or federal institutional hook rarely draws a CVSG.
- **`summary-disposition-route` (`0.08`):** Conditional on a grant, the Court would almost certainly set the case for plenary merits briefing and argument; there is no pending Supreme Court case for which this petition is a hold, and only a remote possibility (~8% conditional on grant) of a GVR if an intervening development warranted remand.
- **`dissent-from-denial` (`0.03`) and `order-writers`:** Given the fact-bound record and lack of dissent below, a separate statement or dissent from denial is unlikely (3%), with the small probability mass concentrated primarily on Justice Thomas (`0.010`) and Justice Gorsuch (`0.008`), who have previously written separately on intellectual property or summary-judgment issues.
- **`big_case_score` (`0.42`):** Scored strictly on stakes/significance if decided rather than grant odds, a Supreme Court merits decision addressing the circuit split over substantial similarity and summary judgment in copyright cases—especially in a high-profile dispute over *Top Gun: Maverick*—would be a major precedent for copyright and media law (`0.42`), though below major constitutional or administrative-state cases.

## Uncertainties and Tooling Notes

- Because the snapshot ends on August 17, 2026 (the day the response was requested), Paramount's brief in opposition is not yet part of the provisioned record. My assessment of how Respondent will dismantle the asserted split rests on the lower-court opinions in `appendix.txt` and the Second Circuit authorities cited therein.
- An attempted CourtListener MCP search for the Ninth Circuit's *Sedlik v. Von Drachenberg* opinion returned an upstream HTTP 429 rate-limit error (`Request was throttled. Rate limit exceeded: 1400/day`); per the prompt contract, I fell back gracefully to the provisioned inputs (`petition.txt` and `appendix.txt`, which already describe *Sedlik*'s posture and scope) and the corpus tooling.
