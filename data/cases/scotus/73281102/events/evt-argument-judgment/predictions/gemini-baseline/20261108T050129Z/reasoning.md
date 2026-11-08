# Prediction Reasoning: *William Maxwell v. Sandra Dinis, Acting Warden* (No. 25-5930)

- **Case ID**: `scotus/73281102`
- **Event ID**: `evt-argument-judgment` (`stage: merits`, `moment: argued`, `mode: forward`)
- **Snapshot Read**: `2026-11-03.json`
- **P(judgment-disturbed)** (`probability` / `granted`): `0.88` (`1`)
- **Predicted Merits Judgment** (`judgment`): `vacated` (with `predicted_disposition: "other"` per the merits-stage schema contract)
- **Predicted Vote Lineup**: `9-0` (`majority` for all nine Justices, opinion by Justice Kavanaugh)

---

## 1. Provisioned Record and Procedural Posture

This forward-mode merits forecast at the `argued` moment is based on the provisioned snapshot (`2026-11-03.json`), `record/context.json`, `record/argument-features.json`, and all twelve provisioned text files in `record/documents/` listed in `documents.json`: `questions-presented.txt`, `petition.txt`, `appendix.txt`, `brief-in-opposition.txt`, `cert-reply.txt`, `decision-below.txt`, `lower-court-docket.txt`, `merits-brief-petitioner.txt`, `merits-brief-respondent.txt`, `merits-reply-petitioner.txt`, `merits-reply-respondent.txt`, and `argument-transcript.txt`. None of the provisioned documents has `empty_text: true` or `ocr_derived: true`.

Petitioner William Maxwell, a federal prisoner at FCI Beaumont Low, filed a pro se habeas petition under 28 U.S.C. § 2241 seeking accelerated transfer from prison to prerelease custody—a residential reentry center (halfway house) or home confinement—under the First Step Act of 2018 (FSA), 18 U.S.C. §§ 3624(g), 3632(d)(4)(C), and the CARES Act. The district court dismissed the petition for failure to exhaust administrative remedies on the First Step Act claim and rejected the CARES Act claim on the merits.

On appeal, the Fifth Circuit affirmed in a published per curiam opinion (*Maxwell v. Thomas*, 133 F.4th 453 (5th Cir. 2025), provisioned in `decision-below.txt` and `appendix.txt`, matching `lower-court-docket.txt` where rehearing en banc was sought on May 19, 2025 and denied on June 23, 2025). The Fifth Circuit declined to address administrative exhaustion ("We need not address whether Maxwell failed to exhaust his administrative remedies because § 2241 is not the proper vehicle") and held instead, following *Melot v. Bergami*, 970 F.3d 596 (5th Cir. 2020), that transfer to a halfway house or home confinement "would not entitle him to accelerated release, only a change in conditions of confinement" that must be pursued under *Bivens*.

On June 1, 2026 (in OT2025), the Supreme Court granted certiorari limited to Question 1 of the petition: whether a claim regarding application of time credits under the First Step Act seeking accelerated transfer to a halfway house or home confinement can be brought in a habeas petition under 28 U.S.C. § 2241. At the merits stage, the Solicitor General confessed error on the Fifth Circuit's categorical vehicle holding and filed a *Brief for the Respondent Supporting Vacatur* (`merits-brief-respondent.txt`) and reply (`merits-reply-respondent.txt`), agreeing with Petitioner that a claim seeking accelerated release from a prison facility into community prerelease custody (a halfway house or home confinement) based on First Step Act time credits is cognizable in habeas under § 2241, while arguing that the Fifth Circuit's judgment should be vacated and remanded (or alternatively dismissed as improvidently granted) so that alternative defenses—specifically administrative exhaustion and 18 U.S.C. § 3621(b)—can be addressed on remand. The Court appointed Brian W. Barnes as amicus curiae in support of the judgment below.

---

## 2. Base-Rate Anchor (`metrics/statpack.md` Merits Section)

Per the stage contract, `record/context.json`'s cert salience band (`elevated`, `sal-v8`) is a cert-stage construct and is ignored here. Instead, we anchor on the **"The merits docket (granted cases)"** section in `metrics/statpack.md`.

Certiorari in No. 25-5930 was granted on **June 1, 2026**, which places the case in **grant Term OT2025**. Pooling `disturbed` over `parsed` across the grant Terms strictly preceding OT2025 (`2015 <= T < 2025`, rendered in the table as OT2017–OT2024):

