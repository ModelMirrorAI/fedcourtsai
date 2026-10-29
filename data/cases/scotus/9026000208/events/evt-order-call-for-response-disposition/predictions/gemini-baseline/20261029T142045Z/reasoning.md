# Predictor Rationale: *George Anibowei v. Todd Blanche, Attorney General, et al.* (No. 26-208)

**Event:** `evt-order-call-for-response-disposition` (Certiorari disposition forecast at the `response-requested` moment)  
**Input Snapshot:** `2026-09-30.json` (Cutoff: `2026-09-30`)  
**Headline Forecast:** `denied` (`granted: false`, `probability: 0.14`)  
**Big-Case Score:** `0.68`

---

## 1. Base Rate Anchor and Conditioning Segment

Per `record/context.json`, this petition is in the **`baseline`** salience band under `sal-v4` (`distribution_count: 1`, `cvsg_date: null`, private petitioner). Anchoring on the per-Term salience-band risk-set table in `metrics/statpack.md` across the strictly prior Terms (OT2017–OT2025):

- **Risk-set grant rate for the `baseline` band (OT2017–OT2025 pooled):** 390 grants out of 10,842 resolved petitions = **3.60%** (terminal `baseline` band rate: 0.87%, 80 / 9,151).
- **Moment conditioning (`response-requested`) and docket signals:** This forecast is taken at `evt-order-call-for-response-disposition`. Although the Federal Respondents automatically have a response deadline on the docket (originally September 18, 2026, extended to October 19, 2026, with distribution for the Conference of October 9, 2026 reflects the amici/extension flow), the petition has drawn **substantial cert-stage amicus support**: **9 amicus briefs** filed on September 18, 2026 by major cross-ideological and institutional repeat players (American Bar Association, Cato Institute & Freedom of the Press Foundation, Constitutional Accountability Center, Fourth Amendment Scholars, Professor Morgan Cloud, Project for Privacy & Surveillance Accountability, The Rutherford Institute, The Haitian Bridge Alliance, Texas Criminal Defense Lawyers Association, and Max Blumenthal), alongside experienced Supreme Court counsel (Andrew Tutt and John Elwood of Arnold & Porter).
- Petitions with 9 cert-stage amicus briefs and elite Supreme Court counsel sit far in the upper tail of the `baseline` risk set—empirically comparable to petitions that reach the `elevated` risk set (~17.6% grant rate across OT2017–OT2025) once distributed after the Brief in Opposition.

Starting from this conditioned prior (~15%–20% for a heavily-amicused constitutional petition with elite counsel), I adjust **downward to 14% (`0.14`)** because of the absence of a circuit split on the categorical warrant question presented, the Court's repeated denials of closely related border-cell-phone-search petitions, and the prior history of this very litigation (*Anibowei v. Mayorkas*, No. 23-199, denied Jan. 8, 2024).

---

## 2. Case Analysis: Why Certiorari Is Unlikely (86% Probability of Denial)

### A. Lopsided Circuit Consensus Against Petitioner's Categorical Warrant Rule
The single Question Presented is binary and categorical: *"Whether the Fourth Amendment permits border agents to search the digital contents of a traveler's cell phone without a warrant."*

