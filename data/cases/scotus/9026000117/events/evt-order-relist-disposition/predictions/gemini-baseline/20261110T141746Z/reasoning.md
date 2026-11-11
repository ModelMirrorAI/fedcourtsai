# Predictor Rationale: *Wes Allen, Alabama Secretary of State, et al. v. Evan Milligan, et al.* (No. 26-117)

## 1. Procedural Posture and Conditioning Snapshot (`2026-11-09.json`)

This forecast evaluates `evt-order-relist-disposition` (`moment: relist`, `stage: cert`) for *Wes Allen, Alabama Secretary of State, et al. v. Evan Milligan, et al.*, No. 26-117 (`scotus/9026000117`), conditioned on the `2026-11-09.json` docket snapshot and `record/context.json`.

- **Mandatory Appellate Jurisdiction (`28 U.S.C. § 1253`):** Unlike a discretionary petition for a writ of certiorari, No. 26-117 is a direct appeal via Jurisdictional Statement (filed July 22, 2026; docketed July 24, 2026) from the May 26, 2026 order of the three-judge U.S. District Court for the Northern District of Alabama (`2:21-cv-01530-AMM`, Judge Manasco, Circuit Judge Marcus, and Judge Moorer) preliminarily enjoining Alabama Secretary of State Wes Allen from conducting the 2026 congressional elections under Alabama's 2023 redistricting plan (SB5) and ordering use of the court-drawn Special Master Plan. Companion filings are pending simultaneously in *Allen v. Singleton*, No. 26-118 (`scotus/9026000118`, also a § 1253 Jurisdictional Statement from `2:21-cv-01291-AMM`) and *Allen v. Caster*, No. 26-116 (`scotus/9026000116`, a petition for a writ of certiorari before judgment to the Eleventh Circuit in `No. 26-11828`).
- **Distribution and Relist Sequence (`distribution_count = 3`):**
  1. Appellees Evan Milligan et al. filed a Motion to Dismiss or Affirm on September 18, 2026; Appellants waived the 14-day waiting period on September 28, 2026 and filed their Opposition to the Motion to Dismiss or Affirm on September 29, 2026.
  2. The appeal was first distributed on September 30, 2026 for the **October 16, 2026** Conference (three weeks before the November 3, 2026 general election).
  3. After taking no action at the October 16 Conference, the Court relisted the case on November 2, 2026 for the **November 6, 2026** Conference—the first Conference held *after* the **November 3, 2026 general election**.
  4. On November 9, 2026, the Court relisted No. 26-117 (along with Nos. 26-116 and 26-118) a second time for the **November 13, 2026** Conference (`distribution_count = 3`, `relist_count = 2`).

## 2. Base Rates and Corpus Priors Consulted

1. **Salience-Band Anchor (`context.cert_anchor`):**
   - `context.json` freezes `band: "high"` under `sal-v8` with `cert_anchor.rate = 0.3484455958549223` (34.84% grant-family rate across the 10-Term lookback window).
2. **Relist-Bucket Base Rate (`metrics/statpack.md`):**
   - In the paid scored segment of `statpack.md`, petitions in `relist_bucket = 2` (`distribution_count = 3`, `n = 495` resolved) resolve as: `denied 57.4%`, `granted 28.3%`, `gvr 12.9%`, `dismissed 1.4%`—a combined grant-family rate (`granted + gvr`) of **41.2%**.
3. **Directly Analogous Corpus Priors (`fedcourts query`):**
   - *Wes Allen v. Evan Milligan*, No. 25-274 (`scotus/73275213`), and *Wes Allen v. Bobby Singleton*, No. 25-273 (`scotus/73275215`): the immediately preceding § 1253 direct appeals from the same three-judge district court's May 8, 2025 permanent injunction (`782 F. Supp. 3d 1092`). On May 11, 2026, after `distribution_count = 2`, the Supreme Court vacated the injunctions and remanded for further consideration in light of *Louisiana v. Callais*, 608 U.S. ___ (2026)—resolving in the corpus as `disposition: "gvr"` (`granted = 1`).
   - *Louisiana v. Callais*, No. 24-109 (`scotus/69779623`): § 1253 direct appeal from a three-judge district court redistricting injunction where the Court noted probable jurisdiction after `distribution_count = 3` (`disposition: "granted"`) and affirmed on April 29, 2026 (`146 S. Ct. 1131`).
   - *Benancio Garcia, III v. Steven Hobbs*, No. 25-901 (`scotus/73280412`), and *Jose A. Trevino v. Steven Hobbs*, No. 25-918 (`scotus/73280426`): VRA § 2 redistricting appeals resolved on October 5, 2026 after 2–3 distributions via vacatur and remand (`disposition: "gvr"`).

