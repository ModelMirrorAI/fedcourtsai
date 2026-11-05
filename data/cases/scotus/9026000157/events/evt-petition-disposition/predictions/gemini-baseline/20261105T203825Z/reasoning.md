# Certiorari Prediction Rationale: *Jasvinder Singh, et al. v. Second Judicial District Court of Nevada, Washoe County, et al.* (No. 26-157)

## Summary of Forecast Numbers

- **Top-level `granted` / `probability` / `predicted_disposition`:** `0` / `0.16` / `"denied"`
- **Declared `claims`:**
  - `disposition`: `0.16`
  - `relist-increment`: `0.96`
  - `cvsg-increment`: `0.02`
  - `summary-disposition-route`: `0.06`
  - `dissent-from-denial`: `0.10`
- **Declared `claim_distributions` (`order-writers`):** `Alito: 0.05`, `Thomas: 0.04`, `Gorsuch: 0.04`, `Kavanaugh: 0.015`, `Barrett: 0.01`, `Roberts: 0.005`, `Sotomayor: 0.005`, `Kagan: 0.005`, `Jackson: 0.005`
- **`big_case_score`:** `0.55`

---

## 1. Base-Rate Anchor and Docket Signals

### Corpus Base-Rate Anchor
In `record/context.json`, this cell is provisioned in `forward` mode with `band = "baseline"` (`sal-v7`), `distribution_count = 1`, and a pre-computed 10-Term risk-set anchor of **`cert_anchor.rate = 0.0515`** (5.15%), pooling the bracketed `[reached]` grant-family rate for paid `baseline` petitions across OT2017–OT2025 in `metrics/statpack.md`. In the originating-court table, petitions from the Nevada Supreme Court (`nev`, `n=20` resolved in the modern discretionary-cert slice) have a `100.0% denied` base rate, and state high courts generally grant at low single-digit rates.

### Upward Docket Trajectory Signals in `2026-11-05.json`
While `record/context.json` reflects `amicus_briefs: null` and `response_requested: null` (leaving the frozen band at `baseline`), the provisioned snapshot `2026-11-05.json` shows several strong upward indicators that move our probability well above the 5.15% `baseline` anchor:

1. **Supreme Court Specialist Counsel on Both Sides:** Petitioners are represented by Tobias S. Loss-Eaton (Sidley Austin LLP) and Jeffrey T. Green (Northwestern Supreme Court Clinic). After the Court called for a response, Respondents brought in Paul Whitfield Hughes (McDermott Will & Schulte LLP) to lead the opposition alongside their Nevada counsel (Holland & Hart LLP).
2. **Three Cert-Stage Amicus Briefs:** Three amicus briefs supporting Petitioners were filed before initial distribution:
   - *Anglican Church in North America* (Jones Day, Aug. 26, 2026);
   - *Former EEOC General Counsel Sharon Fast Gustafson and Rachel N. Morrison* (Hunton Andrews Kurth LLP, Sept. 2, 2026); and
   - *The Roman Catholic Archbishop of Las Vegas and His Successors* (Vinson & Elkins LLP, Sept. 2, 2026).
   In `metrics/statpack.md` ("Cert petitions by amicus-brief count (paid scored segment)"), the `2+` cert-amicus bucket (`n=1446` resolved) has a **22.7% grant-family rate** (`granted 18.2%, gvr 4.5%, denied 76.1%, dismissed 1.2%`), compared to 3.8% (`granted 2.0%, gvr 1.8%`, `n=11109`) for 0 amici and 14.8% (`granted 10.1%, gvr 4.7%`, `n=1158`) for 1 amicus. (In the salience-band table, `elevated` petitions—which `3` amici and a CFR correspond to once indexed—have a 10-Term `[reached]` grant-family rate of roughly 21–28%.)
3. **Call for a Response (CFR) After Waiver:** Respondents waived a response on August 21, 2026. The petition was distributed on September 16, 2026, for the October 9, 2026 Long Conference, and on September 22, 2026, the Court requested a response (extended on October 13, 2026, to November 23, 2026). A CFR demonstrates that at least one chambers flagged the petition as warranting full briefing.

