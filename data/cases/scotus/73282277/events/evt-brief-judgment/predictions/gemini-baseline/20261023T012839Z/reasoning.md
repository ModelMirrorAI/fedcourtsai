# Predictor Rationale (`reasoning.md`): *Hamed Kian v. Florida* (No. 25-6623)

## I. Summary of Numbers

- **`probability` (`judgment-disturbed`)**: `0.75` (`granted: 1`, `predicted_disposition: "other"`)
- **`judgment`**: `"reversed"`
- **`votes`**: 6–3 to reverse (Majority: Gorsuch, Thomas, Sotomayor, Kavanaugh, Barrett, Jackson; Dissent: Roberts, Alito, Kagan)
- **`big_case_score`**: `0.85` (high constitutional and practical significance: reconsiders *Williams v. Florida*, 399 U.S. 78 (1970), and whether the Sixth and Fourteenth Amendments require 12-person juries in state felony prosecutions)

---

## II. Provisioned Inputs Consulted

This cell ran in `forward` mode at `moment: briefed` (`cutoff: 2026-09-29`, `cut_kind: date`). We read the provisioned snapshot `data/cases/scotus/73282277/record/snapshots/2026-09-29.json`, `record/context.json`, `events/evt-brief-judgment/event.yaml`, and all provisioned filings in `record/documents/` (as indexed in `documents.json`, none with `empty_text: true` or `truncated: true`):
- `questions-presented.txt` (1 page)
- `petition.txt` (22 pages)
- `brief-in-opposition.txt` (33 pages)
- `appendix.txt` (20 pages)
- `merits-brief-petitioner.txt` (47 pages, filed Aug. 6, 2026)
- `merits-brief-respondent.txt` (69 pages, filed Sep. 28, 2026)

Note on `snapshot_provenance: truncated`: The dated `ProceedingsandOrder` list in `2026-09-29.json` stops before `2026-09-29` (closing with Respondent's merits brief on Sep. 28, 2026, after Petitioner's merits brief and six supporting amicus briefs in August 2026). Because the snapshot provenance is `truncated`, the undated top-level `Other` counsel list also reflects later-docketed amici (including the Solicitor General for the United States, a multistate coalition led by Montana, a second multistate coalition led by Arizona/Connecticut/Louisiana/Utah, and several prosecutor/county/academic amici).

---

## III. Base-Rate Anchor (`metrics/statpack.md`)

Per the prompt's merits-stage anchoring rules, we ignore the cert-stage `band` in `context.json` and anchor on **"The merits docket (granted cases)"** in `metrics/statpack.md`:
- The event's `opened_at` is `2026-09-28` and certiorari was granted on `2026-06-15`, placing the grant in **October Term 2025** (`grant_term = 2025`).
- The merits table publishes the `excluded (not in granted)` column (confirming the pool guard is active) and covers grant Terms `2017` through `2025`.
- Pooling `disturbed` over `parsed` across the grant Terms strictly preceding OT2025 (`2017 <= T < 2025`, eight Terms present in the table):
  - `2024`: `50 / 73` (`68.5%`, `granted = 75`, coverage `73/75 = 97.3%`)
  - `2023`: `34 / 55` (`61.8%`, `granted = 55`, coverage `55/55 = 100.0%`)
  - `2022`: `50 / 73` (`68.5%`, `granted = 74`, coverage `73/74 = 98.6%`)
  - `2021`: `46 / 65` (`70.8%`, `granted = 67`, coverage `65/67 = 97.0%`)
  - `2020`: `57 / 69` (`82.6%`, `granted = 79`, coverage `69/79 = 87.3%`)
  - `2019`: `42 / 54` (`77.8%`, `granted = 56`, coverage `54/56 = 96.4%`)
  - `2018`: `50 / 75` (`66.7%`, `granted = 77`, coverage `75/77 = 97.4%`)
  - `2017`: `31 / 52` (`59.6%`, `granted = 56`, coverage `52/56 = 92.9%`)
- **Strictly-Prior Pooled Baseline (`2017`–`2024`)**: **`360 / 516 = 69.77%` (`69.8%`)** disturbed, well above the 30-judgment minimum floor, with overall parsed coverage of **`516 / 539 = 95.7%`** (`225` reversed, `115` vacated, `10` affirmed in part, vs. `140` affirmed, `12` DIG, `4` equally divided).

