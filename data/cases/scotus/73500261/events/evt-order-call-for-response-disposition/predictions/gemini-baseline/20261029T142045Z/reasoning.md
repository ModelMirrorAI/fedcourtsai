# Prediction Reasoning: *Cade Brumley, Superintendent, Louisiana State Education, et al. v. Darcy Roake, et al.* (No. 25-1360)

**Event:** `evt-order-call-for-response-disposition` (`moment: response-requested`, `stage: cert`)  
**Input Snapshot:** `2026-07-28.json` (`cutoff: 2026-07-29`, `cut_kind: date`, `mode: forward`)  
**Predicted Disposition:** `denied` (`granted: 0`, `probability: 0.14`, `confidence: 0.78`, `big_case_score: 0.85`)

---

## 1. Case Posture and Provisioned Filings

From `2026-07-28.json` and the provisioned filings in `record/documents/` (`questions-presented.txt`, `petition.txt`, and `appendix.txt`), this petition arises from Louisiana's 2024 enactment of H.B. 71, which requires public school classrooms to display the Ten Commandments alongside a statutory historical context statement, while specifying that school boards need not spend public funds and may rely on donated displays. Before any display was erected or implementing regulations were promulgated by the State Board of Elementary and Secondary Education (BESE), parent plaintiffs (Darcy Roake et al.) brought a facial Establishment Clause and Free Exercise Clause challenge.

The Middle District of Louisiana denied the State Defendants' Rule 12(b)(1) and 12(b)(6) motions and entered a preliminary injunction barring enforcement of H.B. 71 (App. C), and a Fifth Circuit panel initially affirmed (App. B). The Fifth Circuit then granted rehearing en banc and heard the case alongside *Nathan v. Paxton*, a parallel challenge to Texas's S.B. 10. On April 21, 2026, the en banc Fifth Circuit issued two contrasting rulings:
- **In *Roake v. Brumley* (App. A):** A 12-6 en banc majority (per Judge Ho) **vacated the preliminary injunction and remanded with instructions to dismiss the complaint without prejudice** for lack of Article III ripeness, holding that because H.B. 71 does not require school districts to spend public funds and no displays have been selected or posted, Plaintiffs' pre-enforcement claims rest on contingent future events. Separate concurrences by Judges Ho, Oldham, and Elrod argued that H.B. 71 is also constitutional on the merits under *Kennedy v. Bremerton School District*, 597 U.S. 507 (2022), *Van Orden v. Perry*, 545 U.S. 677 (2005), and *American Legion v. American Humanist Ass'n*, 588 U.S. 29 (2019), while six dissenting judges would have reached the merits and affirmed the injunction under *Stone v. Graham*, 449 U.S. 39 (1980).
- **In *Nathan v. Paxton* (App. D; note that the bulk of Appendix D after PDF page 177 was omitted under the 150,000-character pipeline cap, though `petition.txt` and App. A summarize its holding in detail):** An 11-7 en banc majority held the Texas challenge justiciable and **affirmed** the preliminary injunction against Texas's S.B. 10, holding that *Stone v. Graham* remains binding Supreme Court precedent under *Agostini v. Felton*, 521 U.S. 203 (1997).

After the *Roake* plaintiffs obtained an extension of time to August 19, 2026 to file a petition for certiorari (`No. 25A1239`), the Louisiana State Officials (Brumley et al., represented by Louisiana Solicitor General J. Benjamin Aguinaga) filed this **Conditional Petition for a Writ of Certiorari** (`No. 25-1360`) on June 8, 2026. Respondents waived a response on July 6, 2026; the petition was distributed on July 22, 2026 for the September 28, 2026 Long Conference; and on July 28, 2026, the Court called for a response (due August 27, 2026).

Crucially, **Petitioners won the judgment below** (vacatur of the preliminary injunction and remand for dismissal without prejudice) and explicitly ask the Court **not** to grant review unless the Court grants the *Roake* plaintiffs' forthcoming petition or a petition in the parallel Texas case (Pet. 3-5, 20-21).

