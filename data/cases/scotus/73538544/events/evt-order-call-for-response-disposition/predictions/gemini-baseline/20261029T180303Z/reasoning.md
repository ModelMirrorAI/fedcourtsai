# Predictor Rationale (`reasoning.md`)

## Summary of Call

- **`granted`:** `false` (`predicted_disposition`: `"denied"`)
- **`probability` (`disposition`):** `0.32`
- **`relist-increment`:** `0.95`
- **`cvsg-increment`:** `0.01`
- **`summary-disposition-route`:** `0.90`
- **`dissent-from-denial`:** `0.03`
- **`big_case_score`:** `0.15`

## Base-Rate Anchor (`sal-v4`, `baseline` band)

1. **Salience-band base rate:** `record/context.json` stamps `band: "baseline"`, `salience_version: "sal-v4"`, `term: 2025`, `distribution_count: 1`, `cvsg_date: null`, and `amicus_briefs: null`. In `metrics/statpack.md` (*Segment base rate by salience band (sal-v4)*), the bracketed risk-set (`[reached]`) grant-family rate (plenary grants plus GVRs) for the `baseline` band across the eight Terms strictly preceding OT2025 (OT2017–OT2024) pools to **5.2%** (`n = 11,599` weighted resolved petitions: 5.9% on `n=1274` in OT2024, 5.9% on `n=1312` in OT2023, 5.9% on `n=1196` in OT2022, 5.7% on `n=1500` in OT2021, 4.5% on `n=1740` in OT2020, 4.7% on `n=1399` in OT2019, 4.8% on `n=1529` in OT2018, and 4.9% on `n=1649` in OT2017; in OT2025 itself, the `baseline` `[reached]` rate is 4.0% on `n=1314`).
2. **Other marginal cuts in `metrics/statpack.md`:**
   - **By relist count (paid scored segment):** Bucket `0` (`n=10,203` resolved) resolves `denied 96.8%, granted 1.3%, dismissed 1.3%, gvr 0.5%` (grant family `1.8%`); bucket `1` (`n=2,538` resolved) resolves `denied 85.3%, granted 8.5%, gvr 5.2%, dismissed 1.0%` (grant family `13.7%`); bucket `2` (`n=495` resolved) resolves `denied 57.4%, granted 28.3%, gvr 12.9%, dismissed 1.4%` (grant family `41.2%`); and bucket `3+` (`n=484` resolved) resolves `denied 61.6%, granted 23.1%, gvr 14.3%, dismissed 1.0%` (grant family `37.4%`).
   - **By CVSG status (paid scored segment):** `none` (`n=13,556` resolved) resolves `denied 92.4%, granted 4.1%, gvr 2.3%, dismissed 1.2%` (grant family `6.4%`).
   - **By amicus-brief count (paid scored segment):** `0` (`n=11,109` resolved) resolves `denied 95.0%, granted 2.0%, gvr 1.8%, dismissed 1.2%` (grant family `3.8%`).

## Case-Specific Adjustments from the ~5.2% Anchor

Starting from the **5.2%** (`0.052`) `baseline` `[reached]` prior, I adjust upward to **0.32** based on two strong positive signals in the September 11, 2026 record, tempered by several substantive and vehicle counter-weights:

### Upward Factors

1. **The September 10, 2026 Call for a Response (`moment: response-requested`):**
   - Respondent Irigoyen Farms, Inc. filed a brief in opposition on August 26, 2026, while co-respondent Walmart Inc. (represented by Roman Martinez of Latham & Watkins LLP) filed a waiver on August 27, 2026. The petition was distributed on September 9, 2026 for the September 28, 2026 Long Conference (`distribution_count: 1`).
   - On September 10, 2026—the day after distribution—the Court requested a response from Walmart (due October 13, 2026). Because the Court will not grant or GVR a petition against a respondent that waived without first calling for a response, the CFR confirms that at least one chambers flagged the petition after reading it alongside Irigoyen Farms's opposition and petitioner's reply, clearing the initial dead-list filter that eliminates the vast majority of `baseline` petitions.