However, as of November 5, 2026, **the Brief in Opposition has not yet been filed** and the petition has not yet been redistributed or relisted after a BIO (`distribution_count = 1`, where `relist_bucket = 0` in the statpack has a 1.8% terminal grant-family rate over `n=10204` resolved, and `relist_bucket = 1` has a 13.5% grant-family rate over `n=2532` resolved). Conditional on being at the post-CFR / pre-BIO stage with three amicus briefs, the majority of petitions are still denied once the BIO exposes vehicle and factual problems.

---

## 2. Substantive Split vs. Recent Cert Denials

### The Alleged Conflict
Reading `record/documents/questions-presented.txt`, `petition.txt`, and `appendix.txt`, Petitioners challenge the Nevada Supreme Court's published opinion in *Singh v. Second Judicial District Court*, 586 P.3d 858 (Nev. Apr. 2, 2026) (App. 1a–16a). The Nevada Supreme Court explicitly acknowledged a split of authority (App. 10a–13a) and joined the Ninth Circuit (*Puri v. Khalsa*, 844 F.3d 1152 (9th Cir. 2017); *Huntsman v. Corp. of the President of the Church of Jesus Christ of Latter-day Saints*, 127 F.4th 784 (9th Cir. 2025) (en banc)), Second Circuit (*Belya v. Kapral*, 45 F.4th 621 (2d Cir. 2022)), D.C. Circuit (*O'Connell v. U.S. Conference of Catholic Bishops*, 134 F.4th 1243 (D.C. Cir. 2025)), and Kentucky Supreme Court (*Kant v. Lexington Theological Seminary*, 426 S.W.3d 587 (Ky. 2014)) in holding that the "neutral principles of law" approach of *Jones v. Wolf*, 443 U.S. 595 (1979), applies beyond real-property ownership disputes so long as the dispute can be resolved without deciding religious doctrine, practice, or texts. Petitioners contrast those decisions with the Fifth Circuit (*Lutheran Church—Missouri Synod v. Christian*, 178 F.4th 193 (5th Cir. June 4, 2026); *McRaney v. North American Mission Board*, 157 F.4th 627 (5th Cir. 2025)), Sixth Circuit (*Hutchison v. Thomas*, 789 F.2d 392 (6th Cir. 1986)), Eleventh Circuit (*Crowder v. Southern Baptist Convention*, 828 F.2d 718 (11th Cir. 1987)), and Oklahoma Supreme Court (*Oklahoma Annual Conf. of the United Methodist Church, Inc. v. Timmons*, 2023 OK 101).

### Recent Denials on the Same Issue
Despite this tension—and separate opinions by several circuit judges urging Supreme Court clarification—the Court has repeatedly denied certiorari on this issue, including in *Belya v. Kapral*, 143 S. Ct. 2609 (2023), and, most notably, in ***United States Conference of Catholic Bishops v. O'Connell*, No. 25-849** (corpus id `scotus/73280351`), which was **denied on May 26, 2026, after 4 distributions** despite more than a dozen cert-stage amicus briefs (including briefs from two of the same amici supporting Petitioners here: the Anglican Church in North America and Sharon Fast Gustafson / Rachel N. Morrison). While Petitioners argue that No. 26-157 avoids the federal collateral-order jurisdiction question that complicated *O'Connell* and *Belya* (Pet. 28–30), No. 26-157 has serious posture and vehicle problems of its own.

---

## 3. Vehicle and Finality Obstacles

When Respondents file their Brief in Opposition (authored by Paul Hughes), three major vehicle defects will weigh strongly against a grant:

1. **Interlocutory Pleading-Stage Posture and 28 U.S.C. § 1257(a) Finality:**
   The Nevada Supreme Court's decision denied an extraordinary writ of prohibition following the trial court's denial of a Rule 12 motion to dismiss (App. 2a, 6a). Even if Petitioners argue that the denial of an original writ of prohibition in Nevada is formally a standalone proceeding under *Atlantic Richfield Co. v. Christian*, 590 U.S. 1 (2020), or satisfies *Cox Broadcasting Corp. v. Cohn*, 420 U.S. 469 (1975), the Nevada Supreme Court expressly emphasized the preliminary, pleading-stage nature of its ruling:
   - *"In other words, nothing in the relevant sections of NNSS's bylaws or the claims alleged would—**as it appears at this point in the proceedings**—require the district court to evaluate Sikh doctrine, practices, or texts."* (App. 15a.)
   - *"At this juncture, the claims presented in RPIs' underlying complaint appear to be secular in nature..."* (App. 15a.)
   Because the Nevada courts have not foreclosed applying ecclesiastical abstention if discovery or summary-judgment briefing reveals an actual doctrinal controversy, both § 1257(a) finality and prudential ripeness are serious hurdles.

