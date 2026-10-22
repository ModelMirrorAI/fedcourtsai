# Predictor Rationale — *John O. Green v. United States* (No. 26-531)

## Summary of Forecast

- **`probability` / `disposition`:** `0.01` (`granted: 0`, `predicted_disposition: "denied"`)
- **`relist-increment`:** `0.97`
- **`cvsg-increment`:** `0.001`
- **`summary-disposition-route`:** `0.35`
- **`dissent-from-denial`:** `0.01`
- **`big_case_score`:** `0.08`

## Provisioned Inputs Consulted

- **Snapshot:** `2026-10-22.json` (`mode: "forward"`, `moment: arrival`, `cutoff: "2026-10-22"`, `cut_kind: "date"`, `band: "baseline"`, `salience_version: "sal-v4"`, `distribution_count: 0`, `cvsg_date: null`, `signals_observable: true`, `term: 2026`).
- **Provisioned documents (`documents.json`):** `questions-presented.txt` (full text, not truncated) and `petition.txt` (42 pages, full text including Appendices A–D: the Fifth Circuit's July 21, 2026 COA denial order, the Northern District of Texas's November 13, 2025 memorandum opinion and order dismissing the § 2255 motion as time-barred, and the 2023 certiorari denial letters in *Green v. United States*, No. 22-508, and *Selgas v. United States*, No. 22-729). No brief in opposition has been filed yet because the petition was docketed on October 21, 2026, with the response due November 20, 2026.

## Base-Rate Anchor (`metrics/statpack.md`)

This is a `cert`-stage prediction at `moment: arrival` for a paid private petitioner (`John O. Green`), whose frozen salience band in `record/context.json` is `baseline` under `sal-v4`.

1. **Arrival caption-class floor (`baseline` bracketed `reached` rate under `sal-v4`):** Pooling the `baseline` band's bracketed `reached` rates across all 9 rendered prior Terms strictly preceding OT2026 (OT2017–OT2025) in `metrics/statpack.md` yields approximately **5.0%** (`~643.7` weighted grants over `n = 12,883` weighted resolved petitions; the most recent completed Term, OT2025, is `3.9% [n=1303]`).
2. **Originating circuit cut (`ca5`):** In the modern discretionary-cert originating-circuit table, Fifth Circuit petitions have an estimated grant-family rate of **3.7%** (`1.6%` granted + `2.1%` GVR, `94.7%` denied over `5,396` resolved cases).

## Case-Specific Adjustments

Starting from the ~5.0% `baseline` arrival base rate (and 3.9% in OT2025), several strong case-specific factors warrant a substantial downward adjustment to `0.01`:

1. **Conceded Absence of a Circuit Split:** The petition explicitly concedes (Pet. 6–8) that neither Petitioner nor the district court could find *any* appellate decision addressing whether one co-defendant's separate certiorari petition delays finality under 28 U.S.C. § 2255(f)(1) for another co-defendant whose own certiorari petition was already denied. Every district court to consider analogous co-defendant finality arguments (*Cuciniello v. United States*, *Savell v. United States*, *United States v. Westcott*) has rejected piggybacking on a co-defendant's certiorari filing.
2. **Straightforward Textual and Doctrinal Resolution Under *Clay*:** Under 28 U.S.C. § 2255(f)(1), the one-year limitation period runs from "the date on which the judgment of conviction becomes final." In *Clay v. United States*, 537 U.S. 522, 527 (2003), the Court held without qualification that "[f]inality attaches when this Court affirms a conviction on the merits on direct review or denies a petition for a writ of certiorari, or when the time for filing a certiorari petition expires." Green filed his own certiorari petition (No. 22-508), which the Supreme Court denied on January 23, 2023 (143 S. Ct. 747). While Supreme Court Rule 13(3) coordinates the deadline to *file* a certiorari petition when a co-party seeks rehearing in the court of appeals, once co-defendants file separate certiorari petitions under Rule 12(4), each defendant's judgment of conviction becomes final when his own petition is denied. Green's reliance on a ministerial Fifth Circuit clerk's letter transmitting the denial of Selgas's later petition (No. 22-729) with both consolidated trial docket numbers listed in the caption presents a factbound contention rather than a certworthy legal question.
3. **Poor Vehicle and Summary COA Posture:** The order below (Pet. App. 1a–2a) is an unpublished, two-page, single-judge Fifth Circuit order (Judge Edith H. Jones) denying a certificate of appealability under 28 U.S.C. § 2253(c)(2) and *Slack v. McDaniel*, 529 U.S. 473, 484 (2000). Under *Slack*, a petitioner challenging a procedural dismissal must show *both* that jurists of reason would find the procedural ruling debatable *and* that the motion states a debatable constitutional claim. Because the district court never reached Green's underlying constitutional claims (Pet. App. 5a n.2) and the Fifth Circuit denied a COA in a single sentence without addressing them, the case is an unattractive vehicle for plenary review. Moreover, Green was sentenced in June 2021 to 6 months' imprisonment and 3 years' supervised release, diminishing the practical stakes.

## Secondary Claims and Big-Case Score

- **`relist-increment` (`0.97`):** Because `context.json` freezes `distribution_count: 0` at `moment: arrival` (`signals_observable: true`), `relist-increment` measures whether the resolution-time distribution count exceeds zero—that is, whether the petition is distributed for conference at least once. Only petitions dismissed or withdrawn under Rule 46 before distribution fail to reach `distribution_count >= 1` (~1.2%–2.0% of paid petitions in the statpack). Thus `P(distribution_count >= 1) = 0.97`. (By contrast, the probability that the petition is relisted for a *second* conference once distributed, `distribution_count >= 2`, is low at ~0.08 given the lack of a split.)
- **`cvsg-increment` (`0.001`):** The United States is the respondent, represented by the Solicitor General, so a CVSG is structurally inapplicable.
- **`summary-disposition-route` (`0.35`):** Conditional on the unlikely event of a grant, there is a 35% chance the Court would summarily vacate or GVR the COA denial under *Slack v. McDaniel* rather than set a factbound COA denial down for full merits briefing and oral argument.
- **`dissent-from-denial` (`0.01`):** With no circuit conflict, no capital sentence, and a straightforward application of *Clay*, a dissent or statement respecting denial is very unlikely.
- **`big_case_score` (`0.08`):** The case is a narrow, fact-specific post-conviction timeliness dispute arising from an unpublished COA denial with minimal public or doctrinal salience if decided.

## Uncertainties

The primary uncertainty is whether the Court or an individual Justice views the interaction between consolidated direct appeals and separate certiorari petitions under § 2255(f)(1) as a technical gap in *Clay* worth clarifying, though the absence of any lower-court disagreement makes certiorari review highly improbable.
