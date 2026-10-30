# Rationale for Prediction (`reasoning.md`)

## 1. Summary of Numbers

- **`granted`**: `0` (`predicted_disposition`: `"denied"`)
- **`probability` / `disposition`**: `0.28`
- **`relist-increment`**: `0.98`
- **`cvsg-increment`**: `0.01`
- **`summary-disposition-route`**: `0.85` (conditional on grant)
- **`dissent-from-denial`**: `0.12` (conditional on denial)
- **`big_case_score`**: `0.55`

## 2. Provisioned Record and Procedural Posture

I read the provisioned snapshot `data/cases/scotus/9026000046/record/snapshots/2026-09-09.json`, `record/context.json`, `record/documents/documents.json`, `record/documents/questions-presented.txt`, and `record/documents/petition.txt` (full 80-page petition and appendix containing the Second Circuit's April 13, 2026 Summary Order and the Southern District of New York's March 20, 2025 Opinion & Order).

Key facts from the provisioned record as of the September 9, 2026 cutoff (`moment: response-requested`):
- Petitioners Nunzio Calce, Shaya Greenfield, and firearms-rights organizations (represented by Counsel of Record David H. Thompson of Cooper & Kirk, PLLC) challenge New York State's (N.Y. Penal Law § 265.01(1)) and New York City's (N.Y.C. Admin. Code § 10-135) complete prohibitions on the possession of electronic dart guns (tasers) and electronic stun guns.
- Both the SDNY (Judge Edgardo Ramos) and a Second Circuit panel (Judges Calabresi, Lohier, and Kahn, by unpublished Summary Order) ruled against Petitioners solely at *Bruen* step one. Relying on *United States v. Gomez*, 159 F.4th 172, 179–80 (2d Cir. 2025), the Second Circuit held that a plaintiff bears the threshold step-one burden to demonstrate that a banned weapon is "in common use today for self-defense," and concluded that Petitioners' four pieces of summary-judgment evidence (2018 testimony from *Maloney v. Singas*, a 2022 declaration that Axon had sold at least 461,000 Tasers to civilians, Axon's 2023 Form 10-K reporting net sales in dollars, and judicial notice of *Caetano v. Massachusetts*, 577 U.S. 411 (2016), and *Avitabile v. Beach*, 368 F. Supp. 3d 404 (N.D.N.Y. 2019)) were insufficient to establish how many tasers and stun guns are in civilian hands today. Neither court below reached *Bruen* step two.
- Respondent City of New York filed a waiver of its right to respond on August 6, 2026. Two cert-stage amicus briefs supporting Petitioners were filed on August 7, 2026 (Gun Owners of America et al.) and August 10, 2026 (Byrna Technologies, Inc. et al.).
- The petition was distributed on August 19, 2026, for the September 28, 2026 Long Conference (`distribution_count: 1`). On September 8, 2026, the Court requested a response (due October 8, 2026). Because the snapshot stops on the call day (`2026-09-09`), no brief in opposition is on the record yet.

## 3. Base-Rate Anchoring (`metrics/statpack.md`)

In `record/context.json`, this cell carries `band: "baseline"`, `salience_version: "sal-v4"`, `term: 2026`, `mode: "forward"`, and `decided_before: null`.

- **Primary Anchor (`baseline` band `[reached …]` rate):** Pooling the `baseline` `[reached …]` figures in `metrics/statpack.md` ("Segment base rate by salience band (sal-v4)") across the 9 rendered prior Terms (`T < 2026`, i.e., OT2017–OT2025), weighted by each Term's reached `n`, yields **5.1%** (`659.4 / 12,913` resolved weighted petitions; ranging from `4.0% (n=1314)` in OT2025 to `5.9%` in OT2022–OT2024 `n=1196, 1312, 1274`). The corresponding prior-Term pooled terminal `baseline` rate is **1.3%** (`123.7 / 9,774`; `1.0% (n=994)` in OT2025). The gap between the `1.3%` terminal rate and the `5.1%` reached rate reflects the petitions that began in `baseline` and later climbed into `elevated` or `high` via relists or a CVSG.
- **Contextual Statpack Cuts:**
  - **Relist count (paid scored segment):** `0` relists has a `1.8%` grant-family rate (`1.3%` granted + `0.5%` gvr, `n=10,203`); `1` relist has a `13.7%` grant-family rate (`8.5%` granted + `5.2%` gvr, `n=2,538`); `2` relists has a `41.2%` grant-family rate (`28.3%` granted + `12.9%` gvr, `n=495`); `3+` relists has a `37.4%` grant-family rate (`23.1%` granted + `14.3%` gvr, `n=484`).
  - **Amicus-brief count (paid scored segment):** Petitions with `2+` cert-stage amicus briefs (at disposition) have a `22.9%` grant-family rate (`18.4%` granted + `4.5%` gvr, `n=1,449`), compared to `15.1%` for `1` brief (`10.3%` granted + `4.8%` gvr, `n=1,162`) and `3.8%` for `0` briefs (`2.0%` granted + `1.8%` gvr, `n=11,109`).
  - **CVSG status (paid scored segment):** Petitions with no CVSG (`none`) have a `6.4%` grant-family rate (`4.1%` granted + `2.3%` gvr, `n=13,556`), while `cvsg` petitions have a `34.8%` grant-family rate (`29.3%` granted + `5.5%` gvr, `n=164`).
  - **Originating circuit (`ca2`):** In the modern cert petitions by originating circuit table (denial-reweighted), `ca2` has a `5.1%` grant-family rate (`2.7%` granted + `2.4%` gvr, `n=2,070`).