## 3. Substantive and Procedural Analysis Driving the Forecast

Two converging features of No. 26-117 push the binary grant-family probability (`P(granted == 1)`) far above the 34.8% `high`-band base rate and 41.2% two-relist base rate, to **0.88**, with **`gvr`** as the modal `predicted_disposition`:

### A. The Supreme Court Already Rejected the May 26, 2026 Preliminary Injunction on the Merits (`Allen v. Milligan`, 146 S. Ct. 1377 (June 2, 2026))

Following the Supreme Court's May 11, 2026 vacatur of the May 8, 2025 permanent injunction in *Allen v. Caster*, 608 U.S. ___, 146 S. Ct. 1196 (2026), the three-judge district court conducted expedited proceedings and on May 26, 2026 entered a third preliminary injunction barring use of the 2023 Plan for the 2026 congressional elections (`App.1a–110a`). Six days later, on **June 2, 2026**, the Supreme Court granted Alabama's emergency stay application in a published 6–3 Per Curiam opinion (*Allen v. Milligan*, No. 25A1314, 608 U.S. ___, 146 S. Ct. 1377 (2026), over a dissent by Justice Sotomayor joined by Justices Kagan and Jackson).

In that Per Curiam opinion, the Court expressly held that **"The State is likely to succeed on the merits as to both claims"**:
1. On the Fourteenth Amendment intentional vote-dilution claim (asserted in *Singleton* and *Milligan*), the Court held that the District Court "did not heed the presumption of legislative good faith, see *Alexander v. South Carolina State Conference of the NAACP*, 602 U.S. 1, 10 (2024), because it interpreted the State's legal disagreement with the court's earlier remedial order as proof of discriminatory animus."
2. On the VRA § 2 claim, the Court held that "the District Court's analysis departed from *Callais*" because under *Callais* a district court must deny relief unless the plaintiffs' alternative map performs "just as well" with respect to *all* of the State's constitutionally permissible districting criteria (including keeping together the Gulf Coast community of interest in Mobile and Baldwin Counties and avoiding the pairing of incumbents), and because the District Court failed to require an analysis controlling for partisan affiliation on the second and third *Gingles* preconditions.

Because a six-Justice majority has already held in a published Per Curiam opinion that the May 26, 2026 order rests on legal error under *Callais* and *Alexander*, the probability that the Court grants Appellees' motion to affirm (`denied`) is negligible (~**0.01**).

### B. Convergence of the Post-Election Mootness (*Munsingwear*) Path and the Merits Path onto `granted = 1` (and Specifically `gvr`)

Critically, the operative remedial order of the May 26, 2026 Preliminary Injunction (`Milligan Doc. 537` at 77; `App.5a, 108a`) was expressly limited to the **2026 congressional elections**:
> "1. The Court PRELIMINARILY ENJOINS the Alabama Secretary of State from conducting the **2026 congressional elections** according to the 2023 Plan.
> 2. The Court further ORDERS the Alabama Secretary of State to administer all remaining events comprising Alabama's **2026 congressional elections** according to the Special Master Plan..."

Meanwhile, the District Court reserved permanent-injunction proceedings for a bench trial to be ready by January 11, 2027 (subsequently paused pending this appeal per `Milligan Doc. 544`, July 20, 2026).

Because the Supreme Court stayed the May 26, 2026 preliminary injunction on June 2, 2026, Alabama held its special primary on August 11, 2026 and its **general election on Tuesday, November 3, 2026** under the 2023 Plan. The Court's conference schedule tracks this exact calendar: after first distributing No. 26-117 for the October 16, 2026 Conference, the Court held/relisted it across the election to the **November 6, 2026** Conference (three days after the November 3 general election), and then relisted it once more on November 9, 2026 for the **November 13, 2026** Conference.

At the November 13, 2026 Conference (or after any brief further relist), the Court faces three primary disposition options, **all three of which resolve to `granted = 1` on the binary axis**:

