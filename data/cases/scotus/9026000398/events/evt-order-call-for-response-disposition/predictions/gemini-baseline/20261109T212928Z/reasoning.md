# Prediction Reasoning: *Sherhonda Golden v. NBCUniversal Media, LLC* (No. 26-398)

- **Case ID**: `scotus/9026000398`
- **Event ID**: `evt-order-call-for-response-disposition` (`stage: cert`, `moment: response-requested`)
- **Predicted Disposition**: `denied` (`granted: 0`, `probability: 0.04`)

---

## 1. Base-Rate Anchor and Conditioning State

From `record/context.json` (`mode: "forward"`, `snapshot_date: "2026-10-23"`, `cutoff: "2026-10-23"`, `cut_kind: "date"`), the harness froze the conditioning state for this cell as:
- `band`: `"baseline"` under `salience_version: "sal-v8"`
- `distribution_count`: `1` (distributed on October 14, 2026 for the Conference of October 30, 2026)
- `cvsg_date`: `null`, `amicus_briefs`: `null` (0 amicus briefs on the docket)
- `cert_anchor.rate`: **`0.051587928582714486` (~5.2%)**, pooled over `lookback_terms: 10` (`OT2016–OT2025`, `statpack_digest: "sha256:9da7dbfa464075bfc7fab6e6b641ec9060684cd53259a76380a32823adf6f653"`).

In `metrics/statpack.md`, the **"Segment base rate by salience band (sal-v8)"** table shows the bracketed `reached` risk-set rates for `baseline` across the 9 rendered prior Terms strictly preceding OT2026 (`OT2017–OT2025`):
- OT2025: 4.0% (`n=1290`), OT2024: 6.0% (`n=1243`), OT2023: 6.0% (`n=1283`), OT2022: 5.9% (`n=1183`), OT2021: 5.7% (`n=1469`), OT2020: 4.7% (`n=1697`), OT2019: 4.7% (`n=1369`), OT2018: 4.8% (`n=1509`), OT2017: 5.0% (`n=1615`), matching the frozen 10-term `cert_anchor.rate` of **5.16%**.

Checking the marginal signal cuts in `metrics/statpack.md` for the paid scored segment:
- **By relist count**: `0` relists (`distribution_count = 1`) has a resolved base rate of `denied 96.8%, dismissed 1.3%, granted 1.3%, gvr 0.5%` (grant family **1.8%**, `n=10,204` resolved).
- **By CVSG status**: `none` has a resolved base rate of `denied 92.4%, granted 4.1%, gvr 2.3%, dismissed 1.2%` (grant family **6.4%**, `n=13,550` resolved).
- **By amicus-brief count**: `0` amicus briefs has a resolved base rate of `denied 95.0%, granted 2.0%, gvr 1.8%, dismissed 1.3%` (grant family **3.8%**, `n=11,109` resolved).
- **By originating circuit**: `ca2` (Second Circuit) has a resolved base rate of `denied 92.6%, granted 2.6%, dismissed 2.5%, gvr 2.4%` (`n=2,081` resolved).

Because this is the `response-requested` moment (`opened_at: 2026-10-22`), the Court called for a response after Respondent NBCUniversal Media, LLC waived its right to respond on October 8, 2026. A Call for a Response (CFR) indicates that at least one chambers flagged the petition for closer examination rather than letting it be denied on a waiver, which moderately elevates the baseline probability of a grant or GVR relative to an unflagged once-distributed petition. However, weighing the CFR against the specific legal and procedural record of this case leads me to adjust **downward** from the 5.16% `baseline` risk-set anchor to **`probability: 0.04` (4% chance of any grant, 96% chance of denial)**.

---

## 2. Analysis of the Provisioned Record (`2026-10-23.json`, `questions-presented.txt`, `petition.txt`)

### A. Factual and Procedural Posture
We have the provisioned snapshot `2026-10-23.json` and two non-truncated text files in `record/documents/`: `questions-presented.txt` and `petition.txt` (which includes the petition and the Second Circuit and SDNY decisions in the appendix, with only a `[pipeline note]` omitting the final pages of the Fourth Amended Complaint at the end of the appendix). No brief in opposition is on the record yet because the snapshot is cut on October 23, 2026, the day after the Court called for a response (due November 23, 2026).

