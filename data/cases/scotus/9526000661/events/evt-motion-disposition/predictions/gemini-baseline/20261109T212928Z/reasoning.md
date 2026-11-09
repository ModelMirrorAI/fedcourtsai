# Predictor Rationale (`scotus/9526000661`, `evt-motion-disposition`)

## 1. Summary of Call

- **Predicted disposition:** `denied` (`granted: 0`, `probability: 0.03`)
- **Stage and moment:** `interim`, `moment: arrival` (`evt-motion-disposition`, forward mode, `cut_kind: "arrival-position"`, `cut_anchor_index: 0`)
- **Input snapshot and documents read:** `data/cases/scotus/9526000661/record/snapshots/2026-11-09.json` (`input_snapshot: "2026-11-09.json"`) and `data/cases/scotus/9526000661/record/documents/application.txt` (10 pages, `truncated: false`, `ocr_derived: false`, `empty_text: false`).

## 2. Base-Rate Anchoring (`metrics/statpack.md` and `metrics/statpack.json`)

This is an interim-stage arrival cell in October Term 2026 (`26A661`). In `record/context.json`, `band` is `null` (as expected for an application docket). Per the interim-stage anchoring rules, I anchor on **"The interim docket (applications)"** section of `metrics/statpack.md` (and `metrics/statpack.json`):