2. **Square reliance below on authorities and reasoning repudiated by *Montgomery v. Caribe Transport II, LLC*, 608 U.S. 219 (May 14, 2026):**
   - The California Court of Appeal issued its opinion on September 10, 2025 (certified for publication September 30, 2025, 114 Cal. App. 5th 873), and the California Supreme Court denied review on January 14, 2026—four months *before* this Court decided *Montgomery* on May 14, 2026.
   - In holding that the FAAAA's safety exception, 49 U.S.C. § 14501(c)(2)(A), did not save petitioner's wrongful-death and negligence claims, the Fifth Appellate District expressly rejected the Ninth Circuit's decision in *Miller v. C.H. Robinson Worldwide, Inc.*, 976 F.3d 1016 (9th Cir. 2020), and the Sixth Circuit's decision in *Cox v. Total Quality Logistics, Inc.*, 142 F.4th 847 (6th Cir. 2025) (`petition.txt`, App. 15–17 & n.6). It instead adopted the Eleventh Circuit's "direct connection" rule from *Aspen American Insurance Co. v. Landstar Ranger*, 65 F.4th 1261 (11th Cir. 2023), holding that because petitioner's claims against Walmart and Irigoyen Farms "do not purport the tractor trailer itself was defective or otherwise unsafe," "the FAAAA's safety exception does not apply here" (App. 17–19).
   - Crucially, in footnote 7 of its opinion (App. 19), the Fifth Appellate District stated: *"In light of our disposition, we need not address other arguments raised by the parties."*
   - In *Montgomery*, this Court unanimously rejected *Aspen* and *Ye v. GlobalTranz Enterprises, Inc.*, 74 F.4th 453 (7th Cir. 2023), holding that state common-law negligence duties fall within a State's "safety regulatory authority" and that a law is "with respect to motor vehicles" under § 14501(c)(2)(A) if it "concerns" the vehicles used in transportation—not solely when the tractor-trailer itself is mechanically defective.
   - Because the state appellate opinion predated *Montgomery*, expressly relied on the losing side of the circuit split (*Aspen*) to impose a mechanical-defect limitation that *Montgomery* rejected, and declined to reach any alternative ground for affirmance in footnote 7, the petition presents a classic *Lawrence v. Chater* candidate for a low-cost GVR.

### Downward / Moderating Factors (Why `granted: false` Remains Modal)

1. **Substantial factual and doctrinal distance between freight brokers (*Montgomery*) and shippers/retail consignees (*Casarez*):**
   - *Montgomery* addressed a negligent-hiring/selection claim against a freight broker (C.H. Robinson) whose core service was selecting the motor carrier and trucks to haul freight on the highway.
   - Here, neither respondent is a motor carrier or a freight broker, and petitioner expressly disclaimed vicarious liability or negligent-broker-selection theories below (App. 4). Instead, Irigoyen Farms (the produce grower-shipper) contracted with broker Royal Violet Logistics, which subcontracted with broker SIO Logistics, which hired motor carrier Gold Coast Logistics Group, which engaged independent-contractor driver Andre Hill.
   - Petitioner sued Walmart solely on the theory that its retail supply-chain delivery windows ("onerous contractual requirements") incentivized reckless driving by downstream carriers, and sued Irigoyen Farms on the theory that its loading-dock employees loaded produce onto Hill's trailer and released him despite observing that he was fatigued.
   - Even under *Montgomery*, the Court may well conclude (once Walmart files its requested response) that general retail purchasing and scheduling contracts are too attenuated to "concern motor vehicles" under § 14501(c)(2)(A), or that the differences between upstream shippers/consignees and freight brokers make a GVR unnecessary.
2. **Alternative grounds and experienced Supreme Court opposition counsel:**
   - As Irigoyen Farms's August 26, 2026 opposition notes (`brief-in-opposition.txt`), respondents also moved for summary judgment below on state-law duty and causation grounds (arguing that a produce grower and a retail buyer owe no common-law duty to third-party motorists to police the hours-of-service or fatigue of an independent motor carrier's driver four links down the logistics chain), and Walmart is represented by experienced Supreme Court counsel (Roman Martinez of Latham & Watkins LLP, who filed an amicus brief in *Montgomery* itself).
   - Most petitions in which the Court calls for a response are ultimately denied once the respondent's brief demonstrates why the judgment below does not warrant intervention.
