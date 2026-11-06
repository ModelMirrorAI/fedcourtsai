# Rationale for Certiorari Prediction: *New Mexico v. Samuel Neal*, No. 26-37

**Prediction**: `denied` (`granted: 0`, `probability: 0.08`, `big_case_score: 0.15`)

---

## 1. Base-Rate Anchor and Docket Signals

Per `record/context.json`, this cell runs in `forward` mode at `moment: distribution` (`cutoff: null`, `snapshot_date: "2026-11-06"`, `snapshot_provenance: "as-stored"`). The petition is assigned to the `state` salience band under `sal-v7`, and `context.json` provides the frozen pre-Term pooled anchor:
- **`cert_anchor.rate` = 0.2333** (23.33% across `lookback_terms: 10`, corresponding to the `state` band's bracketed `reached` rate in `metrics/statpack.md` across OT2017–OT2025: 30.0% in OT2025 [n=30], 31.6% in OT2024 [n=38], 18.8% in OT2023 [n=32], 13.9% in OT2022 [n=36], 21.9% in OT2021 [n=96], 38.6% in OT2020 [n=44], 15.4% in OT2019 [n=52], 23.8% in OT2018 [n=42], and 20.0% in OT2017 [n=50]).

We cross-check this anchor against the marginal cuts in `metrics/statpack.md` and `metrics/statpack.json`, as well as the specific docket history in `record/snapshots/2026-11-06.json`:
1. **Docket Trajectory (Waiver Followed by Call for a Response)**:
   - The State of New Mexico filed its paid cert petition on July 6, 2026 (docketed July 9, 2026).
   - Respondent Samuel Neal waived his right to respond on July 24, 2026, and the petition was distributed once (`distribution_count: 1`) on August 19, 2026 for the September 28, 2026 Long Conference.
   - On **August 26, 2026**, the Court issued a **Call for a Response (CFR)** (`Response Requested. (Due September 25, 2026)`).
   - Thereafter, Respondent retained Supreme Court specialist counsel (Derek C. Reinbold of Kellogg, Hansen, Todd, Figel & Frederick, P.L.L.C., appearing alongside New Mexico Public Defender counsel Joelle N. Gonzales) and obtained two extensions of time to file the Brief in Opposition, currently due **November 25, 2026**.
   - While a CFR confirms that at least one chambers flagged the petition rather than letting it be denied off a waiver at the Long Conference, the bar for a CFR on a state attorney general's petition is low, and the `state` band's 23.33% historical grant rate already encompasses state petitions that receive opposition briefing.
2. **Zero Amicus Support (`amicus_briefs: null` / 0 entries)**:
   - Under Rule 37.2, cert-stage amicus briefs supporting Petitioner were due 30 days after docketing (August 10, 2026). None were filed—not a single other state joined or supported New Mexico's petition. In `metrics/statpack.md`'s `"Cert petitions by amicus-brief count (paid scored segment)"` table, petitions with `0` amicus briefs (n=11,109 resolved) have a 95.0% denial rate (2.0% granted, 1.8% GVR), compared to 10.1% granted / 4.7% GVR for `1` amicus brief (n=1,158) and 18.2% granted / 4.5% GVR for `2+` amicus briefs (n=1,446).
3. **Originating Court Track Record**:
   - In `metrics/statpack.json`, petitions from the **Supreme Court of New Mexico** over the 10-Term window are **0 for 13** (13 resolved, 100.0% denied).

---

## 2. Analysis of Provisioned Filings (`questions-presented.txt` and `petition.txt`)

We read `record/documents/questions-presented.txt`, `record/documents/documents.json`, and the full text of `record/documents/petition.txt` (including the New Mexico Supreme Court's unanimous opinion in *State v. Neal*, App. 1a–41a, and the New Mexico Court of Appeals' opinion, App. 42a–64a; note that `petition.txt` has a pipeline truncation note near the very end of the statutory appendix at PDF pages 113–116, after all opinions and orders). No Brief in Opposition is in `record/documents/` because it is not due until November 25, 2026.

Even evaluated solely from the Petition and the opinions in its appendix, the case suffers from three severe vehicle and jurisdictional defects that experienced opposition counsel (Kellogg Hansen) will highlight in the forthcoming Brief in Opposition:

### A. Dual Federal/State Constitutional Citation and *Michigan v. Long* / Advisory-Opinion Risk
In declining the State's invitation to overrule its double-jeopardy precedent, the New Mexico Supreme Court explicitly invoked **both** the federal and state constitutions:
> `"Absent such express language, we conclude the current test honors the mandate of the double jeopardy clause contained within both the United States and New Mexico Constitutions—that no person shall 'be twice put in jeopardy' for the same offense. U.S. Const. amend. V; N.M. Const. art. II, § 15."` (App. 40a, ¶ 44; see also App. 9a, ¶ 11).

Although the Petition argues (Pet. 28–31) that the decision below lacks an explicit *Michigan v. Long*, 463 U.S. 1032 (1983), plain statement and is interwoven with federal precedent, this dual reliance poses a classic cert-stage deterrent: even if the Supreme Court had formal jurisdiction under *Michigan v. Long*, the New Mexico Supreme Court could reinstate the exact same outcome on remand under Article II, Section 15 of the New Mexico Constitution.

### B. Authoritative State-Law Statutory Construction and State-Law Rule of Lenity (*Missouri v. Hunter*)
In *Missouri v. Hunter*, 459 U.S. 359, 366–68 (1983), the Supreme Court held that with respect to **cumulative sentences imposed in a single trial**, the Double Jeopardy Clause "does no more than prevent the sentencing court from prescribing greater punishment than the legislature intended," and federal courts are bound by a state supreme court's construction of its own legislature's intent.

Here, the New Mexico Supreme Court did not merely examine whether Neal's trial conduct was unitary. In Part II.A.4.b (`Legislative intent`, App. 20a–26a, ¶¶ 22–29), the court examined the statutory text, sentencing structure, and 2003 amendment history of New Mexico's kidnapping statute, NMSA 1978, § 30-4-1(B), and second-degree criminal sexual penetration (CSP II) statute, NMSA 1978, § 30-9-11(E)(3):
- It noted that the 2003 amendment to § 30-4-1(B) specifically added `"a sexual offense"` as an aggravating circumstance that elevates kidnapping from a second-degree felony (9-year basic sentence) to a first-degree felony (18-year basic sentence), and concluded from the statutory structure that `"the Legislature intended for the sexual offense to serve essentially as a base offense rather than an independent crime in cases where only one sexual offense is presented"` (App. 22a–24a, ¶¶ 24–25).
- It then applied New Mexico's state-law **rule of lenity** (*Swafford v. State*, 1991-NMSC-043, ¶ 34 & n.8; *State v. Montoya*, 2013-NMSC-020, ¶ 51) to resolve any remaining ambiguity in legislative intent against multiple punishments (App. 25a–26a, ¶ 28)—a state-law canon that the Petition itself concedes (Pet. 8) `"expressly departed from this Court's jurisprudence."`

Because a state supreme court's determination of state legislative intent and application of a state-law rule of lenity in a single-trial cumulative-punishment case is a matter of state law under *Missouri v. Hunter*, the U.S. Supreme Court cannot revise the New Mexico Supreme Court's reading of NMSA 1978, § 30-4-1(B).

### C. The State's Oral-Argument Concession Below and the State-Law *Foster* General-Verdict Presumption
The Petition's core premise—that Neal's convictions for first-degree kidnapping and CSP II would survive an abstract or charging-document *Blockburger* comparison—is contradicted by the State's own concession in the court below:
1. Under NMSA 1978, § 30-4-1(B), kidnapping is a divisible compound statute that is elevated to a first-degree felony if the defendant inflicts `"physical injury or a sexual offense upon the victim."` Just as felony murder in *Whalen v. United States*, 445 U.S. 684, 693–94 (1980), subsumed the predicate rape offense when rape was the predicate felony, first-degree kidnapping predicated on inflicting `"a sexual offense"` incorporates and subsumes the lone underlying sexual offense.
2. As the New Mexico Supreme Court expressly recorded (App. 18a–19a, ¶ 21; Pet. 15), **the State conceded at oral argument below** `"that the elements of CSP II would be subsumed by kidnapping if the jury relied on a sexual offense, which was one of the two kidnapping theories the State presented to the jury."`
3. Why, then, did the New Mexico Supreme Court treat the kidnapping conviction as resting on the `"sexual offense"` alternative rather than the `"physical injury"` alternative? Because the jury instructions submitted *both* alternatives (`"physical injury or a sexual offense"`) in a general verdict without a special verdict form, triggering New Mexico's state-law ***Foster* presumption** (*State v. Foster*, 1999-NMSC-007, ¶ 28; *State v. Olguin*, 1995-NMSC-077, ¶ 2, which expressly departs from *Griffin v. United States*, 502 U.S. 46 (1991), on state-law grounds). The Petition does not ask the Court to review *Foster* or *Olguin*.

### D. Weakness of the Alleged Split and Partial Relief Below
- Most of the federal circuit decisions cited in the Petition's three-way split are decades old (dating from 1980 to 2009), and the Petition cites the Eleventh Circuit on *both* sides of its split (Pet. i, 17–18).
- The Petition acknowledges (Pet. 1, 17) that New Mexico is a one-state outlier in looking to trial evidence as part of its two-step *Swafford* framework.
- Moreover, the unanimous (5–0) New Mexico Supreme Court actually **ruled in the State's favor** on the third-degree aggravated battery count, reversing the Court of Appeals in part and reinstating that conviction alongside the 18-year first-degree kidnapping conviction (for a 21-year sentence).

---

## 3. Calibration of Claims and Uncertainties

- **`probability` / `disposition` = `0.08`**: Starting from the `state` band anchor of `0.2333`, we weight the positive signal of the August 26, 2026 Call for a Response against the complete lack of amicus support (`0` briefs), the 0-for-13 New Mexico Supreme Court base rate, the retention of top Supreme Court opposition counsel (Kellogg Hansen), and the severe *Missouri v. Hunter*, *Michigan v. Long*, and state-concession/*Foster* vehicle defects. An 8% grant probability (`granted: 0`, `predicted_disposition: "denied"`) reflects the small residual chance that four Justices overlook these state-law entanglements to address *Blockburger*/*Whalen* methodology.
- **`relist-increment` = `0.97`**: Because the snapshot shows 1 distribution (August 19, 2026) followed by a Call for a Response (August 26, 2026) with the Brief in Opposition due November 25, 2026, the petition will almost certainly be distributed at least once more (`distribution_count >= 2`) once the Brief in Opposition is filed.
- **`cvsg-increment` = `0.005`**: Virtually zero chance of a CVSG in a state-court criminal prosecution with no federal interest.
- **`summary-disposition-route` = `0.12`**: Conditional on a grant, plenary review (`0.88`) is far likelier than a summary reversal or GVR (`0.12`), given the absence of any intervening Supreme Court precedent for a GVR and the complex framing of the Question Presented.
- **`dissent-from-denial` = `0.04`** and **`order-writers`**: Conditional on denial, a clean denial is the modal expectation (`0.96`), with a 4% chance that one of the Justices who called for a response (most likely Justice Alito [`0.015`], Justice Thomas [`0.015`], or Justice Gorsuch [`0.008`]) writes a dissent or statement respecting denial.
- **Main Uncertainties**: Because the Brief in Opposition is not due until November 25, 2026, we cannot yet read Respondent's exact framing, though the presence of Kellogg Hansen as Counsel of Record makes it virtually certain that the *Missouri v. Hunter*, *Michigan v. Long*, and oral-argument concession points on the face of the New Mexico Supreme Court's opinion will be thoroughly briefed.