---

## IV. Adjustments from the Base Rate (`0.698` → `0.75`)

### 1. Upward Adjustments (`+0.12`)
- **Why the Court Granted Certiorari**: There is no lower-court split on whether six-person felony juries are constitutional because *Williams v. Florida* is binding Supreme Court precedent that no state or lower federal court may depart from. The Court had no institutional need to grant an *in forma pauperis* petition from a per curiam affirmance to reaffirm *Williams*. Rather, the grant follows repeated dissents from denial of certiorari by Justice Gorsuch in *Khorrami v. Arizona*, 143 S. Ct. 22 (2022), and *Cunningham v. Florida*, 144 S. Ct. 1287 (2024), along with recorded votes to grant by Justice Kavanaugh (in both *Khorrami* and *Cunningham*) and Justice Jackson (in *Cunningham*).
- **Vehicle Selection (`Parada` vs. `Kian`)**: Our corpus query confirmed that on January 12, 2026, the Court denied certiorari in *Parada v. United States*, No. 25-166 (`scotus/73274854`), which challenged an 11-juror federal verdict after a mid-deliberation good-cause excusal under Fed. R. Crim. P. 23(b)(3), and then granted *Kian* on June 15, 2026. Selecting the pure state-court six-person felony jury vehicle while passing on the federal Rule 23(b)(3) vehicle strongly indicates that the grant coalition specifically targeted *Williams*.
- **Doctrinal Alignment with *Ramos* and *Erlinger***: *Ramos v. Louisiana*, 590 U.S. 83 (2020), dismantled *Williams*'s twin pillars (reliance on the First Senate's deletion of Madison's "accustomed requisites" clause and 1970s functionalism), and *Erlinger v. United States*, 602 U.S. 821, 831 (2024), saw a six-Justice majority (Roberts, Thomas, Sotomayor, Kagan, Gorsuch, Barrett) expressly invoke Blackstone's rule that a felony accusation must be confirmed by the unanimous suffrage of twelve equals and neighbors.

### 2. Downward Adjustments and Main Uncertainties (`-0.07`)
- **Substantial *Stare Decisis* and Reliance Pressures**: Respondent's merits brief makes a much stronger reliance showing than Louisiana and Oregon could make in *Ramos*. Unlike *Apodaca*'s fractured 4-1-4 result, *Williams* was a 7-1 opinion of the Court. Florida has ~5,200 pending criminal direct appeals, built its non-capital courtrooms around six-person jury boxes, and is joined by state and federal amici warning of disruption across six states for felonies, 27 states for misdemeanors, and potential spillover challenges to Fed. R. Crim. P. 23(b)(3) and Fed. R. Civ. P. 48(a).
- **Historical Counter-Evidence**: Respondent also marshals the 1665 colonial *Duke's Laws*, Welsh six-man juries, James Wilson's lecture remark, nine pre-1868 state constitutions permitting legislative regulation of jury size, and the bipartisan 1875 Florida Reconstruction legislature's fiscal rationale to argue that the 12-person rule is not on all fours with *Ramos*'s unanimity record.
- **Swing-Justice Uncertainty**: While Gorsuch, Thomas, Sotomayor, and Jackson form a solid four-vote bloc to overrule *Williams*, Petitioner needs at least one (and likely obtains both) of Justices Kavanaugh and Barrett. Because Justice Kavanaugh voted to grant in both *Khorrami* and *Cunningham* and authored *Edwards v. Vannoy*, 593 U.S. 255 (2021)—which insulates final convictions on collateral review—we estimate a 75% probability that at least five (and most likely six: Gorsuch, Thomas, Sotomayor, Kavanaugh, Barrett, Jackson) vote to overrule *Williams* and reverse, leaving a 25% probability that *stare decisis* holds a narrow majority to affirm (or, far less likely, produces a DIG).
- **Choice of `"reversed"` over `"vacated"`**: In *Ramos*, 590 U.S. at 111, the Court entered a judgment of `"reversed"` rather than `"vacated"`, and Petitioner's brief requests reversal. Because `reversed` accounts for roughly two-thirds (`225 / 350`) of full disturbances in the strictly-prior statpack pool and matches *Ramos*, we select `"reversed"` as the modal judgment label.
