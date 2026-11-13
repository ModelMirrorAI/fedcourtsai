# Predictor Rationale — `scotus/72483489` / `evt-brief-judgment`

## Summary of Forecast

- **`probability` (`judgment-disturbed`):** `0.88` (`granted = 1`, `predicted_disposition = "other"`)
- **`judgment`:** `vacated` (decomposed internally as `P(vacated) = 0.65`, `P(reversed) = 0.23`, `P(affirmed) = 0.12`, with `<0.02` folded into `undisturbed` for a post-argument DIG)
- **Predicted vote lineup:** `9–0` (`majority` for all nine sitting Justices)
- **`big_case_score`:** `0.28`

## Provisioned Inputs and Mode

This is a **forward-mode** merits cell (`context.mode = "forward"`, `context.cutoff = "2026-11-05"`, `DECIDED_BEFORE` unset) at `moment: briefed` (`opened_at = 2026-11-04`, the day Respondent PepsiCo filed its merits brief; oral argument is calendared for January 12, 2027).

From `data/cases/scotus/72483489/record/`, I read:
- `context.json` and `snapshots/2026-11-05.json` (`input_snapshot = "2026-11-05.json"`);
- `documents/documents.json`, `questions-presented.txt`, `lower-court-docket.txt`, and `decision-below.txt` (Second Circuit Dec. 19, 2024 summary order in *RiseandShine IV*, No. 23-1176);
- Cert-stage briefs: `sg-invited-brief.txt` (CVSG brief of the United States, May 20, 2026) and `supplemental-brief.txt` (both parties' June 8, 2026 supplemental briefs);
- Merits-stage briefs: `merits-brief-petitioner.txt` (RiseandShine's opening brief, Sept. 8, 2026) and `merits-brief-respondent.txt` (PepsiCo's response brief, Nov. 4, 2026).

**Provisioning note on the United States' merits amicus brief:** The docket snapshot (`2026-11-05.json`) records on September 15, 2026 both `"Amicus brief of United States not accepted for filing. (September 17, 2026--corrected version to be efiled.)"` and `"Brief amicus curiae of United States supporting vacatur filed. (Corrected)"`, but `merits-amicus-united-states.txt` was not staged in `record/documents/` (recorded in `flags.json` under `provisioning`, severity `info`). Even without that file staged separately, the Solicitor General's full substantive position is transparent from (1) the docket entry's explicit caption (`supporting vacatur`), (2) the staged CVSG brief (`sg-invited-brief.txt`), and (3) Respondent's merits brief (`merits-brief-respondent.txt`), which repeatedly summarizes and cites `SG.Br.` (e.g., pp. 30–33, 44, 52, 56 n.7). I did not retrieve any post-`2026-11-05` filings on this docket so the forecast strictly reflects `moment: briefed`.

## Base-Rate Anchor (`metrics/statpack.md`)

Certiorari was granted on **June 29, 2026**, placing this case in **grant Term 2025** (October Term 2025). Under the prompt contract's ten-Term lookback rule (`2015 <= T < 2025`, strictly before `grant_term = 2025`), `metrics/statpack.md`'s *"The merits docket (granted cases)"* table publishes `excluded (not in granted)` counts (making the pool guard-clean and quotable) across eight available grant Terms (**OT2017–OT2024**; OT2015–OT2016 have no parsed rows in the pack):

- **Pre-guard exclusions (`OT2017–OT2024`):** `19` cert-order dispositions removed (`6 + 3 + 2 + 3 + 3 + 1 + 0 + 1`).
- **Cohort and parse coverage (`OT2017–OT2024`):** `534` parsed, dated judgments out of `549` merits-opening grants (**`97.3%` coverage**).
- **Pooled merits disturbed baseline (`OT2017–OT2024`):** `376` disturbed (`239` reversed + `125` vacated + `12` affirmed-in-part) vs. `158` undisturbed (`142` affirmed + `12` DIG + `4` equally divided) = **`70.4%` (`376 / 534`)**.

I did not anchor on `context.band` (`high`), which is a spent cert-stage salience feature.

## Adjustments from `0.704` to `0.88`

Starting from the **`0.704`** merits disturbed baseline, three converging case-specific signals justify a substantial upward adjustment to **`0.88`**, tempered by one serious respondent counterweight:

1. **Certiorari granted over the Solicitor General's vehicle objection after the SG agreed the Second Circuit erred (`+0.09`):** In its May 2026 CVSG brief (`sg-invited-brief.txt`), the Solicitor General squarely concluded that the Second Circuit erred in treating inherent trademark strength as a pure question of law, explaining under *Hana Financial*, *Booking.com*, and *Village at Lakeridge* that inherent strength is a mixed question in which factual issues of ordinary consumer perception predominate—yet recommended denying review solely because other *Polaroid* factors made the case a questionable vehicle for changing the bottom-line summary judgment. The Court granted certiorari anyway on June 29, 2026. When the Court overrides an SG vehicle objection after the SG agrees the court below applied an erroneous outlier rule, the probability that the Court took the case to *affirm* the outlier rule is very small.
2. **United States merits amicus brief supporting vacatur (`+0.05`):** On the merits, the United States filed an amicus brief supporting vacatur. Our forecast closely follows the Solicitor General's position on both axes: (a) rejecting the Second Circuit's "question of law" rule in favor of treating conceptual strength as predominantly factual, and (b) vacating and remanding rather than reversing outright or affirming on alternative grounds in the first instance.
3. **12-to-1 circuit split and doctrinal fit with *Hana Financial*, *Booking.com*, and *Jack Daniel's* (`+0.06`):** Eleven circuits treat trademark strength (including conceptual placement on the *Abercrombie* spectrum) as a factual issue for the jury or clear-error review. In its merits brief, PepsiCo notably retreats from defending a pure question-of-law label and instead urges treating inherent strength as a primarily *legal* mixed question akin to copyright fair use in *Google LLC v. Oracle America, Inc.*, 593 U.S. 1 (2021), or patent claim construction in *Markman*. That analogy faces steep headwinds: *Hana Financial* (9–0) and *Booking.com* (8–1, with only retired Justice Breyer dissenting) already classified trademark commercial-impression and *Abercrombie* boundary questions as factual inquiries into consumer perception, and *Jack Daniel's* (9–0) resisted importing speech-driven threshold legal screens into ordinary source-identifying Lanham Act confusion disputes.
4. **Counterweight — PepsiCo's Rule 56 / *Polaroid* alternative-ground affirmance defense (`-0.024`, keeping `1 - P = 0.12`):** PepsiCo's merits brief mounts a disciplined alternative-grounds argument: even under Rule 56's factual standard, no reasonable jury could deem "RISE" conceptually strong for morning caffeinated beverages given dictionary usage, crowded third-party coffee marks, and RiseandShine's own PTO prosecution statements, and in any event the Second Circuit noted waiver as to other *Polaroid* factors (dissimilarity of the "MTN DEW"-branded cans and lack of acquired strength). While the Court strongly prefers vacatur and remand ("court of review, not first view") when correcting an appellate legal standard—as it did unanimously in *Jack Daniel's*, *Dewberry Group*, and *Hughes v. Northwestern University*—there remains roughly a `9%` chance the Court affirms on harmless-error / alternative Rule 56 grounds plus a `~2–3%` chance of a DIG or legal-gatekeeper affirmance, yielding `0.12` undisturbed and **`0.88` disturbed**.

## Why `judgment = "vacated"` Over `"reversed"`

Conditional on disturbing the judgment (`0.88`), **`vacated` (`~0.65`)** is substantially likelier than **`reversed` (`~0.23`)**. RiseandShine's opening brief asks only to reject the Second Circuit's legal-question rule and remand without asking this Court to adjudicate the full *Polaroid* summary-judgment record itself; the Solicitor General explicitly supports **vacatur**; and PepsiCo expressly argues (Resp. Br. 56 n.7, citing `SG.Br.32`) that if the Court disagrees on the question presented, it should vacate and let the Second Circuit address alternative grounds. That posture mirrors *Jack Daniel's* (599 U.S. at 163), *Abitron* (600 U.S. at 428), and *Dewberry* (604 U.S. at 328), all of which vacated and remanded.

## Per-Justice Votes and Authorship Distributions

Pooling `metrics/statpack.md`'s *"Per-Justice merits votes (complete lineups)"* strictly before `grant_term = 2025` (**OT2020–OT2024**, 5 Terms; **OT2022–OT2024** for Justice Jackson):
- **With-judgment rates (`OT2020–OT2024`):** Kavanaugh `254/269` (`94.4%`), Roberts `253/269` (`94.1%`), Barrett `232/257` (`90.3%`), Alito `211/266` (`79.3%`), Gorsuch `211/267` (`79.0%`), Thomas `212/269` (`78.8%`), Kagan `206/269` (`76.6%`), Jackson `121/162` (`74.7%`, OT2022–OT2024), Sotomayor `196/269` (`72.9%`).
- **Plain-judgment disturb rates (`OT2020–OT2024`):** Kavanaugh `185/257` (`72.0%`), Roberts `181/257` (`70.4%`), Gorsuch `173/252` (`68.7%`), Barrett `165/245` (`67.3%`), Kagan `169/252` (`67.1%`), Sotomayor `167/250` (`66.8%`), Jackson `101/152` (`66.4%`), Alito `158/251` (`62.9%`), Thomas `159/257` (`61.9%`).

Because technical Lanham Act and mixed-question cases on this Court regularly produce unanimous lineups (*Hana Financial* 9–0; *Village at Lakeridge* 9–0; *Jack Daniel's* 9–0; *Dewberry* 9–0; *Booking.com* 8–1 with only Breyer dissenting; and Thomas/Alito having *dissented* from *Google v. Oracle*'s legal-question approach while Gorsuch/Thomas strongly favor civil jury factfinding), **`majority` for all nine Justices** maximizes expected vote accuracy.

For **`majority-author`**, I weight **Sotomayor (`0.200`)** and **Kagan (`0.195`)** highest given Sotomayor's authorship of *Hana Financial* and Second Circuit trademark background and Kagan's authorship of *Village at Lakeridge*, *Jack Daniel's*, and *Dewberry* (slightly discounted only because she authored two recent trademark opinions), followed by **Barrett (`0.130`)**, **Thomas (`0.110`, *Bufkin* / *Elster*)**, and **Gorsuch (`0.105`)**. For **`separate-writers`**, I assign modest positive probabilities led by **Thomas (`0.18`)**, **Gorsuch (`0.18`)**, **Sotomayor (`0.17`, who concurred in *Booking.com*, *Jack Daniel's*, *Abitron*, *Dewberry*, and *Lakeridge*)**, and **Alito (`0.16`, likeliest to write separately on Rule 56 gatekeeping or alternative grounds)**.

## Main Uncertainties

1. **Label split between `vacated` and `reversed`:** Even when remanding for further summary-judgment proceedings, the Court occasionally uses `"reversed and remanded"` rather than `"vacated and remanded"`; that wording choice is our single largest source of exact-match `judgment` error (`~23%`).
2. **Oral argument testing of harmless error / DIG:** Oral argument has not yet occurred; if multiple Justices press RiseandShine on appellate waiver of the other *Polaroid* factors, affirmance on alternative grounds (or a narrow DIG) could rise above `0.12`.
