# Prediction Reasoning: *Jasvinder Singh, et al. v. Second Judicial District Court of Nevada, Washoe County, et al.* (No. 26-157)

- **Case ID:** `scotus/9026000157`
- **Event ID:** `evt-order-call-for-response-disposition` (Call for a Response)
- **Snapshot:** `2026-09-23.json`
- **Predicted Disposition:** `denied` (`granted: false`, `probability: 0.14`)

---

## 1. Base-Rate Anchor and Trajectory Position

Under `record/context.json` and `metrics/statpack.md` (`sal-v7`), this paid discretionary-certiorari petition from the Supreme Court of Nevada carries a frozen `"band": "baseline"` anchor with a 10-Term pooled reached grant rate of **5.15%** (`cert_anchor.rate = 0.051513`).

However, the docket snapshot as of September 23, 2026 (`2026-09-23.json`) shows significant cert-stage escalation beyond an unassisted baseline filing:
1. **Repeat-player Supreme Court counsel:** Petitioners are represented by Tobias S. Loss-Eaton and Jeffrey T. Green of Sidley Austin LLP and the Northwestern Supreme Court Clinic; Respondents have added Paul Whitfield Hughes of McDermott Will & Schulte LLP alongside trial/appellate counsel at Holland & Hart LLP.
2. **Concerted cert-stage amicus support:** Following Respondents' August 21, 2026 waiver of the right to respond, three cert-stage amicus briefs were timely filed in support of Petitioners:
   - *Anglican Church in North America* (filed Aug. 26, 2026, by Jones Day);
   - *Former EEOC General Counsel Sharon Fast Gustafson and Rachel N. Morrison* (filed Sept. 2, 2026, by Hunton Andrews Kurth LLP); and
   - *The Roman Catholic Archbishop of Las Vegas and His Successors* (filed Sept. 2, 2026, by Vinson & Elkins LLP).
3. **Call for a Response (CFR):** After distribution on September 16, 2026 for the October 9, 2026 Long Conference (`distribution_count = 1`), the Court called for a response on September 22, 2026 (due October 22, 2026).

In `metrics/statpack.md`, paid petitions in the `elevated` salience band (which reflects non-federal/non-state petitions that draw a CFR and multiple amicus briefs) have a 10-Term reached grant rate around **21%–28%**, and paid petitions with `2+` cert-stage amicus briefs have a resolved grant-family rate of **22.7%** (18.2% granted, 4.5% GVR) across all relist counts, though petitions evaluated at the initial CFR moment—before the Brief in Opposition (BIO) is filed and before any post-BIO conference relist—convert to plenary grants at a substantially lower rate (typically ~10%–18%) because the vast majority are denied once the BIO exposes vehicle, factual, or finality defects.

---

## 2. Case Overview and Question Presented

The Northern Nevada Sikh Society (NNSS) is a Nevada nonprofit corporation (organized under NRS Chapter 82) that owns and operates the Sikh Temple of Reno, Nevada. Under Article One of the NNSS bylaws, the corporation and its assets are "vested in general body (Sikh Sangat as a whole) of the State of Nevada and remain to be that forever," and "[t]he Management Committee or any other person has no authority to change it" (App. 18a). Article Three defines general membership in explicitly religious terms (requiring that a member be a Sikh by birth, marriage, adoption, or conversion, believe in the *Shri Guru Granth Sahib* and the scriptures of the Ten Gurus, and not profess any other religion, App. 19a).

In 2024, Respondents—general members and former members of the NNSS Management Committee—sued Petitioners (current Management Committee officers and members of two subcommittees) in Nevada state court under NRS 82.216(1). Respondents alleged that Petitioners violated the corporate bylaws by:
1. Forming an "Interim Committee" and later a "Subcommittee" without approval of a majority of the general members in order to transfer the Sikh Temple into a separate trust;
2. Failing to issue membership cards or maintain membership records as required by the bylaws; and
3. Refusing to allow members to inspect the corporation's books and records.
Respondents sought declaratory and injunctive relief declaring that the committees lacked authority to dispose of NNSS's assets, that the Temple must remain the property of NNSS, and that the Management Defendants' actions and elections were invalid under the bylaws.