As the Fifth Circuit explained in *Malik v. U.S. Department of Homeland Security*, 78 F.4th 191, 199 (5th Cir. 2023) (App. 20a–22a)—which controlled the summary affirmance here—**no federal court of appeals has held that a warrant is required to search a cell phone at the border**. On the contrary, the First, Fourth, Fifth, Seventh, Eighth, Ninth, Tenth, and Eleventh Circuits have all squarely rejected applying *Riley v. California*, 573 U.S. 373 (2014), to require a warrant for border cell phone searches:
- *Alasaad v. Mayorkas*, 988 F.3d 8, 17 (1st Cir. 2021), *cert. denied sub nom. Merchant v. Mayorkas*, 141 S. Ct. 2858 (2021) (No. 20-1505)
- *United States v. Kolsuz*, 890 F.3d 133, 147 (4th Cir. 2018); *United States v. Aigbekaen*, 943 F.3d 767, 779 n.5 (4th Cir. 2019)
- *Malik v. U.S. Dep't of Homeland Sec.*, 78 F.4th 191, 200 (5th Cir. 2023)
- *United States v. Mendez*, 103 F.4th 1303, 1309 (7th Cir. 2024)
- *United States v. Haitao Xiang*, 67 F.4th 895, 900 (8th Cir. 2023)
- *United States v. Cano*, 934 F.3d 1002, 1015 (9th Cir. 2019), *cert. denied*, 141 S. Ct. 2877 (2021) (No. 20-1043)
- *United States v. Williams*, 942 F.3d 1187, 1190–91 (10th Cir. 2019)
- *United States v. Touset*, 890 F.3d 1227, 1233 (11th Cir. 2018)

While the circuits differ on Secondary Questions—such as whether *forensic* (as opposed to manual) searches require *reasonable suspicion* (compare *Touset*, 890 F.3d at 1233, with *Kolsuz*, 890 F.3d at 144, and *Cano*, 934 F.3d at 1016) or whether border searches must be tethered strictly to detecting physical digital contraband (*Cano*, 934 F.3d at 1018)—Petitioner deliberately does **not** raise the reasonable-suspicion split or the scope-of-contraband split. Instead, Petitioner frames the Question Presented exclusively around a categorical warrant requirement, where the circuits are 8–0 against him (with only two isolated district court decisions in the Second Circuit, *United States v. Smith*, 673 F. Supp. 3d 381 (S.D.N.Y. 2023), and *United States v. Sultanov*, 742 F. Supp. 3d 258 (E.D.N.Y. 2024), reaching a contrary result). The Solicitor General will heavily emphasize in the Brief in Opposition that every court of appeals to address the Question Presented has rejected Petitioner's position.

### B. Prior Supreme Court Denials on the Exact Issue—Including *Anibowei* Itself
Corpus queries confirm that the Court has repeatedly declined to review this question even when presented alongside acknowledged circuit splits on reasonable suspicion and scope:
1. ***United States v. Cano*, No. 20-1043 (cert. denied June 28, 2021)** (`scotus/72465054`): Even when the **United States petitioned** from the Ninth Circuit's decision invalidating a warrantless border cell phone search, the Court denied certiorari after two distributions.
2. ***Merchant v. Mayorkas*, No. 20-1505 (cert. denied June 28, 2021)** (`scotus/72465554`): A civil challenge brought by travelers represented by the ACLU and EFF challenging the same 2018 CBP and 2009 ICE directives under the First and Fourth Amendments was denied alongside *Cano*.
3. ***Anibowei v. Mayorkas*, No. 23-199 (cert. denied Jan. 8, 2024)** (`scotus/72479748`): In the interlocutory appeal in **this very lawsuit** (*Anibowei I*, 70 F.4th 898 (5th Cir. 2023)), Petitioner (represented by the same counsel of record, Andrew Tutt) petitioned for certiorari, supported by the Cato Institute as amicus, after the Fifth Circuit vacated a preliminary injunction and held that no Fifth Circuit precedent required a warrant for border cell phone searches. The Court denied certiorari after two distributions.