1. **Scored 10-Term Pooled Baseline (`2016 <= T < 2026`):**
   - Pooling `finer_granted` over `finer_resolved` (partial grants counted as granted, moot dismissals excluded from both numerator and denominator, `finer_unread = 0` in every pooled Term) across the ten application-Terms strictly preceding OT2026 (**OT2016–OT2025**) yields **156 granted out of 1,337 resolved substantive applications (`11.7%`, specifically `11.67%`)**. This easily clears the pre-registered `INTERIM_BASE_RATE_MIN_RESOLVED = 50` floor.
   - Across all 11 parsed historical Terms strictly before OT2026 (**OT2015–OT2025**, adding OT2015's `12 / 113`), the pooled finer rate is **168 / 1,450 (`11.59%`, or `11.6%`)**. (Note: `unparsed` is `1` in OT2015–OT2017 and `0` in OT2018–OT2025, while OT2014 and earlier are `100%` unparsed with `0` resolved substantive rows.)
2. **Applicant-Class and Capital-Marking Conditioning ("Substantive applications by applicant class"):**
   - The statpack splits the 10-Term OT2016–OT2025 substantive resolved pool (`156 / 1,337 = 11.7%`) by applicant class (`caption-v2`) and capital marking.
   - While federal (`46 / 65 = 70.8%`) and state (`37 / 78 = 47.4%`) applicants succeed at high rates, **private** applicants overall succeed at only **6.1% (`73 / 1,194`)**.
   - Within the exact cell matching this application—**`private` applicant + `capital` marking**—the 10-Term historical grant rate (OT2016–OT2025) is **3.5% (`10 / 288`)**, compared with `7.0% (63 / 906)` for non-capital private applicants.
   - Moreover, inspecting the per-Term `applicant_cuts` in `metrics/statpack.json` shows a sharp recent decline in private capital stay grants:
     - **OT2025:** `0 / 44` (`0.0%`)
     - **OT2024:** `0 / 44` (`0.0%`)
     - **OT2023:** `1 / 38` (`2.6%`)
     - **OT2022:** `1 / 33` (`3.0%`)
     - **OT2021:** `2 / 26` (`7.7%`)
     - **OT2020:** `0 / 16` (`0.0%`)
     - (And in **OT2026** to date, outside the strictly-prior anchor: `0 / 19`.)
   - Thus, while the evaluator scores Brier skill against the unconditioned 10-Term substantive pool (`11.7%`), the empirical base rate for a private capital stay application is **3.5% over 10 Terms** and **0.6% (`1 / 159`) over the four most recent prior Terms (OT2022–OT2025)**.
3. **Escalation-Signal Context:**
   - At `moment: arrival` (`cut_kind: "arrival-position"`, `cut_anchor_index: 0`), the application has not yet climbed any rung of the escalation ladder (`response_requested: false`, `referred_to_court: false`, `amicus_briefs: 0`).
   - Across all 1,612 substantive applications in the statpack (1,496 strictly before OT2026), `response_requested` appears on `313 / 1,612` (`19.4%`; `293 / 1,496 = 19.6%` strictly before OT2026) and `referred_to_court` appears on `874 / 1,612` (`54.2%`; `841 / 1,496 = 56.2%` strictly before OT2026).

## 3. Case-Specific Adjustments from the Provisioned Record and Prior Proceedings

Reading `record/documents/application.txt` alongside the prior published decisions in Pavatt's and his co-defendant Brenda Andrew's cases (*Pavatt v. State*, 2007 OK CR 19, 159 P.3d 272; *Pavatt v. Carpenter*, 928 F.3d 906 (10th Cir. 2019) (en banc), *cert. denied sub nom. Pavatt v. Sharp*, 140 S. Ct. 958 (2020); *Andrew v. White*, 604 U.S. 86 (2025)) confirms that the probability of a stay should remain near the private-capital base rate at **`0.03` (3.0%)**:

1. **High Doctrinal Hurdle on the Question Presented (*Peña-Rodriguez* Extension):**
   - Pavatt seeks a stay of his November 12, 2026 execution pending certiorari (`26-6095`) from the Oklahoma Court of Criminal Appeals' denial of successive post-conviction relief (`PCD-2026-827`). His central constitutional claim asks the Court to recognize a new Sixth and Fourteenth Amendment exception to Oklahoma's no-impeachment rule (Okla. Stat. tit. 12, § 2606(B)), analogous to *Peña-Rodriguez v. Colorado*, 580 U.S. 206 (2017), so that he can rely on an affidavit from jury foreman Mark Haydon stating that the prosecution's sentencing-phase argument—that Pavatt personally fired both shots from the single-shot 16-gauge shotgun—was decisive in persuading holdout jurors to impose a death sentence.
   - In *Peña-Rodriguez*, 580 U.S. at 221–25, the Court went to great lengths to distinguish *Tanner v. United States*, 483 U.S. 107 (1987), and *Warger v. Shauers*, 574 U.S. 40 (2014), holding that the no-impeachment rule yields only to clear statements of racial animus because racial bias is a unique historical evil that cannot readily be policed through *voir dire* or courtroom observation.
   - Here, by contrast, the prosecutor's closing argument occurred in open court on the trial record, and any due-process claim that the State knowingly presented or argued false evidence (*Mooney v. Holohan*, 294 U.S. 103 (1935); *Napue v. Illinois*, 360 U.S. 264 (1959); *Donnelly v. DeChristoforo*, 416 U.S. 637 (1974)) is governed by an **objective** materiality standard that neither requires nor permits probing individual jurors' subjective deliberative processes. Four Justices are extremely unlikely to grant certiorari to expand *Peña-Rodriguez* into a general due-process exception for juror affidavits assessing the subjective impact of prosecutorial arguments.
2. **Successive Post-Conviction Posture and Cumulative Record:**
   - Pavatt was convicted and sentenced to death for the November 20, 2001 murder of Rob Andrew, and his direct appeal and initial federal habeas proceedings concluded more than six years ago (*Pavatt v. Sharp*, 140 S. Ct. 958 (2020)). The current application arises from a successive state post-conviction proceeding (`PCD-2026-827`) filed shortly before his scheduled execution.
   - As summarized in *Pavatt v. Carpenter*, 928 F.3d at 911–13, the trial record contained extensive evidence of Pavatt's guilt and culpability, including his own confession to shooting Rob Andrew, his purchase of the .22 firearm used to stage Brenda Andrew's superficial gunshot wound, his forging of life-insurance documents and cutting of Rob Andrew's brake lines prior to the murder, and his flight to Mexico with Brenda Andrew. Even setting aside the no-impeachment rule, the Court rarely grants eleventh-hour stays of execution to review fact-bound materiality and diligence determinations from successive state post-conviction orders.
3. **Why `probability = 0.03` Rather Than Lower:**
   - I retain a 3.0% probability (rather than <1%) for two reasons: (a) the Supreme Court has recent familiarity with the underlying crime from co-defendant Brenda Andrew's case (*Andrew v. White*, 604 U.S. 86 (2025)), where the Court summarily vacated and remanded on a prosecutorial due-process claim (albeit one preserved on initial federal habeas review and involving pervasive gender/sexual character evidence, which the Tenth Circuit ultimately held harmless on remand on January 13, 2026); and (b) Pavatt's application is represented by institutional capital habeas counsel (the Federal Public Defender's Capital Habeas Unit for the Western District of Oklahoma) and pairs the juror-impeachment question with an allegation of newly discovered evidence showing that the prosecution's two-shot theory was false.

## 4. Rationale for `interim-v3` Claims and `order-writers` Distribution

- **`interim-disposition` (`0.03`):** Matches top-level `probability = 0.03` as required.
- **`response-requested-increment` (`0.15`):** Although the overall substantive-application rate for `response_requested` is `19.4%` (`19.6%` pre-OT2026), in capital execution stays filed three days before an execution (`Nov. 9` filing for a `Nov. 12` execution), the State of Oklahoma routinely files its response brief immediately under the Court's capital-case protocol without a separate docket entry showing a formal call for a response (as seen in corpus prior `scotus/73281280`, *Michael L. King v. Florida*, `25A1000`, where `referred_to_court` was `true` and `response_requested` was `false`). I therefore set `response-requested-increment` slightly below the overall substantive average at `0.15`.
- **`referral-increment` (`0.88`):** Unlike ordinary non-capital stay applications (where `referred_to_court` is `54.2%` overall), last-minute capital stay-of-execution applications are almost always referred by the Circuit Justice (here Justice Gorsuch) to the full Court so that the full bench acts on the stay alongside the linked certiorari petition (`26-6095`). I set `referral-increment` at `0.88`.
- **`amicus-increment` (`0.04`):** Only `6.9%` (`112 / 1,612`) of substantive applications in the statpack attract amicus filings, and compressed three-day execution-week applications in successive state post-conviction proceedings rarely draw amicus briefs.
- **`order-writers`:** Most capital stay denials carry no separate writing. Where a separate writing occurs on a capital post-conviction stay denial involving *Napue* / Sixth Amendment claims, Justice Sotomayor (`0.06`) and Justice Jackson (`0.04`) are the most frequent authors, with smaller probabilities for Justice Kagan (`0.02`), Justice Gorsuch (`0.02`), Justice Thomas (`0.01`, author of the dissent in *Andrew v. White*, 604 U.S. 86 (2025)), Justice Alito (`0.01`), and `0.005` each for Chief Justice Roberts, Justice Kavanaugh, and Justice Barrett.

## 5. Main Uncertainties

- The primary uncertainty is that the Oklahoma Court of Criminal Appeals' slip opinion in `PCD-2026-827` and the linked certiorari petition (`26-6095`) are not separately staged in `record/documents/` (only the 10-page stay application `application.txt` is staged, which summarizes the ruling below). If the OCCA decision rested exclusively on an independent and adequate state procedural bar (such as Oklahoma's successive post-conviction bar, Okla. Stat. tit. 22, § 1089(D)(8)) without reaching the federal *Peña-Rodriguez* / *Napue* merits, the likelihood of a stay is even lower than 3%.
