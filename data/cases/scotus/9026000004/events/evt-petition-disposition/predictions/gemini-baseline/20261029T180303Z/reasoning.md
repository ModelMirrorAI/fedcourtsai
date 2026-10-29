# Predictor Rationale: *Samsung Electronics America, Inc. v. Jordan Brewer* (No. 26-4)

## Summary of Forecast
- **Predicted Disposition:** `denied` (`granted: 0`, `probability: 0.03`)
- **Claims (`cert-v3`):** `disposition: 0.03`, `relist-increment: 0.12`, `cvsg-increment: 0.005`, `summary-disposition-route: 0.10`, `dissent-from-denial: 0.02`
- **Big-Case Score:** `0.45`

## Inputs Consulted
1. **Provisioned Snapshot (`2026-10-29.json`) and Conditioning Context (`context.json`):**
   - `mode: "forward"`, `band: "elevated"`, `salience_version: "sal-v4"`, `distribution_count: 2`, `cvsg_date: null`, `term: 2026`.
   - Docket proceedings show a paid petition filed June 29, 2026 (docketed July 1, 2026) from an unpublished June 23, 2025 decision of the Court of Appeals of Georgia (Fourth Division), with certiorari denied 5–4 by the Supreme Court of Georgia on March 3, 2026.
   - One cert-stage amicus brief was filed by the Atlantic Legal Foundation on August 3, 2026. Respondent Jordan Brewer filed a brief in opposition on September 2, 2026, and Petitioner Samsung Electronics America, Inc. (SEA) filed a reply brief on September 16, 2026.
   - The petition was distributed on September 29, 2026 for the October 16, 2026 conference, marked `Rescheduled` on October 15, 2026, and distributed on October 19, 2026 for the October 30, 2026 conference.
2. **Provisioned Documents (`record/documents/`):**
   - Read `documents.json`, `questions-presented.txt`, `petition.txt` (including the appended Georgia Court of Appeals opinion, trial court orders, and Georgia Supreme Court order), and `brief-in-opposition.txt` (including its statutory/regulatory appendix). Note that while the docket reflects a September 16, 2026 cert reply brief, no `cert-reply.txt` was provisioned in `documents.json`.
   - Note on retrieval: CourtListener MCP calls returned HTTP 429 (daily rate limit throttled), so we relied on the provisioned record (which already contains the full lower-court opinions in the petition appendix), `uv run fedcourts query` against the corpus, and `metrics/statpack.md`.

## Base-Rate Anchoring (`metrics/statpack.md`)
Under the prompt contract for a cert-stage cell with `band: "elevated"` under `salience_version: "sal-v4"`, we anchor on the **bracketed `reached`** grant rate for the `elevated` band in the "Segment base rate by salience band (sal-v4)" table, pooled across all rendered Terms strictly preceding OT2026 (OT2017–OT2025):
- OT2025: 13.4% (n=320, ~43 grants)
- OT2024: 18.3% (n=338, ~62 grants)
- OT2023: 17.5% (n=354, ~62 grants)
- OT2022: 19.2% (n=302, ~58 grants)
- OT2021: 20.8% (n=342, ~71 grants)
- OT2020: 16.4% (n=397, ~65 grants)
- OT2019: 13.8% (n=334, ~46 grants)
- OT2018: 16.1% (n=348, ~56 grants)
- OT2017: 18.1% (n=404, ~73 grants)
- **Pooled strictly-prior `elevated` [reached] anchor (OT2017–OT2025):** **17.1%** (536 grants over n=3,139 weighted resolved petitions). By comparison, the terminal `elevated` rate across OT2017–OT2025 is 10.3% (236 / 2,286).

Cross-checking the marginal cuts in `metrics/statpack.md`:
- **Modern discretionary-cert petitions overall:** 1.5% `granted` (692) + 1.3% `gvr` (590) = **2.8%** grant-family rate across 44,777 resolved petitions.
- **Relist bucket `1` (`distribution_count = 2`, paid scored segment):** 8.5% `granted` + 5.2% `gvr` = **13.7%** grant-family rate (n=2,538 resolved; 85.3% denied).
- **CVSG `none` (paid scored segment):** 4.1% `granted` + 2.3% `gvr` = **6.4%** grant-family rate (n=13,556 resolved).
- **Cert amicus `1` (paid scored segment):** 10.3% `granted` + 4.8% `gvr` = **15.1%** grant-family rate (n=1,162 resolved).
- **Originating court `(none)` (state courts in modern cert table):** 0.6% `granted` + 0.7% `gvr` = **1.3%** grant-family rate (n=11,615 resolved).

## Case-Specific Adjustments from the 17.1% Anchor

We adjust substantially downward from the 17.1% `elevated` reached baseline to **3.0% (`0.03`)** for four converging reasons:

1. **The second distribution is a pre-conference reschedule, not a post-conference relist:**
   The docket shows that the petition was scheduled for its first conference on October 16, 2026, marked `Rescheduled` on October 15, 2026, and redistributed on October 19, 2026 for the October 30, 2026 conference. As `metrics/statpack.md` notes, `dist-v2` counts a pre-conference reschedule in `distribution_count`, placing this petition in `elevated` before any conference has considered it. A pre-conference reschedule carries far less grant signal than a post-conference relist.
2. **Repeated, recent Supreme Court denials on the same post-*Mallory* issue—including from Georgia:**
   In *Mallory v. Norfolk Southern Railway Co.*, 600 U.S. 122 (2023) (No. 21-1168), the Court upheld registration-based general jurisdiction under *Pennsylvania Fire Insurance Co. v. Gold Issue Mining & Milling Co.*, 243 U.S. 93 (1917). Three days later, the Court denied certiorari in *Cooper Tire & Rubber Co. v. McCall*, No. 21-926 (cert. denied June 30, 2023), which challenged the very Georgia Supreme Court precedent applied by the Georgia Court of Appeals below. The Court has continued to deny follow-on challenges to registration-based general jurisdiction, including *Syngenta Crop Protection, LLC v. Nemeth*, No. 24-1190 (cert. denied Oct. 6, 2025), and *Norfolk Southern Railway Co. v. Mallory*, No. 25-1208 (cert. denied Oct. 5, 2026). Notably, the lone amicus here (Atlantic Legal Foundation) was also amicus in *Cooper Tire*, *Syngenta*, and *Norfolk Southern v. Mallory*.
3. **Lack of a true constitutional split on notice via authoritative state judicial construction:**
   SEA argues that Georgia's registration statute (`O.C.G.A. § 14-2-1505(b)`) lacks express statutory text warning of general jurisdiction and that SEA initially registered in 1982, prior to *Allstate Insurance Co. v. Klein*, 262 Ga. 599 (1992). However, as the BIO demonstrates, *Pennsylvania Fire* itself rested on the Missouri Supreme Court's judicial construction of Missouri's registration statute (see *Mallory*, 600 U.S. at 131–32), and the state decisions SEA cites as "splits" simply construed their own state registration statutes not to confer general jurisdiction as a matter of state statutory interpretation. Furthermore, SEA renewed its Georgia registration annually for nearly three decades after *Klein* (including in 2019 and 2020), undermining its claim of lack of prior notice.
4. **Severe vehicle and factual complications:**
   - **Strong forum nexus:** Unlike *Mallory* and *Cooper Tire* (out-of-state plaintiffs injured out of state), Respondent Jordan Brewer is a Georgia resident who bought the replacement battery in Georgia and was injured at his home in Georgia when the e-cigarette exploded in his pocket.
   - **Default judgment and unwithdrawn admissions:** The case arises from a $10.86 million default judgment entered after SEA failed to answer complaints served on its registered agent and failed to respond to requests for admissions under `O.C.G.A. § 9-11-36`. Although the Georgia Court of Appeals affirmed on *Cooper Tire* consent-by-registration grounds without relying on the unappealed denial of SEA's motion to withdraw its admissions, the default posture and unwithdrawn admissions are significant vehicle deterrents.

## Rationale for Auxiliary Claims and Uncertainties
- **`relist-increment` (0.12):** Because October 30, 2026 is the petition's first actual conference after its October 15 reschedule, there is roughly a 12% chance that a chambers relists the case at least once (for example, to check the post-*Mallory* arguments or the 5–4 Georgia Supreme Court cert vote) before ultimately denying review.
- **`cvsg-increment` (0.005):** Virtually zero probability of a CVSG in a private state-court tort default judgment presenting a purely constitutional Due Process question.
- **`summary-disposition-route` (0.10):** Conditional on a grant, plenary review is far likelier (90%) than a summary disposition or GVR (10%), as there is no pending SCOTUS merits vehicle for a hold-and-GVR and the Court's 5–4 split in *Mallory* makes summary reversal unlikely.
- **`dissent-from-denial` (0.02) and `order-writers`:** Given that *Cooper Tire*, *Syngenta*, and *Norfolk Southern v. Mallory* all drew zero recorded dissents from denial, we assign a 2% conditional probability to a dissent or statement respecting denial, weighted slightly toward Justices Alito (0.006), Barrett (0.005), Thomas (0.004), and Gorsuch (0.003).
- **Main uncertainties:** The 5–4 vote to deny certiorari in the Georgia Supreme Court (where four justices voted to grant review) and the presence of experienced Supreme Court counsel (Dominic Draye for Petitioner; former Georgia Solicitor General and former Georgia Supreme Court Justice Andrew Pinson for Respondent) slightly elevate the chance that a Justice takes a closer look at conference, preventing the grant probability from falling to the ~1% floor.