### C. Vehicle Considerations
Although this petition arises from a final judgment following a Rule 12(b)(6) dismissal of Count VI (where the district court and Fifth Circuit held that *Malik* foreclosed Anibowei's facial and as-applied warrant challenge), the case remains a civil suit for prospective declaratory and injunctive relief (including expungement of copied data from a 2016 search and a declaration against future border searches under ICE's 2009 Directive and CBP's 2018 Directive). The factual record is thin because the case was dismissed on the pleadings without discovery into the specific circumstances of Anibowei's October 2016 manual/advanced search or his up-to-four prior searches. Moreover, in *Malik*, the Fifth Circuit left open whether reasonable suspicion is required for advanced forensic searches because the government had not challenged that aspect of the district court's ruling in *Malik*. The Solicitor General will argue that if the Court ever wishes to address border cell phone searches, it should wait for either a Second Circuit appellate decision (where *Smith* and *Sultanov* are percolating) or a criminal suppression case with a fully developed factual record that cleanly presents both the warrant and reasonable-suspicion questions.

### D. Why Grant Probability Is Still 14% (Non-Trivial)
Despite the headwinds above, a 14% grant probability is warranted because:
1. **Substantial Amicus Coalition (9 Briefs):** Nine cert-stage amicus briefs—including the American Bar Association, Cato Institute, Constitutional Accountability Center, Rutherford Institute, and leading Fourth Amendment scholars—demonstrate exceptional salience and cross-ideological interest.
2. **Doctrinal Appeal to Originalist and Privacy-Minded Justices:** Justices Gorsuch, Sotomayor, and Jackson (and Chief Justice Roberts in *Riley* and *Carpenter*) have expressed strong interest in how founding-era Fourth Amendment principles apply to modern digital repositories. Petitioner's framing heavily targets *Riley* and *Carpenter*'s historical analysis of general warrants and writs of assistance.
3. **Clean Legal Holding Below:** Unlike *Anibowei I* (No. 23-199), which arrived in an interlocutory preliminary-injunction posture before *Malik* settled Fifth Circuit law, this petition arrives from a final judgment squarely applying *Malik*'s categorical holding that the Fourth Amendment does not require a warrant for any border cell phone search.

---

## 3. Mechanical Claims (`cert-v3`) and Authorship Distribution (`order-writers`)

- **`disposition` (`0.14`):** Matches headline `probability`.
- **`relist-increment` (`0.35`):** Although `relist-increment` is masked as vacuous on `evt-order-call-for-response-disposition` when scored (because a petition awaiting a response will be distributed again after the response is filed), the snapshot currently shows `distribution_count: 1` (from the pre-extension distribution schedule). In terms of true post-response relists after the BIO arrives, given the 9 amicus briefs and the Fourth Amendment issue, there is a ~35% chance that at least one Justice (e.g., Justice Gorsuch or Justice Sotomayor) holds or relists the petition at least once after the post-BIO distribution.
- **`cvsg-increment` (`0.0`):** Federal Respondents (Todd Blanche, Attorney General, et al.) are already named parties represented by the Solicitor General (`D. John Sauer`). The Court never issues a CVSG when the United States is already a party.
- **`summary-disposition-route` (`0.08`):** Conditional on a grant, summary disposition (GVR or summary reversal) is very unlikely (8%). There is no intervening Supreme Court precedent since the Fifth Circuit's June 2026 judgment, and the Court would not summarily reverse an 8–0 circuit consensus on a major Fourth Amendment issue without plenary briefing and oral argument.
- **`dissent-from-denial` (`0.08`):** Conditional on denial, there is a modest (~8%) chance that Justice Gorsuch or Justice Sotomayor (potentially joined by Justice Jackson) writes a dissent from the denial of certiorari or a statement respecting the denial, given the nine amicus briefs and the significance of *Riley* at the border—though none was noted when *Cano*, *Merchant*, or *Anibowei I* (No. 23-199) were denied.
- **`order-writers`:** Per-Justice probabilities of authoring any separate writing on the cert order sum to a small total consistent with the ~8% conditional dissent/statement probability, led by Justice Gorsuch (`0.035`), Justice Sotomayor (`0.025`), Justice Thomas (`0.015`), and Justice Jackson (`0.015`).

---

## 4. Big-Case Score (`0.68`)

If granted and decided on the merits, *Anibowei v. Blanche* would be one of the most consequential Fourth Amendment decisions of the decade—the direct successor to *Riley v. California* (2014) and *Carpenter v. United States* (2018), determining the constitutional rules governing tens of thousands of warrantless electronic device searches at U.S. international airports and ports of entry every year. The 9 cert-stage amicus briefs from major legal and civil-liberties organizations confirm its high public and doctrinal salience (`0.68`).