## 4. Adjustments from the Anchor (`P(grant) = 0.28`)

Starting from the `5.1%` prior-Term `baseline` `[reached]` base rate, several strong upward factors move my probability to `0.28`:

1. **The Call for a Response (`moment: response-requested`) and Guaranteed Second Distribution (+0.09):** After the City of New York waived its response on August 6, 2026, a Justice called for a response on September 8, 2026. Once the brief in opposition is filed, the petition will be distributed a second time, placing it in at least the `1`-relist (`elevated`) cohort (`13.7%` grant-family rate in the relist-count cut, `n=2,538`; prior-Term `elevated` reached rate ~`16.9%`).
2. **Direct Overlap with Pending OT2026 Merits Case *Viramontes v. Cook County*, No. 25-238 (+0.16):** Corpus lookup confirmed that on June 30, 2026, the Court granted certiorari in *Viramontes v. Cook County*, No. 25-238 (also litigated by Counsel of Record David H. Thompson of Cooper & Kirk, PLLC). *Viramontes* presents the threshold methodological question of whether *Heller* and *Bruen*'s "in common use" inquiry is a burden the plaintiff must satisfy at *Bruen* step one (plain text) or part of the government's historical burden at step two. That is the exact question presented by QP 1 in *Calce*, and both courts below disposed of *Calce* solely on step-one threshold grounds without reaching step two in the alternative. Because a GVR counts as a grant (`granted = 1`), the standard practice of holding a petition that turns on a threshold methodological rule pending an argued merits case addressing that rule—and GVR'ing if the merits decision alters or clarifies the lower court's framework—creates a substantial GVR pathway here.
3. **Prior SCOTUS Attention to Stun-Gun Bans (*Caetano*) and Cert Amicus Support (+0.04):** Two cert-stage amicus briefs are already on the docket (`2+` amicus bucket: `22.9%` grant-family rate, `n=1,449`), and in *Caetano v. Massachusetts*, 577 U.S. 411 (2016), the Court summarily vacated a decision upholding Massachusetts's stun-gun ban, with Justice Alito (joined by Justice Thomas) specifically noting that hundreds of thousands of tasers and stun guns are lawfully owned in 45 states and singling out New York's ban.
4. **Countervailing Vehicle Defects (-0.06):** Two significant vehicle problems prevent the grant/GVR probability from rising higher: (a) the Second Circuit decided *Calce* in a non-precedential Summary Order (applying its earlier published precedent in *United States v. Gomez*, 159 F.4th 172 (2d Cir. 2025)), and (b) both the district court and the Second Circuit emphasized that Petitioners built an unusually sparse summary-judgment record (only four items of evidence, none providing current civilian stun-gun ownership figures). When the City of New York files its brief in opposition, it will frame the decision below as a factbound failure of proof at summary judgment. Even if *Viramontes* clarifies the *Bruen* framework, there is a high chance (~72%) that the Court denies certiorari either after receiving the BIO or after deciding *Viramontes* because of the thin evidentiary record below.

## 5. Rationale for Auxiliary Claims and `order-writers`

- **`relist-increment` (`0.98`):** Although the harness masks `relist-increment` on `response-requested` cells because a further distribution after the response arrives is nearly automatic, I state `0.98` to reflect that absent a rare Rule 46 dismissal or withdrawal before the response is distributed, the petition is certain to be distributed again after the October 8, 2026 response due date.
- **`cvsg-increment` (`0.01`):** No federal statute, treaty, or federal agency program is involved in this challenge to New York State and New York City stun-gun bans, making a CVSG virtually impossible.
- **`summary-disposition-route` (`0.85`):** Conditional on a grant, a GVR in light of *Viramontes v. Cook County* (or a *Caetano*-style summary per curiam vacatur) is far more likely than setting a non-precedential Second Circuit summary order with a sparse factual record for plenary briefing and oral argument (`0.24 / 0.28 ≈ 0.85`).
- **`dissent-from-denial` (`0.12`) and `order-writers`:** Conditional on denial (`P(deny) = 0.72`), there is a `0.12` probability that at least one Justice authors a dissent from or statement respecting the denial of certiorari. Unconditionally, `0.72 × 0.12 = 0.0864`. Justice Thomas (`0.055`) and Justice Alito (`0.030`) are by far the likeliest authors given Justice Alito's concurrence in *Caetano* (joined by Justice Thomas) condemning stun-gun bans and Justice Thomas's frequent dissents from denial in post-*Bruen* Second Amendment cases, followed by Justice Gorsuch (`0.012`) and Justice Kavanaugh (`0.006`), with much smaller probabilities (`0.001`–`0.005`) for the remaining Justices.

## 6. Note on Upstream Retrieval

During retrieval, the CourtListener MCP `search` endpoint returned HTTP 429 rate-limit errors followed by an HTTP 502 Bad Gateway maintenance page. Per the prompt contract, I relied on the local/ranged corpus (`uv run fedcourts query`)—which successfully returned the docket records for *Viramontes v. Cook County* (No. 25-238), *Wolford v. Lopez* (No. 24-1046), *Snope v. Brown* (No. 24-203), and *Ocean State Tactical v. Rhode Island* (No. 24-131), as well as recent OT2026 grants and GVRs—together with the complete 80-page provisioned `petition.txt` and `metrics/statpack.md`.