Petitioner Sherhonda Golden signed up in 2022 for a free daily email newsletter from Today.com (owned by NBCUniversal) and clicked video links in the newsletter to watch prerecorded videos on Today.com while logged into Facebook. She brought a putative class action under the Video Privacy Protection Act ("VPPA"), 18 U.S.C. § 2710, alleging that Today.com's embedded Meta Pixel transmitted the URLs/titles of the videos she requested alongside her numeric Facebook ID ("FID") stored in the `c_user` browser cookie.

The case went through two distinct rounds in the lower courts:
1. **First Round ("Consumer" / "Subscriber" Issue)**: Judge Engelmayer (S.D.N.Y.) initially dismissed the complaint on the ground that a subscriber to a free daily email newsletter is not a "subscriber of goods or services from a video tape service provider" ("consumer") under 18 U.S.C. § 2710(a)(1). While Golden's appeal was pending, the Second Circuit decided *Salazar v. National Basketball Ass'n* (*Salazar II*), 118 F.4th 533 (2d Cir. 2024), *cert. denied*, 146 S. Ct. 809 (Dec. 8, 2025) (No. 24-994), holding that an online newsletter subscriber *does* plausibly qualify as a VPPA "consumer." Judge Engelmayer issued an indicative ruling vacating his prior dismissal, and the Second Circuit remanded.
2. **Second Round ("Personally Identifiable Information" Issue)**: Before NBCU moved to dismiss the Fourth Amended Complaint, the Second Circuit decided *Solomon v. Flipps Media, Inc.*, 136 F.4th 41 (2d Cir. May 1, 2025), *cert. denied*, 146 S. Ct. 885 (Dec. 8, 2025), joining the Third Circuit (*In re Nickelodeon Consumer Privacy Litig.*, 827 F.3d 262 (3d Cir. 2016)) and Ninth Circuit (*Eichenberger v. ESPN, Inc.*, 876 F.3d 979 (9th Cir. 2017)) in adopting the "ordinary person" standard for "personally identifiable information" ("PII") under 18 U.S.C. § 2710(a)(3) and rejecting the First Circuit's recipient-focused "reasonable foreseeability" standard (*Yershov v. Gannett Satellite Info. Network, Inc.*, 820 F.3d 482 (1st Cir. 2016)). Under *Solomon*, transmitting video titles/URLs and a user's `c_user` FID via the Meta Pixel is not a disclosure of PII because an ordinary person inspecting the computer code could not readily identify the individual. The Second Circuit applied *Solomon* again in *Hughes v. National Football League*, No. 24-2656, 2025 WL 1720295 (2d Cir. June 20, 2025), *cert. denied*, 146 S. Ct. 1790 (Mar. 9, 2026).
3. **Decisions Below**: On September 3, 2025, Judge Engelmayer dismissed Golden's Fourth Amended Complaint with prejudice as squarely foreclosed by *Solomon* and *Hughes* (`Pet. App. 9a–31a`). On May 21, 2026, the Second Circuit (Judges Chin, Park, and Kahn) affirmed by summary order (`Pet. App. 1a–8a`), holding that Golden's allegations were materially indistinguishable from *Solomon* and that a three-judge panel could not overrule *Solomon* based on general textualist principles in intervening Supreme Court decisions on unrelated statutes (*Fuld*, *A.J.T.*, *Kousisis*, and *Thompson*).

---

## 3. Why the Probability of Grant (Plenary or GVR) Is Low (`0.04`)

### A. Two Recent Cert Denials on the Exact Same Question from the Same Circuit
The Supreme Court has already denied certiorari **twice in the past eleven months** on this exact question presented from the Second Circuit involving the Meta Pixel:
1. *Solomon v. Flipps Media, Inc.*, 136 F.4th 41 (2d Cir. 2025), *cert. denied*, 146 S. Ct. 885 (Dec. 8, 2025) — the Second Circuit's published flagship opinion adopting the "ordinary person" rule.
2. *Hughes v. National Football League*, 2025 WL 1720295 (2d Cir. 2025), *cert. denied*, 146 S. Ct. 1790 (Mar. 9, 2026) — the follow-on Second Circuit summary order applying *Solomon*.

Nothing in the circuit landscape has changed in the seven months since *Hughes* was denied on March 9, 2026. No court of appeals has broken with the Second, Third, and Ninth Circuits' consensus since the First Circuit's decade-old decision in *Yershov* (2016), which involved GPS coordinates and device identifiers rather than browser cookies/pixels.

