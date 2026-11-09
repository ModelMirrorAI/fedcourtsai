# Prediction Reasoning: *Wes Allen, Alabama Secretary of State, et al. v. Bobby Singleton, et al.* (No. 26-118)

## 1. Executive Summary & Forecast

- **Event**: `evt-order-relist-disposition` (`stage: cert`, `moment: relist`, `distribution_count: 3`)
- **Predicted Disposition**: `gvr` (`granted: 1`, `probability: 0.78`)
- **Disaggregated Outcome Distribution**:
  - `gvr` (vacatur and remand—either as moot under *United States v. Munsingwear, Inc.*, 340 U.S. 36 (1950), following the conclusion of the 2026 congressional election cycle, or on the merits in light of *Louisiana v. Callais*, 146 S. Ct. 1131 (2026), and *Abbott v. LULAC*, 2026 WL 1127246 (U.S. Apr. 27, 2026)): **0.48**
  - `granted` (probable jurisdiction noted, or consideration of jurisdiction postponed to the hearing on the merits, for full briefing and oral argument alongside Nos. 26-116 and 26-117): **0.22**
  - `summary-reversal` (per curiam summary reversal of the May 26, 2026 preliminary injunction on the merits): **0.08**
  - `dismissed` (appeal dismissed as moot or for want of jurisdiction without vacating the May 26, 2026 preliminary injunction): **0.21**
  - `denied` (summary affirmance of the three-judge district court's preliminary injunction): **0.01**
- **Total Grant-Family Probability (`P(granted = 1)`)**: `0.48 + 0.22 + 0.08 = 0.78`.

---

## 2. Base-Rate Anchor & Trajectory Conditioning

Per `record/context.json` and `metrics/statpack.md`, this cell is frozen in the **`high` salience band** (`sal-v8`) at `distribution_count = 3` (two relists after its initial October 16, 2026 conference distribution):

1. **Pre-computed Segment Anchor (`cert_anchor`)**: Over the 10 prior Terms (OT2016–OT2025), the risk-set grant-family rate for dockets reaching the `high` salience band is **`0.3484`** (34.84%). Across all resolved `high`-band dockets in the modern live/historical slice (`n = 773`), the breakdown is `denied 63.8%`, `granted 22.4%`, `gvr 12.4%`, `dismissed 1.4%` (`34.8%` grant-family rate).
2. **Relist Trajectory (`relist_bucket = 2`)**: Across the paid scored segment in `metrics/statpack.md`, petitions with `distribution_count = 3` (`relist_bucket = 2`, `n = 495` resolved) resolve `denied 57.4%`, `granted 28.3%`, `gvr 12.9%`, `dismissed 1.4%` (**41.2%** grant-family rate).
3. **Mandatory Direct-Appeal Adjustment (28 U.S.C. § 1253)**: Unlike a discretionary petition for certiorari from a circuit court, No. 26-118 is a **mandatory-jurisdiction direct appeal under 28 U.S.C. § 1253** from a three-judge district court order granting a preliminary injunction against a state congressional redistricting statute (`Ala. Code § 17-14-70`), docketed alongside its consolidated three-judge companion appeal *Allen v. Milligan*, No. 26-117, and the companion petition for certiorari before judgment in *Allen v. Caster*, No. 26-116 (`record/same-question.json`). Moreover, this exact trio already resulted in (a) a vacatur and remand (`disposition: "gvr"`) on May 11, 2026 in the prior direct appeals from the May 2025 permanent injunction (No. 25-273 in *Singleton*, No. 25-274 in *Milligan*, and *Allen v. Caster*, 146 S. Ct. 1196 (2026)), and (b) a 6–3 Supreme Court stay of the very May 26, 2026 preliminary injunction now on appeal (*Allen v. Milligan*, 608 U.S. ___, 146 S. Ct. 1377 (June 2, 2026)). These case-specific features justify a substantial upward adjustment from the `0.3484` segment anchor to **`0.78`**.

---

## 3. Procedural Posture, Provisioned Record, and the November 3, 2026 Election

### A. Provisioned Filings vs. Docket Entries
In `record/documents/`, three filings are provisioned (`documents.json`):
- `petition.txt` and `questions-presented.txt`: Appellants' Jurisdictional Statement filed July 22, 2026 (docketed July 24, 2026).
- `appendix.txt`: Appellants' Appendix (`App.1a–678a`), containing the three-judge district court's May 26, 2026 Preliminary Injunction order (`App.1a–78a`), Judge Manasco's May 26, 2026 Preliminary Injunction order in *Caster* (`App.79a–106a`), the May 8, 2025 Permanent Injunction opinions (`App.107a–668a`), the May 26, 2026 Notices of Appeal (`App.669a–74a`), and the Eleventh Circuit's June 25, 2026 order staying the *Caster* appeal (`No. 26-11828`) pending this Court's disposition of *Singleton* and *Milligan* (`App.675a–76a`).

On the docket snapshot (`record/snapshots/2026-11-09.json`), two subsequent filings appear that were not provisioned as text files (because the provisioning matcher looks for `Motion to dismiss or affirm` / `Brief in opposition` rather than a bare `Motion to dismiss`):
- **September 18, 2026**: `"Motion to dismiss filed by appellees Bobby Singleton, et al."`
- **September 29, 2026**: `"Response to motion to dismiss from appellants Wes Allen, et al. filed. (Distributed)"`

### B. Why Appellees Filed a "Motion to Dismiss" (Rather Than a Rule 18.6 "Motion to Dismiss or Affirm") and Why the Court Held the Case Past November 3, 2026
The sequence of events in the record explains both the caption of Appellees' September 18, 2026 motion and the timing of the Court's conference distributions:
1. **May 11, 2026 Remand**: After deciding *Louisiana v. Callais*, 608 U.S. ___, 146 S. Ct. 1131 (Apr. 29, 2026), this Court on May 11, 2026 vacated the three-judge court's May 2025 permanent injunction and remanded for further consideration in light of *Callais* (No. 25-273 in *Singleton*; No. 25-274 in *Milligan*; *Allen v. Caster*, 146 S. Ct. 1196 (2026)).
2. **May 26, 2026 Preliminary Injunction Limited to the 2026 Elections**: On remand, Plaintiffs moved for a preliminary injunction strictly for the **2026 congressional elections** (`App.13a–14a`). In its May 26, 2026 order (`Singleton Doc. 363` / `Milligan Doc. 537`, `App.1a–78a`), the three-judge district court expressly limited its operative mandate (`App.77a`, ¶¶ 1–2) to the 2026 election cycle:
   - Paragraph 1: *"The Court PRELIMINARILY ENJOINS the Alabama Secretary of State from conducting the 2026 congressional elections according to the 2023 Plan."*
   - Paragraph 2: *"The Court further ORDERS the Alabama Secretary of State to administer all remaining events comprising Alabama's 2026 congressional elections according to the Special Master Plan (appended to this Order as Appendix E)."*
   - Paragraph 4 (`App.77a–78a`): Directed the parties to meet and confer on a scheduling order for further proceedings ahead of the **2028 congressional elections** (noting that major-party candidate qualifying for the 2028 primaries opens in November 2027).
3. **June 2, 2026 Supreme Court Stay (*Allen II*)**: Seven days later, in *Allen v. Milligan*, 608 U.S. ___, 146 S. Ct. 1377 (June 2, 2026) (*Allen II*, Nos. 25A1314, 25A1315, 25A1316), a 6–3 majority of this Court stayed the May 26, 2026 preliminary injunctions pending appeal in a per curiam opinion (over a 25-page dissent by Justice Jackson, joined by Justices Sotomayor and Kagan). The Court held that under *Purcell v. Gonzalez*, 549 U.S. 1 (2006), the district court erred by enjoining the 2023 Plan when Alabama had enacted HB 1 (`Ala. Code § 17-13-3.1`) scheduling a special primary election for August 11, 2026 under the 2023 Plan.
4. **Post-Stay District Court Activity and Expiration of the 2026 Election Cycle**: Following the June 2, 2026 stay, Alabama conducted its August 11, 2026 special primary election and its **November 3, 2026 general election** under the 2023 Plan (`petition.txt` at 8–10; *Allen II*, 146 S. Ct. at 1378–80). Meanwhile, on June 22, 2026, the *Singleton* and *Milligan* Plaintiffs filed motions in the district court to alter the judgment (`Singleton Doc. 369`; `Milligan Doc. 545`), and on September 18, 2026, Appellees moved in this Court to **dismiss** the interlocutory appeal (as moot in light of the June 2, 2026 stay and the impending completion of the 2026 elections).
5. **Conference Timing Around Election Day (November 3, 2026)**:
   - First distribution: **Conference of October 16, 2026** (distributed September 30, 2026).
   - Rather than acting before Election Day, the Court held Nos. 26-116, 26-117, and 26-118 until **November 2, 2026** (the day before the November 3, 2026 general election), when it distributed all three dockets for the **Conference of November 6, 2026**—the very first Conference after the 2026 general election concluded.
   - On **November 9, 2026**, the Court relisted all three dockets for the **Conference of November 13, 2026** (`distribution_count = 3`).

---

## 4. Substantive Merits Under *Louisiana v. Callais* and *Abbott v. LULAC*

In the Jurisdictional Statement (`petition.txt` at i, 12–37; `questions-presented.txt`), Appellants present three substantive questions challenging the May 26, 2026 preliminary injunction:
1. **Section 2 of the VRA after *Louisiana v. Callais***: In *Louisiana v. Callais*, 608 U.S. ___, 146 S. Ct. 1131 (Apr. 29, 2026) (Alito, J., joined by Roberts, C.J., and Thomas, Gorsuch, Kavanaugh, and Barrett, JJ.), this Court held that Section 2 enforces the Fifteenth Amendment's ban on intentional racial discrimination and updated the *Thornburg v. Gingles*, 478 U.S. 30 (1986), framework in three critical respects:
   - Under *Gingles* I, a plaintiff's illustrative maps cannot use race as a districting criterion and **must satisfy all of the State's legitimate nonracial districting objectives**, including traditional districting criteria and the State's specified political goals (`146 S. Ct. at 1147–49`).
   - Under *Gingles* II and III, plaintiffs must provide an analysis that **controls for party affiliation**, showing racial-bloc voting that cannot be explained by partisan preferences (`id. at 1149`).
   - Under the totality of the circumstances, plaintiffs must establish a strong inference of present-day intentional racial discrimination rather than relying on historical discrimination or socio-economic disparities (`id. at 1149–50`).
   On remand, the three-judge district court acknowledged that *Callais* "marked a major shift in Section Two jurisprudence" (`App.6a`), yet still concluded Plaintiffs were likely to succeed under Section 2 without requiring race-blind illustrative maps that kept Mobile and Baldwin Counties together in CD-1 or avoided pairing incumbents, and without any statistical control for partisan affiliation under *Gingles* II and III (`App.43a–70a`). Instead, the panel reasoned that Alabama's Gulf Coast and incumbency goals were not "legitimate" under *Callais* because the panel had previously found the 2023 Plan was motivated by an intent to maintain only one majority-Black district (`App.55a–60a`). As Appellants argue (`petition.txt` at 14–25), that reasoning is circular and collapses *Callais*'s objective *Gingles* preconditions.
2. **Fourteenth Amendment Intentional Vote Dilution after *Abbott v. LULAC* and *Alexander***: The three-judge panel primarily rested its May 26, 2026 preliminary injunction on the ground that *Callais* left untouched its May 2025 finding of intentional vote dilution under the Fourteenth Amendment (`App.19a–43a`). Appellants contend (`petition.txt` at 25–34) that this defies both the May 11, 2026 GVR order (which vacated the 2025 injunction notwithstanding its alternative constitutional ground) and *Abbott v. League of United Latin American Citizens*, 2026 WL 1127246 (U.S. Apr. 27, 2026), and *Alexander v. South Carolina State Conference of the NAACP*, 602 U.S. 1 (2024), because the panel inferred discriminatory intent chiefly from the 2023 Legislature's refusal to draw a second majority-Black district at the expense of Gulf Coast unity and incumbent protection—conduct that *Callais* holds is lawful and constitutionally required where race-based redistricting is not justified by a valid Section 2 showing.
3. **Equitable Discretion and *Purcell***: Appellants challenge the district court's issuance of an eleventh-hour preliminary injunction after the May 19, 2026 primaries (`petition.txt` at 34–37)—the exact ruling this Court already stayed on June 2, 2026 in *Allen II*, 146 S. Ct. 1377.

---

## 5. Weighing the Competing Dispositions at the Cert / Jurisdiction Stage

### A. Vacatur and Remand (`gvr`, P = 0.48) — Modal Outcome
Why is `gvr` ("Judgment VACATED and case REMANDED...") the single most probable disposition?
1. **Expiration of the 2026-Only Preliminary Injunction & *Munsingwear* Practice**: The order on appeal (`Singleton Doc. 363`, `App.77a`) is an interlocutory preliminary injunction whose operative relief applied **solely to the 2026 congressional elections**. Because this Court stayed that order on June 2, 2026 (*Allen II*, 146 S. Ct. 1377) and the 2026 general election took place on November 3, 2026 under the 2023 Plan, the preliminary injunction can no longer have any operative effect on the 2026 election cycle, while proceedings toward a final judgment for the 2028 cycle remain before the district court (`App.77a–78a`, ¶ 4). Under *United States v. Munsingwear, Inc.*, 340 U.S. 36, 39–40 (1950), *University of Texas v. Camenisch*, 451 U.S. 390, 394–98 (1981), and *Azar v. Garza*, 584 U.S. 726, 729 (2018) (per curiam), when an appeal from a preliminary injunction becomes moot through the passage of the election it governed (and not through the appellant's voluntary action), the Court's standard practice is to **vacate the preliminary-injunction order and remand** for further proceedings or with instructions to dismiss the preliminary-injunction request as moot.
2. **Convergence of Mootness Vacatur and Merits Vacatur under `gvr`**: Moreover, the six-Justice majority from *Callais* and *Allen II* has strong institutional reasons not to leave the three-judge panel's 78-page May 26, 2026 order standing unvacated as law of the case while the district court adjudicates permanent relief for 2028. Whether the Court enters a *Munsingwear* vacatur of the expired 2026 preliminary injunction or a merits vacatur-and-remand for further proceedings consistent with *Callais* and *Abbott v. LULAC*, both orders take the `"Judgment VACATED and case REMANDED..."` form, which resolves to `gvr` (`granted = 1`).
3. **Why the Post-Election Conference Hold Signals Vacatur/Remand**: Holding Nos. 26-116, 26-117, and 26-118 from the October 16, 2026 Conference until the November 6, 2026 Conference (three days after Election Day) and relisting them for November 13, 2026 strongly indicates the Court waited for the November 3, 2026 election to pass before disposing of the interlocutory 2026 preliminary-injunction appeals.

### B. Plenary Review (`granted` — Probable Jurisdiction Noted or Postponed, P = 0.22)
There is a substantial secondary probability (`0.22`) that at least four Justices (from the six-Justice *Callais* / *Allen II* majority) vote to note probable jurisdiction—or postpone consideration of jurisdiction/mootness to the hearing on the merits—to review the three-judge panel's post-*Callais* Fourteenth Amendment and Section 2 holdings directly. Because the panel relied on the full February 2025 bench-trial record (`App.16a–18a`) and indicated that the 2023 Plan remains unlawful under the Fourteenth Amendment and Section 2, Appellants argue that the controversy over the 2023 Plan remains live for the 2028 and 2030 elections (or falls within the "capable of repetition, yet evading review" exception). However, because no final judgment on remand has yet been entered and the May 26, 2026 order was strictly a 2026 preliminary injunction, full plenary briefing and oral argument on an expired interlocutory order is less likely than vacating and remanding so any further review occurs from a final judgment.

### C. Summary Reversal (`summary-reversal`, P = 0.08)
Appellants explicitly urge the Court to summarily reverse (`petition.txt` at 3, 12, 38). While several conservative Justices (especially Justices Thomas, Alito, and Gorsuch) may favor a summary reversal rebuking the panel's treatment of *Callais*, summary reversal of a preliminary injunction whose 2026 election target has already passed is procedurally awkward compared to a vacatur and remand (`gvr`).

### D. Dismissal Without Vacatur (`dismissed`, P = 0.21) and Summary Affirmance (`denied`, P = 0.01)
On the non-grant side (`P = 0.22` total):
- There is a `0.21` probability that the Court grants Appellees' September 18, 2026 Motion to Dismiss by entering a bare dismissal (`"The appeal is dismissed as moot."` or `"The appeal is dismissed for want of jurisdiction."`) without vacating the May 26, 2026 order. That probability is capped at `0.21` because under *Munsingwear* and *Camenisch*, an appellant who obtained a stay of an election-year preliminary injunction and saw the election pass is ordinarily entitled to vacatur of the unreviewed preliminary injunction rather than a bare dismissal that leaves the adverse order intact.
- Summary affirmance (`denied`) is assigned `0.01`, as the 6–3 Court just stayed the May 26, 2026 order in *Allen II* and vacated the prior permanent injunction in light of *Callais*.

---

## 6. Secondary Claims & Per-Justice Forecast

- **`disposition` (`0.78`)**: Matches top-level `probability`.
- **`summary-route` (`0.72`)**: Conditional on a grant-family outcome (`0.78`), the probability of a summary/order-list disposition (`gvr` at `0.48` + `summary-reversal` at `0.08` = `0.56`) rather than plenary review (`granted` at `0.22`) is `0.56 / 0.78 ≈ 0.72`.
- **`relist-increment` (`0.30`)**: At `distribution_count = 3` (Conference of November 13, 2026), most two-relist cases dispose at the upcoming conference, though a further relist (~30%) could occur if a Justice circulates a separate concurrence or dissent across the three companion dockets (`26-116`, `26-117`, `26-118`).
- **`cvsg-increment` (`0.01`)**: Near-zero on a relisted post-election direct appeal where the Court has already twice ruled on this exact litigation in May and June 2026.
- **`dissent-from-denial` (`0.75`)**: Conditional on `actual_disposition == "denied"` (which on a direct appeal requires a summary affirmance), it is highly likely (~75%) that at least one conservative Justice from the *Callais* majority would note a dissent.
- **`order-writers` & `votes`**: The six Justices in the *Callais* and *Allen II* majority (Roberts, Thomas, Alito, Gorsuch, Kavanaugh, Barrett) are predicted `for-relief` (favoring vacatur/remand, noting probable jurisdiction, or summary reversal rather than leaving the May 26, 2026 order undisturbed), while the three *Callais* and *Allen II* dissenters (Sotomayor, Kagan, Jackson) are predicted `against-relief`. Modest separate-writing probabilities are assigned, led by Justice Jackson (`0.14`, author of the June 2, 2026 *Allen II* stay dissent) and Justices Thomas and Alito (`0.12` each, authors of the *Callais* concurrence and majority opinion).
