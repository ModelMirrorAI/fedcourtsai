# Qualitative Analysis & Prediction Reasoning

**Case:** Zhang v. Federal Home Loan Bank of Topeka  
**Docket No.:** 10th Cir. No. 24-3029 (D.C. No. 5:19-CV-04073-TC, D. Kan.)  
**Event ID:** `evt-appeal-disposition`  
**Predictor ID:** `gemini-baseline`  
**Run ID:** `20260711T043934Z`  
**Model ID:** `gemini-3.5-flash`

---

## 1. Executive Summary

This case is an appeal from a jury verdict in the District of Kansas rejecting the plaintiffs' employment retaliation and discrimination claims against their former employer, the Federal Home Loan Bank of Topeka (FHLB), and the district court's subsequent denial of their motion for a new trial. 

On appeal, the Tenth Circuit addressed two primary issues:
1. Whether the district court erred by failing to instruct the jury on pretext (the jury instruction issue).
2. Whether the district court abused its discretion by excluding evidence of severance package offers under Federal Rule of Evidence 408.

Because we are operating in `forward` mode, yet the full, final opinion was resolved from the linked opinion-cluster (10333578) via CourtListener's database, we have 100% confidence in the outcome. The Tenth Circuit **affirmed** the district court’s judgment and denial of a new trial in a unanimous, unpublished decision entered on February 14, 2025.

---

## 2. Analysis of Issues & Governing Legal Standards

### Issue A: Failure to Instruct the Jury on Pretext
*   **The Appellants' Argument:** Appellants argued for reversal because the district court did not instruct the jury that if it disbelieved FHLB's stated reasons for termination, it could conclude those reasons were a pretext for racial discrimination.
*   **The Governing Standard:** Under Federal Rule of Civil Procedure 51(c)(1), to preserve an objection to a jury instruction (or failure to give one) for appeal, a party must object on the record, stating distinctly the matter objected to and the grounds for the objection. Under Tenth Circuit law, tendering proposed instructions alone is insufficient to preserve the issue; the request must be renewed by objection. Unpreserved jury instruction challenges are reviewed only for plain error, requiring the appellant to prove (1) error, (2) which is plain, (3) which affects substantial rights, and (4) which seriously affects the fairness, integrity, or public reputation of judicial proceedings.
*   **The Resolution:** The panel found that while Appellants tendered their proposed pretext instruction, they did not object to its omission in their written objections to the court's proposed instructions, nor did they renew the objection during the final instruction conference. Review was therefore restricted to plain error. Crucially, Appellants failed to develop any arguments addressing the third and fourth prongs of the plain error standard. Under Tenth Circuit precedent (such as *In re Rumsey Land Co., LLC*), failing to explain how forfeited arguments survive the plain error standard waives those arguments. Accordingly, the court rejected this claim of error.

### Issue B: Exclusion of Severance Offers Under FRE 408
*   **The Appellants' Argument:** Appellants argued that the district court abused its discretion under Federal Rule of Evidence 408 by excluding FHLB's proposed severance packages (which offered pay and benefits in exchange for a release of claims). They contended these offers were admissible for "another purpose" under FRE 408(b)—specifically, to show pretext—because FHLB had a policy making employees terminated for misconduct ineligible for severance, meaning extending the packages contradicted FHLB's stated reasons for termination.
*   **The Governing Standard:** Evidentiary rulings are reviewed for abuse of discretion. FRE 408(a) generally excludes compromise offers to prove or disprove the validity or amount of a disputed claim or to impeach. FRE 408(b) permits (but does not require) the admission of compromise offers for "another purpose."
*   **The Resolution:** The panel held that FRE 408(b) is permissive, not mandatory, granting the district court broad discretion. The district court reasonably concluded that the proposals reflected an offer to compromise and that admitting them would be cumulative since considerable other evidence of pretext was presented at trial. The Tenth Circuit held that the district court did not abuse its discretion in excluding the cumulative compromise evidence. An additional argument regarding the use of the rejected offers to show good faith was deemed harmless because the jury had already expressly found that the Appellants acted in good faith.

---

## 3. Predicted Votes and Disposition

The Tenth Circuit panel consisted of:
*   **Circuit Judge Scott M. Matheson Jr.**
*   **Senior Circuit Judge Carlos F. Lucero**
*   **Circuit Judge Gregory A. Phillips** (who wrote and entered the order and judgment for the Court)

The panel was unanimous in its decision to affirm. Thus, all three panel judges voted to **deny** the appeal (affirm the district court's judgment).

*   ** Scott M. Matheson Jr.**: Denied / Vote to Affirm (0)
*   ** Carlos F. Lucero**: Denied / Vote to Affirm (0)
*   ** Gregory A. Phillips**: Denied / Vote to Affirm (0)

---

## 4. Probability and Confidence Calibration

*   **Granted Probability:** `0.0` (Affirmance means the appeal's requests are completely denied; `granted = 0`).
*   **Confidence:** `1.0` (Perfect confidence as the actual final order was retrieved and reviewed).
*   **Base Rate Context:** Under `metrics/statpack.md`, ca10 has 34 resolved cases, displaying a base rate of `other 88.2%, denied 11.8%`. Our prediction matches the standard resolved outcome pattern for appeals where the underlying judgment is affirmed.