### B. Poor Vehicle Relative to *Solomon*
Even if the Court ever wished to revisit the VPPA's definition of PII, *Golden* is a markedly worse vehicle than *Solomon*:
- The decision below is a non-precedential summary order (`25-2226-cv`) that did not engage in *de novo* statutory construction of § 2710(a)(3), instead applying Second Circuit law-of-the-panel rules.
- Unlike the plaintiff in *Solomon* (who subscribed directly to a video streaming platform), Golden's threshold status as a VPPA "consumer" rests solely on a free Today.com email newsletter subscription—the exact issue currently under review in *Salazar v. Paramount Global*, No. 25-459 (cert. granted Jan. 26, 2026; argued Oct. 14, 2026). If the Court affirms the Sixth Circuit in *Salazar* and holds that newsletter subscribers are *not* VPPA consumers, Golden's claim fails at the threshold without ever reaching the PII question.

### C. Why the CFR and the Request to Hold for *Salazar v. Paramount Global* Will Likely Still End in a Denial
Why did the Court call for a response on October 22, 2026—eight days after oral argument in *Salazar v. Paramount Global* (No. 25-459)?
- The same counsel of record represent both sides in both cases: Joshua Ian Hammack represents both Michael Salazar (No. 25-459) and Sherhonda Golden (No. 26-398), and Paul D. Clement represents both Paramount Global (No. 25-459) and NBCUniversal (No. 26-398).
- In Part II of the Petition (`Pet. 25–26`), Golden explicitly asked the Court, "[a]t a minimum," to hold this petition pending *Salazar v. Paramount Global*. Because NBCU waived a response on October 8, 2026, calling for a response allows the Court to hear NBCU's position on whether the case should be held or denied outright.
- Crucially, **neither possible outcome in *Salazar v. Paramount Global* warrants a GVR in *Golden***:
  - In *Golden*, the District Court and Second Circuit *already held* under Second Circuit law (*Salazar v. NBA*, 118 F.4th 533) that Golden *is* a VPPA "consumer" (`Pet. App. 18a`), and affirmed dismissal solely on the independent ground that no PII was disclosed under *Solomon*.
  - Thus, if the Supreme Court **affirms** the Sixth Circuit in *Salazar v. Paramount Global* (holding that newsletter subscribers are *not* consumers), Golden loses on *both* elements and the dismissal below stands.
  - And if the Supreme Court **reverses** the Sixth Circuit in *Salazar v. Paramount Global* (holding that newsletter subscribers *are* consumers), that merely confirms the Second Circuit rule already applied in Golden's favor below, leaving the independent PII dismissal under *Solomon* untouched.
- There remains a small (~1.4% unconditional, or `0.35` conditional on the 4% grant probability) chance that if the Court reverses in *Salazar v. Paramount Global* with sweeping language about interpreting the VPPA's text, it might issue a routine GVR, and a ~2.6% unconditional chance of plenary review on the PII split. Combined, that yields `probability: 0.04` (`granted: 0`, `predicted_disposition: "denied"`).

---

## 4. Claims, Distribution Claims, and Big-Case Score Rationale

- **`claims`**:
  - `disposition`: `0.04` (equals top-level `probability`, representing a 2.6% chance of plenary review + 1.4% chance of a post-*Salazar* GVR).
  - `relist-increment`: `0.98` (the snapshot records 1 distribution so far, for the Oct. 30, 2026 conference; once NBCU files its response due Nov. 23, 2026, the petition will be distributed again for a subsequent conference).
  - `cvsg-increment`: `0.01` (private statutory dispute with no federal party or agency interest).
  - `summary-disposition-route`: `0.35` (conditional on a grant, ~35% chance of a GVR following *Salazar v. Paramount Global* vs. ~65% chance of plenary review on the PII question).
  - `dissent-from-denial`: `0.02` (conditional on denial, neither *Solomon* nor *Hughes* drew a dissent from denial on this exact question).
- **`claim_distributions` (`order-writers`)**: Low per-Justice writing probabilities summing to slightly above 2% to account for possible co-signed dissents/statements from denial, led by Justices Thomas (`0.005`), Gorsuch (`0.005`), and Alito (`0.004`).
- **`big_case_score`: `0.38`**: If decided on the merits, whether the VPPA's definition of PII encompasses numeric social-media identifiers transmitted via third-party tracking pixels would have broad commercial impact across online publishers, streaming platforms, and digital advertising networks, though it remains a statutory consumer-privacy dispute of moderate public salience.