2. **Religious Membership Qualifications Are Undisputed Below:**
   The Question Presented asks whether a civil court may decide an internal governance dispute *"under organizational documents that define membership and authority in religious terms."* Yet the Nevada Supreme Court specifically observed that **"[t]he parties also do not contest whether the Management Defendants meet the religious eligibility requirements for the disputed Management Committee positions or to be considered general members of NNSS"** (App. 14a). Rather, the complaint (App. 39a–60a) alleges secular corporate-procedure breaches under NRS 82.216(1): (a) forming subcommittees to transfer the Temple property into a trust without a general-member vote, (b) failing to issue membership cards and maintain membership rolls, and (c) refusing to allow members to inspect corporate accounting books and records (App. 3a–4a, 14a–15a).

3. **Direct Entanglement with Church Real Property:**
   Although the petition frames this case as extending *Jones v. Wolf* "beyond the property-ownership context," the Nevada Supreme Court opened its opinion by noting that *"general members sought relief from a Nevada court after the organization's managers sought to transfer property rights in alleged violation of its bylaws"*—namely, transferring the Sikh Temple of Reno out of the nonprofit corporation (NNSS) and into a separate trust despite Article One of the recorded 2009 Bylaws stating that NNSS's assets *"are vested in general body (Sikh Sangat as a whole) of the State of Nevada and remain to be that forever"* (App. 2a–4a, 18a). Respondents will persuasively argue that a suit to prevent unauthorized alienation of the physical temple property in violation of an express vesting clause in recorded corporate bylaws is at its core a church-property dispute where *Jones v. Wolf* already applies.

Weighing the upward signals (CFR, 3 amicus briefs, elite counsel, active circuit split) against the pre-BIO posture, the recent denial in *O'Connell*, and the interlocutory/fact-bound vehicle flaws yields **`probability = 0.16`** (`predicted_disposition = "denied"`).

---

## 4. Rationale for Declared Claims, `order-writers`, and `big_case_score`

- **`disposition` (`0.16`):** Matches top-level `probability` (`0.15` plenary grant + `0.01` GVR).
- **`relist-increment` (`0.96`):** The snapshot records `1` distribution (`Sep 16 2026`), followed by `Response Requested` (`Sep 22 2026`, extended to `Nov 23 2026`). Under Supreme Court practice, once a requested BIO is filed (or the deadline passes), the petition is redistributed for conference. The only scenario in which the distribution count does not rise past 1 is a Rule 46 dismissal/settlement before post-BIO distribution (~4%).
- **`cvsg-increment` (`0.02`):** In the statpack, CVSGs occur in only `180 / 14180` (~1.3%) of paid scored-segment petitions (`n=164` resolved with CVSG vs. `n=13549` without). Here, the dispute involves state corporate law and the First Amendment with no federal statutory or regulatory hook, making a CVSG very unlikely (`0.02`).
- **`summary-disposition-route` (`0.06`):** Conditional on a grant, summary reversal is unlikely given the deep doctrinal split, but there is a small (~6% conditional) chance of a GVR if the Court grants another church-autonomy vehicle first.
- **`dissent-from-denial` (`0.10`) and `order-writers`:** Because the petition drew a CFR and three amicus briefs on a First Amendment church-autonomy issue, there is a ~10% conditional chance on denial that one or more conservative Justices (most plausibly Justice Alito at `0.05`, Justice Thomas at `0.04`, or Justice Gorsuch at `0.04`, with smaller probabilities for Justice Kavanaugh at `0.015`, Justice Barrett at `0.01`, and `0.005` each for Chief Justice Roberts and Justices Sotomayor, Kagan, and Jackson) author a dissent from or statement respecting the denial of certiorari.
- **`big_case_score` (`0.55`):** If decided on the merits, a Supreme Court ruling delineating the boundary between the church-autonomy doctrine and the *Jones v. Wolf* neutral-principles approach would be a significant First Amendment precedent governing religious nonprofits, schools, and denominations nationwide, though less sweeping in public salience than major constitutional cases involving federal statutes or nationwide government mandates.