1. **Vacatur and Remand (`gvr`, P = 0.65):**
   - **Mootness (*Munsingwear*) Vacatur:** Because the 2026 congressional elections have now been completed under the Court's June 2, 2026 stay, the preliminary injunction governing only the 2026 elections is moot. Under *United States v. Munsingwear, Inc.*, 340 U.S. 36, 39 (1950), when an order under appellate review becomes moot before appellate disposition, the established practice of the Court is to vacate the order below and remand for further proceedings (or with instructions to dismiss the preliminary-injunction motions for the 2026 election as moot).
   - **Merits Vacatur and Remand:** Alternatively (or in combination), the Court can summarily vacate the May 26, 2026 order and remand for further proceedings consistent with *Louisiana v. Callais*, 608 U.S. ___ (2026), *Abbott v. League of United Latin American Citizens*, 607 U.S. ___ (2026), and *Allen v. Milligan*, 608 U.S. ___, 146 S. Ct. 1377 (2026)—mirroring the May 11, 2026 vacatur order in No. 25-274.
   - Under `schemas/prediction.schema.json`, **both** a *Munsingwear* vacatur-and-remand and a merits vacatur-and-remand on a direct appeal resolve to `predicted_disposition = "gvr"` and `granted = 1`.
2. **Probable Jurisdiction Noted / Postponed to the Merits (`granted`, P = 0.17):**
   - In their Jurisdictional Statement (`petition.txt` at 35–36) and Opposition to the Motion to Dismiss or Affirm, Appellants urge the Court to note probable jurisdiction (or summarily reverse) so that the three-judge district court does not enter a fourth injunction after the scheduled January 2027 permanent-injunction trial. If four Justices vote to note probable jurisdiction (finding the controversy capable of repetition yet evading review or still live as to ongoing relief), the order noting probable jurisdiction resolves to `predicted_disposition = "granted"` and `granted = 1`.
3. **Per Curiam Summary Reversal (`summary-reversal`, P = 0.06):**
   - Because the Court has already issued a detailed Per Curiam merits analysis in the June 2, 2026 stay opinion (`146 S. Ct. 1377`) and has now relisted the case twice (`distribution_count = 3`), there is a modest probability (~6%) that the Court summarily reverses the May 26, 2026 preliminary injunction outright (`summary-reversal`, which also maps to `granted = 1`).
4. **Non-Grant Dispositions (`dismissed` P = 0.11, `denied` P = 0.01; total `P(granted == 0) = 0.12`):**
   - The only plausible path to `granted = 0` is if the Court grants Appellees' motion to dismiss the appeal as moot *without* vacating the May 26, 2026 preliminary injunction (`dismissed`, ~11%). While appellate courts occasionally dismiss an appeal from an expired preliminary injunction as moot without vacatur because a preliminary injunction lacks preclusive effect, the Supreme Court's standard practice where it stayed the injunction pending appeal—and where the 158-page opinion below would otherwise guide further proceedings in the same case—strongly favors vacatur and remand (`gvr`) over a naked dismissal.

Summing the grant-side dispositions yields **`probability = 0.88`** (`0.65 + 0.17 + 0.06`), **`granted = 1`**, and **`predicted_disposition = "gvr"`**.

## 4. Mechanical Secondary Claims and Order-Writers Distribution

- **`relist-increment` (`0.35`):** Across the paid scored segment in `metrics/statpack.md`, 49.4% of petitions reaching 2 relists (`483 / 978`) receive a 3rd+ relist. Here, however, the first relist (from October 16 to November 6, 2026) served the specific calendar purpose of holding the appeal past the November 3, 2026 general election, making the November 9 relist (to November 13, 2026) the first post-election conference relist. A routine vacatur-and-remand order after a post-election check will issue on the November 16, 2026 order list without another relist; a further relist (~35% probability) would occur primarily if a Justice is circulating a separate concurrence or dissent or if the Court is drafting a per curiam opinion across Nos. 26-116, 26-117, and 26-118.
- **`cvsg-increment` (`0.005`):** The United States already entered an appearance in the District Court (`Milligan Doc. 546`), and the Court never invites the Solicitor General to file an amicus brief on a time-sensitive direct appeal from a preliminary injunction that the Court has already stayed on the merits.
- **`order-writers`:** In both the May 11, 2026 vacatur (*Allen v. Caster*, 146 S. Ct. 1196) and the June 2, 2026 stay (*Allen v. Milligan*, 146 S. Ct. 1377), **Justice Sotomayor** authored a dissenting opinion joined by Justices Kagan and Jackson. If the Court vacates on the merits or summarily reverses (rather than issuing a one-sentence *Munsingwear* vacatur), Justice Sotomayor is the most likely separate writer (`0.08`), followed by **Justice Thomas** (`0.05`, who concurred separately in *Callais*), **Justice Alito** (`0.03`), and **Justice Kavanaugh** (`0.03`), with lower probabilities for **Justice Jackson** (`0.025`), **Justice Gorsuch** (`0.02`), **Justice Kagan** (`0.015`), **Justice Barrett** (`0.01`), and **Chief Justice Roberts** (`0.005`).