The state trial court denied Petitioners' motion to dismiss under the ecclesiastical abstention (church-autonomy) doctrine, and Petitioners sought an extraordinary writ of prohibition or mandamus from the Nevada Supreme Court. In a published opinion (`Singh v. Second Judicial District Court`, 586 P.3d 858 (Nev. Apr. 2, 2026)), the Nevada Supreme Court denied writ relief. Relying on the Ninth Circuit's decision in *Puri v. Khalsa*, 844 F.3d 1152 (9th Cir. 2017), the court held that:
- The "neutral-principles" exception to the ecclesiastical abstention doctrine (recognized in *Presbyterian Church in the United States v. Mary Elizabeth Blue Hull Memorial Presbyterian Church*, 393 U.S. 440 (1969), and *Jones v. Wolf*, 443 U.S. 595 (1979)) is not limited to real-property ownership disputes between competing factions, so long as the court can resolve the dispute using neutral principles of law without considering or resolving controversies over religious doctrine, practices, or texts (App. 12a–13a); and
- "At this juncture," Respondents' claims under NRS 82.216(1) appear secular and turn on whether NNSS Management exceeded its corporate authority under the bylaws without requiring the court to evaluate Sikh doctrine, practices, or religious eligibility requirements (App. 14a–15a).

The Question Presented asks:
> Whether the church-autonomy doctrine allows a civil court to invoke "neutral principles" beyond the property-ownership context, and thus to decide a religious institution's internal governance dispute under organizational documents that define membership and authority in religious terms.

---

## 3. Analysis of Certiorari Factors

