# Certiorari Prediction: *The Nielsen Company (US), LLC v. Cumulus Media New Holdings Inc.* (No. 26-370)

## Summary of Prediction

- **Predicted Disposition:** `denied`
- **Grant Probability (`granted: false`):** `0.01` (1.0%)
- **Confidence:** Very High

We predict that the Supreme Court will deny the petition for a writ of certiorari. Although Petitioner (represented by experienced Supreme Court counsel at Gibson, Dunn & Crutcher LLP and supported by two cert-stage *amicus* briefs from the Chamber of Commerce and the Washington Legal Foundation) frames an important antitrust question regarding "constructive tying" and above-cost bundled pricing under Section 2 of the Sherman Act, the procedural posture and docket signals overwhelmingly point toward denial. Most critically, Respondent Cumulus Media waived its right to file a brief in opposition on October 15, 2026, and the petition was distributed on October 28, 2026 for the November 13, 2026 Conference without a response having been requested. Under Supreme Court practice, the Court virtually never grants certiorari on a paid petition without first calling for a response (CFR). Furthermore, the case arises in an interlocutory posture from a preliminary injunction while a related enforcement appeal remains actively pending in the Second Circuit, making it an unsuitable vehicle for plenary review at this stage.

---

## 1. Baseline & Procedural Signals

### Base Rate Anchor
From the 10-Term `statpack.md` empirical baseline (OT2016–OT2025), the overall certiorari grant rate across 49,950 decided petitions is **2.1%**, and for the **Paid** docket (14,894 petitions) it is **6.2%**. For petitions originating from the **Second Circuit**, the overall grant rate is **2.0%** (74 of 3,661), and the paid cert grant rate is **4.9%** (52 of 1,069). The `context.json` cert anchor for the baseline band is **5.09%**.

### Waiver of Brief in Opposition & First Distribution Without CFR
The single strongest procedural signal on the October 31, 2026 docket snapshot is the sequence of filings leading to distribution:
1. **Sept. 17, 2026:** Petition for a writ of certiorari filed.
2. **Oct. 15, 2026:** Waiver of right of respondent Cumulus Media New Holdings Inc. to respond filed.
3. **Oct. 16 & Oct. 19, 2026:** Amicus briefs filed by Washington Legal Foundation and the Chamber of Commerce of the United States of America.
4. **Oct. 28, 2026:** `DISTRIBUTED for Conference of 11/13/2026.` (`distribution_count: 1`, `response_requested: false`, `response_filed: false`, `cvsg: false`).

In modern Supreme Court practice, the Court does not grant plenary review (or summarily reverse) when the respondent has waived the brief in opposition without first requesting a response and relisting the case after the brief in opposition is filed. According to the 10-Term `statpack.md` distribution-count table:
- Petitions resolved after **1 distribution** have a grant rate of **0.2%** (84 of 44,581 overall; and on the paid docket, 79 of 11,481, or **0.7%**, virtually all of which had a brief in opposition filed voluntarily before first distribution).
- Even if a Justice were to call for a response (CFR) before or at the November 13, 2026 Conference, only a minority of CFR'd cases ultimately result in a grant of certiorari.

---

## 2. Analysis of the Merits & Certworthiness Arguments

### The Question Presented and Alleged Circuit Split
Petitioner asks whether a seller that offers two products separately and in a bundle, at prices never alleged to be below cost, may be held liable under Section 2 of the Sherman Act for a "constructive tie" because a court deems the standalone price of the tying product too high relative to a discounted bundle.