- **Pre-guard / post-guard counts and coverage (OT2017–OT2024)**:
  - `granted`: $79 + 56 + 73 + 62 + 80 + 60 + 81 + 58 = 549$
  - `excluded (not in granted)`: $1 + 0 + 1 + 3 + 3 + 2 + 3 + 6 = 19$ (out of 28 total excluded across all grant Terms)
  - `parsed`: $77 + 56 + 73 + 62 + 73 + 58 + 78 + 57 = 534$ (coverage of `parsed` against `granted`: $534 / 549 = 97.3\%$, well above the 30-judgment floor)
- **Pooled strictly-prior disturbed base rate (OT2017–OT2024)**:
  - `disturbed`: $52 + 35 + 51 + 43 + 60 + 46 + 54 + 35 = 376$ of $534$ (**$70.4\%$**)
  - Breakdown of the 534 parsed judgments:
    - `reversed`: $39 + 22 + 24 + 30 + 41 + 33 + 30 + 20 = 239$ ($44.8\%$)
    - `vacated`: $13 + 13 + 27 + 8 + 19 + 11 + 20 + 14 = 125$ ($23.4\%$)
    - `in part` (`affirmed-in-part-reversed-in-part`): $0 + 0 + 0 + 5 + 0 + 2 + 4 + 1 = 12$ ($2.2\%$)
    - `affirmed`: $21 + 17 + 21 + 15 + 13 + 11 + 23 + 21 = 142$ ($26.6\%$)
    - `DIG` (`dismissed-as-improvidently-granted`): $2 + 4 + 1 + 3 + 0 + 1 + 1 + 0 = 12$ ($2.2\%$)
    - `equally divided`: $2 + 0 + 0 + 1 + 0 + 0 + 0 + 1 = 4$ ($0.7\%$)

---

## 3. Adjustments From the Base Rate and Oral Argument Evidence

### A. Quantitative Summary of the Transcript (`record/argument-features.json`)

The deterministic transcript count in `record/argument-features.json` reports:
- **Coverage**: `total_turns: 118`, `attributed_turns: 116`, `unattributed_turns: 2`, `total_words: 6814`, `attributed_words: 3248`, `advocate_words: 3566`, `unattributed_words: 0`, `segments: 4`.
- **By advocate alignment**:
  - `petitioner` (Masha G. Hansford, opening and rebuttal): `21` Justice turns, `652` Justice words (`22` turns / `1,303` words by Hansford).
  - `neither` (Kevin J. Barber, Assistant to the Solicitor General, supporting vacatur): `34` Justice turns, `1,085` Justice words (`33` turns / `1,000` words by Barber).
  - `respondent` (Brian W. Barnes, Court-appointed amicus supporting the judgment below): `61` Justice turns, `1,511` Justice words (`59` turns / `1,263` words by Barnes).
- **Per-Justice totals across all segments** (`turns` / `words`): Roberts (`35` / `762`), Gorsuch (`29` / `1,135`), Sotomayor (`13` / `926`), Kavanaugh (`13` / `513`), Jackson (`11` / `718`), Alito (`8` / `459`), Barrett (`8` / `402`), Thomas (`8` / `214`), Kagan (`5` / `345`).