---

## 2. Base-Rate Anchoring (`sal-v4`, `band: state`)

In `record/context.json`, the cell's frozen conditioning state is:
- `band: "state"`, `salience_version: "sal-v4"`, `term: 2025`, `distribution_count: 1`, `cvsg_date: null`, `signals_observable: true`.
- The snapshot shows `0` amicus briefs docketed as of `2026-07-28` (in `metrics/statpack.md`, the paid scored segment's `0`-amicus bucket has a `3.8%` grant-family rate [`2.0%` granted, `1.8%` GVR, `n=11109`], `1` amicus has `15.1%` [`n=1162`], and `2+` amici has `22.9%` [`n=1449`], though amicus counts are measured at disposition rather than at the CFR moment).

Following the prompt's anchoring rule for `moment: response-requested`, I anchor on the **bracketed `reached`** rate for the `state` band in `metrics/statpack.md` (*Segment base rate by salience band (sal-v4)*) pooled over the Terms **strictly preceding** `term: 2025` (i.e. OT2017–OT2024, the 8 strictly prior Terms rendered in the table):
- **OT2024:** `31.6%` (`n=38`, ~12.0 grants)
- **OT2023:** `18.8%` (`n=32`, ~6.0 grants)
- **OT2022:** `13.9%` (`n=36`, ~5.0 grants)
- **OT2021:** `22.7%` (`n=97`, ~22.0 grants)
- **OT2020:** `41.3%` (`n=46`, ~19.0 grants)
- **OT2019:** `17.0%` (`n=53`, ~9.0 grants)
- **OT2018:** `23.8%` (`n=42`, ~10.0 grants)
- **OT2017:** `21.6%` (`n=51`, ~11.0 grants)

Pooling across OT2017–OT2024 gives `94 / 395` = **23.8%** (`reached` risk-set grant-family rate for the `state` band). As a cross-check, in the paid scored segment (`metrics/statpack.md`), `relist_bucket = 0` (`distribution_count = 1`) has a `1.8%` grant-family rate (`1.3%` granted, `0.5%` GVR, `n=10203`), `relist_bucket = 1` has `13.7%` (`8.5%` granted, `5.2%` GVR, `n=2538`), `cvsg = none` has `6.4%` (`4.1%` granted, `2.3%` GVR, `n=13556`), and `ca5` in the modern cert table has `3.8%` (`1.7%` granted, `2.1%` GVR, `n=5399`).

---

## 3. Case-Specific Adjustments from the 23.8% Anchor

Starting from the **23.8%** `state`-band `reached` anchor, I adjust downward to **14.0% (`0.14`)** for the following reasons:

1. **Why the Call for a Response (CFR) Does Not Strongly Increase `P(grant)` Here:**
   Normally, a Call for a Response on a `state` petition after a respondent's waiver is a positive signal that at least one chambers wants full briefing. Here, however, the CFR is primarily a matter of routine docket coordination: the *Roake* plaintiffs had already sought and received an extension until August 19, 2026 (`No. 25A1239`) to file their own petition challenging the Fifth Circuit's vacatur of their preliminary injunction, and Texas's petition in *Paxton v. Nathan* arises from the companion en banc decision issued the same day. Calling for a response in No. 25-1360 (due August 27, 2026) simply ensures that both sides' filings in *Roake* are briefed on a parallel timeline rather than leaving No. 25-1360 unbriefed at the Long Conference.

2. **Substantial Downward Adjustment for Prevailing-Party / Conditional Cross-Petition Posture:**
   Unlike the typical `state`-band petition—where a State Solicitor General seeks review of an adverse circuit judgment invalidating a state law or granting habeas/injunctive relief—**Louisiana won in the en banc Fifth Circuit**. The en banc court vacated the preliminary injunction against H.B. 71 and remanded with instructions to dismiss the complaint without prejudice. Under *Camreta v. Greene*, 563 U.S. 692, 700 (2011), the Court's settled practice is to decline certiorari petitions filed by prevailing parties seeking only a more favorable ground of dismissal (here, dismissal with prejudice on the First Amendment merits rather than dismissal without prejudice on Article III ripeness). Moreover, Petitioners themselves explicitly urge the Court *not* to grant review at this stage unless it grants Respondents' petition or the Texas case.

3. **Vehicle Comparison with *Paxton v. Nathan* and the *Roake* Plaintiffs' Petition:**
   - If the Court wishes to address whether *Stone v. Graham* should be overruled under *Kennedy v. Bremerton School District*, the companion Texas case (*Paxton v. Nathan*) is a clean, non-conditional vehicle in which the en banc Fifth Circuit held the dispute ripe, applied *Stone v. Graham* on the merits, and affirmed a preliminary injunction against the State of Texas.
   - Even if the Court wishes to review the Louisiana statute specifically (or the Fifth Circuit's ripeness holding), the *Roake* plaintiffs' forthcoming petition (`25A1239`) is the direct challenge to the Fifth Circuit's judgment vacating the injunction.
   - Thus, `25-1360` would only be granted (~14% probability) if the Court decides to grant the *Roake* plaintiffs' petition (or *Paxton v. Nathan*) **and** decides either to grant `25-1360` alongside it to ensure Question Presented 2 (the facial First Amendment merits of H.B. 71) is formally before the Court, or eventually disposes of `25-1360` via a GVR after resolving a companion case.

---

## 4. Rationale for Mechanical Claims (`cert-v3`) and `big_case_score`

- **`disposition` (`0.14`):** Equal to top-level `probability = 0.14`.
- **`relist-increment` (`0.95`):** At `moment: response-requested`, the snapshot shows `distribution_count: 1` (the pre-CFR July 22, 2026 distribution for the September 28, 2026 conference). As noted in the prompt (`on a response-requested cell relist-increment is all but certain (the petition is distributed again once the response is in or its time runs out), so the harness masks it too`), once the response arrives on or after August 27, 2026, the petition will be distributed for a subsequent conference, raising `distribution_count` to at least 2 (plus likely additional relists to coordinate with the *Roake* plaintiffs' petition and *Paxton v. Nathan*). I set `relist-increment` at `0.95`.
- **`cvsg-increment` (`0.005`):** A CVSG is virtually unheard of on a conditional state Establishment Clause petition with no federal statutory or regulatory nexus.
- **`summary-disposition-route` (`0.12`):** Conditional on `disposition` resolving to a grant, plenary review (consolidating `25-1360` with the *Roake* plaintiffs' petition or *Paxton v. Nathan*) accounts for ~88% of the grant probability mass, while ~12% reflects the possibility of a GVR if the Court holds `25-1360` pending a companion merits decision.
- **`dissent-from-denial` (`0.15`) & `order-writers`:** Conditional on a denial, there is a ~15% probability that one or more Justices (most likely Justice Thomas `0.09`, Justice Alito `0.09`, or Justice Gorsuch `0.08`, with smaller probabilities for Justice Kavanaugh `0.03`, Justice Sotomayor `0.02`, Justice Jackson `0.02`, and `0.01` for Chief Justice Roberts and Justices Kagan and Barrett) author a dissent from or statement respecting the denial of certiorari—particularly if the Court denies review in the *Roake*/*Nathan* litigation or leaves the Fifth Circuit's ripeness holding in place while declining to reach *Stone v. Graham*.
- **`big_case_score` (`0.85`):** Decoupled from grant probability, the substantive stakes of this dispute—whether public schools may display the Ten Commandments in every classroom and whether *Stone v. Graham* remains good law after *Kennedy v. Bremerton School District*—are extraordinarily high and nationally salient (`0.85`).