3. **Lack of plenary certworthiness on QP 2 and zero amicus support:**
   - There are no cert-stage amicus briefs (`0` amicus briefs on the docket), and petitioner identifies no circuit or state high-court split on QP 2 (whether non-enumerated entities such as shippers and receivers may invoke § 14501(c)(1) preemption when a state-law claim relates to a carrier's or broker's price, route, or service). Plenary review is therefore very unlikely (~3% unconditional probability), and the grant probability (`0.32`) is driven almost entirely (~29% unconditional probability) by the prospect of a GVR in light of *Montgomery*.

## Rationale for Auxiliary Claims and Distributions

- **`relist-increment` (`0.95`):** The snapshot freezes `distribution_count: 1` (the September 9, 2026 distribution for the September 28 conference). Because the Court called for Walmart's response on September 10, 2026 with a due date of October 13, 2026, the Clerk will distribute the petition again for a late-October or November 2026 conference once the requested opposition and any reply are in. Under the harness's resolution rule (comparing resolution-time `distribution_count` against the cell's frozen `distribution_count: 1`), that post-BIO distribution counts as at least one additional distribution, making `relist-increment` nearly certain (`0.95`, leaving `0.05` for pre-distribution settlement/Rule 46 dismissal or anomalous docket entry formatting).
- **`cvsg-increment` (`0.01`):** The Solicitor General just participated in *Montgomery* during OT2025; the Court will not invite the SG's views on a follow-on GVR petition.
- **`summary-disposition-route` (`0.90`):** Conditional on any grant (`granted` or `gvr`), a summary GVR in light of *Montgomery* accounts for ~90% of the grant mass (`0.29 / 0.32 ≈ 0.906`), as the Court has no reason to schedule full merits briefing and oral argument so soon after deciding *Montgomery*.
- **`dissent-from-denial` (`0.03`) and `order-writers`:** *Montgomery* was unanimous, and routine denials of post-decision GVR petitions rarely provoke a published dissent from denial. Individual `order-writers` probabilities are set between `0.001` and `0.008` (highest for Justice Thomas at `0.008` and Justice Gorsuch at `0.006`, with Justice Kavanaugh—who concurred in *Montgomery*—at `0.004`).

## Provisioning and Upstream Notes

1. **Combined `brief-in-opposition.txt` staging (`flags.json` note):** Under the pipeline's documented rule for multi-respondent oppositions (`docs/document-provisioning.md`: *"A combined opposition is kept or dropped whole. It is dated by its earliest brief, so a cutoff between two respondents' briefs admits the later one (`documents_before`)"*), `record/documents/documents.json` dates `brief-in-opposition.txt` at `"Aug 26 2026"` (the date of Irigoyen Farms's pre-cutoff opposition) and stages the combined text of both Irigoyen Farms's August 26, 2026 brief and Walmart Inc.'s October 13, 2026 response (which postdates the cell's `2026-09-11` cutoff). Although this cell runs in `forward` mode (where post-cutoff docket material is not outcome leakage), `predict.md` specifies that a `moment: response-requested` forecast should reason from the call-day vantage point without relying on what the requested response will say. I have therefore anchored this forecast strictly on the pre-cutoff September 11, 2026 record (the Petition, the Fifth Appellate District's opinion in the Appendix, Irigoyen Farms's August 26, 2026 BIO, Walmart's August 27, 2026 waiver, Petitioner's August 31, 2026 Reply, the September 9 distribution, and the September 10 call for a response) and logged an informational `provisioning` flag in `flags.json`.
2. **CourtListener MCP rate limit:** A single lookup attempt for *Montgomery v. Caribe Transport II, LLC* via the CourtListener MCP `search` tool returned HTTP 429 (`Rate limit exceeded: 1400/day`). Per `predict.md`, I fell back to `uv run fedcourts query` against the local/ranged corpus and the provisioned filings.