Petitioner contends that the Second Circuit's recognition of "constructive tying" conflicts with:
1. **Supreme Court Precedent on Above-Cost Pricing:** *Brooke Group Ltd. v. Brown & Williamson Tobacco Corp.*, 509 U.S. 209 (1993), *Verizon Communications Inc. v. Law Offices of Curtis V. Trinko, LLP*, 540 U.S. 398 (2004), and *Pacific Bell Telephone Co. v. linkLine Communications, Inc.*, 555 U.S. 438 (2009), which generally insulate unilateral above-cost pricing from antitrust liability and caution against placing federal courts in the role of ongoing rate regulators.
2. **Sixth and Ninth Circuit Precedent on Bundled Discounts:** *Cascade Health Solutions v. PeaceHealth*, 515 F.3d 883 (9th Cir. 2008), and * Collins Inkjet Corp. v. Eastman Kodak Co.*, 781 F.3d 264 (6th Cir. 2015), which apply a discount-attribution cost test ("whether, when the full amount of the discount on the bundled offering is allocated to the competitive product, the resulting price is below the seller's incremental cost of producing the competitive product").
3. **Other Circuits' Skepticism of Pricing-Based Tying:** *Aerotec International, Inc. v. Honeywell International, Inc.*, 836 F.3d 1171 (9th Cir. 2016), and *Schor v. Abbott Laboratories*, 457 F.3d 608 (7th Cir. 2006).

### Countervailing Considerations Weighing Against Certiorari
While the intersection of bundled discounting, constructive tying, and *linkLine*/*PeaceHealth* is an area of genuine academic and doctrinal interest in antitrust law, several features of the Second Circuit's decision substantially weaken the case for certiorari:

1. **Fact-Bound Express-to-Constructive Evasion Theory:** The Second Circuit did not evaluate a standard multiproduct bundled discount in isolation. Rather, it emphasized that Nielsen had adopted an **express** tying policy ("the Network Policy," which refused to sell a usable, unredacted Nationwide Report unless the customer bought Nielsen's local ratings data in every market where the customer operated stations)—a policy the district court held unlawful and whose illegality Nielsen did not challenge on appeal (Pet. App. 23a, 31a–32a). Only after Cumulus sent a cease-and-desist letter threatening suit did Nielsen purports to "exempt" Cumulus from the Network Policy by quoting a standalone price for Nationwide that was **10 times** what Cumulus paid under its existing contract and **150% higher** than the highest price any other national network paid (Pet. App. 10a, 33a). Both the district court and the Second Circuit treated this standalone quote on the preliminary record as a pretextual continuation of the express tie rather than a bona fide bundled discount.
2. **Preliminary Record on Cost Justification:** Far from holding that cost is legally irrelevant under all circumstances, the Second Circuit explicitly applied its precedent in *American Manufacturers I*, 388 F.2d 272, 283 (2d Cir. 1967) (derived from *United States v. Loew's, Inc.*, 371 U.S. 38 (1962)), which asks whether a price differential has the effect of conditioning the sale of the single product on the package "and if the difference in price cannot be legitimately justified by cost considerations" (Pet. App. 27a, 33a). The panel noted that on the preliminary-injunction record, "Nielsen has made no effort to quantify these costs or correlate them with its price for standalone Nationwide," while leaving open that "Nielsen may later 'quantify [its] costs or correlate them with its price for standalone Nationwide'" on a full merits record (Pet. App. 33a, 41a–42a).
3. **Interlocutory Posture & Active Ongoing Proceedings:** The petition seeks review of an interlocutory decision affirming a preliminary injunction. The Second Circuit repeatedly stressed the preliminary and deferential nature of its ruling ("This interlocutory appeal raises a number of complicated and novel issues. We resolve many of them not for all time, but on a preliminary basis and with considerable deference to the district court's factual findings and discretionary decisions," Pet. App. 54a; see also Pet. App. 5a). Moreover, district court proceedings on the merits remain ahead, Cumulus has undergone Chapter 11 reorganization proceedings, and a separate appeal concerning enforcement of the preliminary injunction (`No. 26-2516`) is currently pending in the Second Circuit (with briefing completed in October 2026). The Supreme Court strongly disfavors granting certiorari in interlocutory commercial disputes where factual development on remand (including cost quantification) or subsequent appellate proceedings may narrow, moot, or reshape the legal issues.

---

## 3. Conclusion

Combining the low base rate for paid Second Circuit petitions (~4.9%), the interlocutory preliminary-injunction posture with unresolved factual questions on cost justification, and the decisive procedural fact that Respondent waived its brief in opposition and the petition was distributed for its first conference without a Call for a Response (a posture with a <1% historical grant rate), we estimate a **1.0% (`0.01`)** probability of a grant and predict that the petition will be **denied**.