Court-appointed amicus drew by far the heaviest questioning (`61` turns and `1,511` Justice words—more than double Petitioner's `652` words), and the content of those questions in `argument-transcript.txt` confirms that the bench was almost uniformly skeptical of amicus's defense of the judgment below.

### B. Why `P(judgment-disturbed) = 0.88` and `judgment = "vacated"`

Starting from the `70.4%` strictly-prior merits disturbed base rate, the case record supports a strong upward adjustment to **`0.88`**:

1. **Consensus on the Question Presented Across the Bench**:
   - Neither party defends the Fifth Circuit's holding that a prisoner seeking accelerated transfer from prison to a halfway house or home confinement under the First Step Act cannot proceed under 28 U.S.C. § 2241. Even Court-appointed amicus abandoned the Fifth Circuit's *Bivens* rationale.
   - During amicus's argument, Justices across the ideological spectrum rejected amicus's core contention that home confinement and halfway houses are merely "conditions of confinement" indistinguishable from imprisonment in a prison facility:
     - **Justice Thomas** (Tr. 50–51) challenged amicus's claim that home confinement is imprisonment ("in normal parlance, nobody thinks of sitting in your living room as imprisonment").
     - **Chief Justice Roberts** (Tr. 51–52) pointed to 18 U.S.C. § 3624(g)(5), which provides that if a prisoner violates the conditions of prerelease custody, the BOP Director may revoke prerelease custody and require the prisoner to serve the remainder of his sentence *"in prison"*—observing that this statutory text "strongly suggests that the residential center is not prison."
     - **Justice Gorsuch** (Tr. 10–14, 46–50, 56–59) emphasized historical habeas practice (*In re Bonner*, 151 U.S. 242 (1894), bail, and parole) and pointed out that adopting the Solicitor General's line—that habeas covers claims seeking release *from prison* into community prerelease custody—avoids turning intraprison security transfers into habeas actions.
     - **Justice Kavanaugh** (Tr. 23–24, 59–61) confirmed with Petitioner's counsel that the Court need not decide prison-to-prison transfers (such as supermax to medium security) here, and pressed amicus on the total absence of any alternative judicial remedy if habeas is unavailable (given that *Bivens* does not apply and 18 U.S.C. § 3625 bars APA review).
     - **Justice Kagan** (Tr. 14–15, 61–63) noted that prerelease custody and supervised release replaced federal parole in the Sentencing Reform Act of 1984, making *Preiser v. Rodriguez*, 411 U.S. 475 (1973), directly applicable.
     - **Justice Sotomayor** (Tr. 52–55), **Justice Jackson** (Tr. 17–19, 64–66), and **Justice Barrett** (Tr. 15–17, 21–22, 63–64) similarly rejected amicus's attempt to equate community prerelease custody with prison confinement.

2. **Why `vacated` Over `reversed`**:
   - Within the `0.88` disturbed probability, I assign roughly `0.48` to `vacated` and `0.40` to `reversed`. Because the district court dismissed Maxwell's First Step Act claim for failure to exhaust administrative remedies and the Fifth Circuit expressly bypassed exhaustion to affirm on the threshold § 2241 vehicle rule, the Solicitor General styled its merits filing as a *Brief for the Respondent Supporting Vacatur* so that the Fifth Circuit can address preserved alternative grounds (such as administrative exhaustion) on remand. When the Court rejects a court of appeals' threshold rationale in a posture where the Solicitor General supports vacatur and the lower court may still affirm the dismissal on an unreached threshold defense on remand, `vacated` is the modal judgment form.

3. **Residual Risk (`0.12` Undisturbed: ~`0.08` DIG / ~`0.04` Affirmed)**:
   - The main downside risk to disturbing the judgment below is not an affirmance on the merits (~`0.04`), but a dismissal of the writ as improvidently granted (`dismissed-as-improvidently-granted`, ~`0.08`). Justices Thomas (Tr. 29–30) and Alito (Tr. 19–21, 30–34) asked whether Maxwell's failure to exhaust, his projected January 2027 halfway-house eligibility date, or the government's newly raised argument under 18 U.S.C. § 3621(b) counseled a DIG.
   - However, a DIG remains unlikely (`0.08`): (a) the Solicitor General pushed back against a DIG if the Court is ready to resolve the Question Presented (Tr. 31–33, 39–40), noting the live split across the Fifth and Eighth Circuits (*Fortner v. Eischen*, 170 F.4th 655 (8th Cir. 2026); see also *Osorio-Calderon v. Warden FCI Sandstone*, No. 25-3090 (8th Cir. June 30, 2026)); (b) Justices Sotomayor (Tr. 34–36), Gorsuch (Tr. 36–39), and Jackson (Tr. 41–43) were sharply skeptical of the government's unpreserved § 3621(b) argument on both textual and Suspension Clause grounds; (c) both parties agreed that exhaustion and § 3621(b) should be left for remand; and (d) even if BOP transfers Maxwell to a halfway house in January 2027, his claim for additional earned time credits is not moot because up to 12 months of credits can be applied toward early supervised release under 18 U.S.C. §§ 3624(g)(3) and 3632(d)(4)(C).

---

## 4. Per-Justice Votes and Authorship (`votes` and `claim_distributions`)

From `metrics/statpack.md`'s **"Per-Justice merits votes (complete lineups)"** section, pooling the Terms strictly before this case's OT2025 grant Term (OT2020–OT2024 rendered in the pack):

- **Roberts**: Sat in `238` complete lineups (`53 + 48 + 46 + 51 + 40`); voted `with judgment` in `224 / 238` (`94.1%`: `51/53`, `46/48`, `44/46`, `47/51`, `36/40`); voted to `disturb` in `161 / 230` plain judgments (`70.0%`: `39/52`, `29/46`, `31/44`, `36/49`, `26/39`).
- **Kavanaugh**: Sat in `238` complete lineups; `with judgment` in `227 / 238` (`95.4%`: `50/53`, `46/48`, `45/46`, `48/51`, `38/40`); `disturb` in `167 / 230` (`72.6%`: `40/52`, `31/46`, `32/44`, `36/49`, `28/39`).
- **Barrett**: Sat in `232` complete lineups (`53 + 48 + 46 + 49 + 36`); `with judgment` in `211 / 232` (`90.9%`: `48/53`, `43/48`, `43/46`, `45/49`, `32/36`); `disturb` in `152 / 222` (`68.5%`: `36/50`, `30/46`, `28/44`, `34/47`, `24/35`).
- **Gorsuch**: Sat in `236` complete lineups (`51 + 48 + 46 + 51 + 40`); `with judgment` in `183 / 236` (`77.5%`: `38/51`, `37/48`, `37/46`, `38/51`, `33/40`); `disturb` in `153 / 224` (`68.3%`: `28/49`, `33/46`, `33/43`, `36/49`, `23/37`).
- **Alito**: Sat in `235` complete lineups (`52 + 47 + 46 + 51 + 39`); `with judgment` in `188 / 235` (`80.0%`: `40/52`, `39/47`, `37/46`, `42/51`, `30/39`); `disturb` in `139 / 224` (`62.1%`: `30/51`, `27/45`, `30/43`, `32/48`, `20/37`).
- **Thomas**: Sat in `238` complete lineups; `with judgment` in `187 / 238` (`78.6%`: `42/53`, `38/48`, `36/46`, `41/51`, `30/40`); `disturb` in `140 / 229` (`61.1%`: `32/52`, `28/46`, `26/44`, `32/49`, `22/38`).
- **Kagan**: Sat in `238` complete lineups; `with judgment` in `181 / 238` (`76.1%`: `44/53`, `34/48`, `37/46`, `35/51`, `31/40`); `disturb` in `154 / 225` (`68.4%`: `35/50`, `30/46`, `30/44`, `32/47`, `27/38`).
- **Sotomayor**: Sat in `238` complete lineups; `with judgment` in `172 / 238` (`72.3%`: `41/53`, `34/48`, `37/46`, `30/51`, `30/40`); `disturb` in `151 / 224` (`67.4%`: `36/50`, `30/46`, `28/44`, `31/47`, `26/37`).
- **Jackson**: Sat in `147` complete lineups in OT2022–OT2024 (`53 + 48 + 46`); `with judgment` in `112 / 147` (`76.2%`: `38/53`, `36/48`, `38/46`); `disturb` in `96 / 140` (`68.6%`: `37/50`, `32/46`, `27/44`).

Because Petitioner agreed at oral argument (Tr. 13–14, 24–25) to the narrow rule favored by Justices Gorsuch, Kagan, Barrett, and Kavanaugh—holding only that claims seeking accelerated transfer *out of a prison facility* into community prerelease custody (a halfway house or home confinement) are cognizable under § 2241, while leaving intraprison transfers undecided and remanding alternative defenses—all nine Justices are predicted to vote `majority` (`9-0`).

- **Majority Author (`majority-author`)**: **Justice Kavanaugh** (`0.22`) is the modal assignment choice for a crisp, unanimous opinion adopting the narrow consensus rule and remanding alternative arguments, followed by **Justice Gorsuch** (`0.17`), **Justice Kagan** (`0.14`), **Justice Barrett** (`0.12`), and **Chief Justice Roberts** (`0.11`).
- **Separate Writers (`separate-writers`)**: Separate writing probabilities are modest because the narrow consensus opinion deliberately avoids reaching either intraprison transfers or the unpreserved § 3621(b) issue. **Justice Alito** (`0.28`) and **Justice Thomas** (`0.22`) are the most likely to write a brief concurrence emphasizing that exhaustion and § 3621(b) remain open on remand or noting the limits of habeas, while **Justice Gorsuch** (`0.18`) or **Justice Jackson** (`0.15`) could write separately on the historical scope of habeas or why § 3621(b) does not bar time-credit claims.