### A. Factors Favoring Certiorari (Upward Pressure from the 5.15% Anchor)
1. **Active Lower-Court Division and Judicial Commentary on "Neutral Principles":** There is genuine doctrinal tension across federal circuits and state high courts over how far *Jones v. Wolf*'s "neutral principles of law" framework extends outside formal title/property disputes. Several courts—including the Ninth Circuit (*Puri v. Khalsa*, 844 F.3d 1152; *Huntsman v. Corp. of the President of the Church of Jesus Christ of Latter-day Saints*, 127 F.4th 784 (9th Cir. 2025) (en banc)), the Second Circuit (*Belya v. Kapral*, 45 F.4th 621 (2d Cir. 2022)), the D.C. Circuit (*O'Connell v. U.S. Conference of Catholic Bishops*, 134 F.4th 1243 (D.C. Cir. 2025)), the Texas Supreme Court (*Southern Methodist University v. South Central Jurisdictional Conference of the United Methodist Church*, 716 S.W.3d 475 (Tex. 2025)), and now the Nevada Supreme Court—frame neutral principles as available whenever a civil claim can be resolved without deciding religious doctrine. Conversely, the Fifth Circuit (*Lutheran Church—Missouri Synod v. Christian*, 178 F.4th 193 (5th Cir. 2026); *McRaney v. North American Mission Board of the Southern Baptist Convention*, 157 F.4th 627 (5th Cir. 2025)), alongside earlier decisions from the Sixth and Eleventh Circuits (*Hutchison v. Thomas*, 789 F.2d 392 (6th Cir. 1986); *Crowder v. Southern Baptist Convention*, 828 F.2d 718 (11th Cir. 1987)) and state high courts such as Oklahoma (*Oklahoma Annual Conference of the United Methodist Church, Inc. v. Timmons*, 2023 OK 101), hold that church autonomy categorically bars civil courts from adjudicating internal church governance, polity, or membership disputes even under facially secular rules. Prominent concurrences and dissents (e.g., Judges Bress and Bumatay in *Huntsman*, Judge Park in *Belya*, Judge Rao in *O'Connell*, and Judges Jones and Ho in *Lutheran Church* and *McRaney*) have highlighted this divide.
2. **Strong Representation and Amicus Support:** The combination of Sidley Austin / Northwestern Clinic counsel, three coordinated amicus briefs from repeat religious-liberty amici, and the Court's Call for a Response confirms that at least one chambers views the church-autonomy question as warranting full adversarial briefing.

### B. Factors Weighing Strongly Against Certiorari (Why Denial Remains Likely)
1. **Recent Denial of Certiorari in *USCCB v. O'Connell* (No. 25-849):** Corpus query records show that on **May 26, 2026**—just four months before this CFR—the Court denied certiorari in *United States Conference of Catholic Bishops v. O'Connell*, No. 25-849 (`scotus/73280351`), despite four distributions and more than a dozen amicus briefs (including briefs from two of the exact same amici appearing here: *Anglican Church in North America* and *Sharon Fast Gustafson and Rachel N. Morrison*). That follows the Court's earlier denial in *Belya v. Kapral*, 143 S. Ct. 2609 (2023). While *O'Connell* and *Belya* also implicated federal collateral-order jurisdiction, the Court has consistently declined to take up interlocutory church-autonomy petitions at the motion-to-dismiss stage.
2. **Interlocutory Posture, Provisional Ruling Below, and Finality Obstacles Under 28 U.S.C. § 1257(a):**
   - The case is at the threshold motion-to-dismiss stage in state trial court. Petitioners sought discretionary extraordinary writ relief (prohibition) in the Nevada Supreme Court.
   - Although Petitioners invoke *Atlantic Richfield Co. v. Christian*, 590 U.S. 1 (2020), and *Cox Broadcasting Corp. v. Cohn*, 420 U.S. 469 (1975), to argue that the denial of an original writ of prohibition is a final judgment, the Nevada Supreme Court's opinion is expressly provisional. The court emphasized twice that nothing in the bylaws or claims *"as it appears at this point in the proceedings"* requires evaluating Sikh doctrine (App. 15a) and that *"At this juncture, the claims presented in RPIs' underlying complaint appear to be secular in nature"* (App. 15a).
   - Because the state courts have not precluded Petitioners from reasserting ecclesiastical abstention on summary judgment if discovery or factual development shows that resolving the election or trust claims actually requires determining who is an observant Sikh under Article Three of the bylaws, the federal question is not finally and conclusively resolved against Petitioners on a developed record.
3. **Poor Fit Between the Question Presented and the Underlying Property-Transfer Dispute:**
   - Petitioners frame the Question Presented as whether the neutral-principles approach may be extended *"beyond the property-ownership context."*
   - Yet the core catalyst of the underlying lawsuit *is* a dispute over control and disposition of the congregation's real property: Petitioners' alleged attempt to transfer the Sikh Temple of Reno out of the nonprofit corporation (NNSS) and into a separate trust in violation of Article One of the bylaws ("This corporation, its Management Committee and its assets are vested in general body (Sikh Sangat as a whole) of the State of Nevada and remain to be that forever," App. 18a) without congregational approval.
   - Furthermore, the Nevada Supreme Court expressly noted that "[t]he parties also do not contest whether the Management Defendants meet the religious eligibility requirements for the disputed Management Committee positions or to be considered general members of NNSS" (App. 14a).
   - Once Respondents' Supreme Court counsel (Paul Hughes) files the BIO, the brief will emphasize that preventing nonprofit corporate directors from transferring the church building into a trust in violation of explicit corporate charter restrictions—and enforcing statutory rights to inspect corporate books and records under NRS 82.216(1)—lies squarely within the traditional heartland of *Jones v. Wolf* (which expressly contemplated looking to corporate charters and majority-vote rules in congregational property disputes where no doctrinal controversy is presented).

---

## 4. Conclusion and Probability Calibration

- **Base rate anchor (`baseline` reached, `sal-v7`):** 5.15%.
- **Upward adjustments:** The Call for a Response after a waiver, three cert-stage amicus briefs, top-tier Supreme Court clinic representation, and genuine circuit-level friction over the scope of "neutral principles" in church-autonomy cases raise the probability of a grant well above the 5.15% baseline.
- **Downward adjustments from the `elevated` (21%–28%) / `2+ amicus` (22.7%) ceiling:** We are at the pre-BIO CFR stage (`distribution_count = 1`), and the petition suffers from serious vehicle defects that the forthcoming BIO will highlight: (1) an interlocutory motion-to-dismiss posture where the Nevada Supreme Court explicitly qualified its holding as limited to *"this juncture"* / *"at this point in the proceedings"*; (2) a central factual focus on transferring the Sikh Temple real property into a trust, which blurs the Question Presented's premise that this case is "beyond the property-ownership context"; (3) the absence of any actual dispute over religious qualifications or Sikh doctrine; and (4) the Court's recent denial of certiorari in *USCCB v. O'Connell* (No. 25-849) on May 26, 2026.

We therefore forecast **denied** (`granted: false`) with a grant probability of **0.14** (14%).
