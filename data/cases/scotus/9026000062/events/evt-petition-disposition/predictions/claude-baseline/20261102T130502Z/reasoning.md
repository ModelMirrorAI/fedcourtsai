# Reasoning — Custodia Bank, Inc. v. Federal Reserve Board of Governors (No. 26-62)

**P(grant) = 0.08.**

## Inputs read
- Snapshot `record/snapshots/2026-11-02.json`. It shows a paid petition from the Tenth Circuit (No. 24-8024, decided Oct 31, 2025; rehearing en banc denied Mar 13, 2026). There are two BIOs, filed Oct 13, 2026: one from the Board, through the Solicitor General (Sauer), and one from the Federal Reserve Bank of Kansas City. Three amicus briefs were filed: Blockchain Association, The Digital Chamber, and Sen. Lummis with former Sen. Toomey. The reply came in Oct 28. The petition was **DISTRIBUTED once**, for the Conference of Nov 13, 2026.
- Documents: the questions presented, the petition, the appendix (truncated at the cap), both BIOs and the reply. I read the QP and the petition's reasons in full, and the BIOs' sections on why review is unwarranted and on vehicle.
- `context.json`: forward mode, band `baseline` (sal-v6), distribution_count 1, no CVSG, `cert_anchor.rate` = 0.0519.
- `same-question.json`: empty list. No other pending petitions share this QP.

## Anchor
The frozen anchor is the `baseline` band's reached rate pooled over prior Terms: **5.2%**. This is a paid petition at its first distribution, with no relist and no CVSG.

## Adjustments
**Up:**
- Elite counsel: Shanmugam.
- Three amicus briefs, including one from a sitting Senator. In the statpack's amicus 2+ bucket (n=1542), the grant family is about 23%. That bucket is heavily confounded, so I used it only for direction.
- Judge Tymkovich wrote two forceful opinions below: a panel dissent and a dissent from denial of rehearing en banc. The question is a pure, dispositive statutory question about Fed power, and the current Court cares about agency power.
- The administration's posture favors fintech (EO 14,405). Gorsuch, as Circuit Justice for the Tenth Circuit, has written on agency-discretion themes.

**Down, and stronger:**
- The petition concedes there is no circuit split. The only other circuit to address the question, the Second Circuit in *Banco San Juan* (2026), agrees with the Tenth Circuit. The Ninth Circuit case (*PayServices*) is in abeyance.
- The **federal government opposes**. The SG filed a BIO for the Board even though the administration otherwise favors crypto. SG opposition when there is no split is a strong denial predictor.
- There is a live vehicle problem: the Board's May 2026 proposed rule on "Payment Accounts" (91 Fed. Reg. 30,627) could moot the dispute or reshape it. Custodia said below that a limited payment account would satisfy it.
- The petition leans on separation-of-powers and Appointments Clause themes. The Tenth Circuit held those arguments waived, and the petition does not challenge that waiver holding. Respondents also cite *Trump v. Cook* (2026) as upholding the Fed's structure.
- Custodia framed its claim as an all-or-nothing entitlement and did not challenge the reasons for the denial. That makes the case a narrower vehicle than the petition's rhetoric suggests.

Net: somewhat above the anchor, at 0.08. Importance and the dissent below push up. No split, SG opposition and the pending rulemaking pull down.

## Other claims
- **Relist-increment 0.22.** A Justice, most plausibly Gorsuch, may want a second look or a dissent from denial. The statpack shows most petitions at one distribution are never relisted.
- **CVSG 0.01.** A federal party is already a respondent and the SG has filed, so a CVSG would be pointless.
- **Summary route given a grant: 0.04.** No intervening decision suggests a GVR.
- **Dissent from denial given a denial: 0.10.** Gorsuch is the most plausible writer, then Thomas.

## Uncertainty
- I have not seen the Tenth Circuit's reasoning beyond the excerpts quoted in the briefs. I did not read the appendix in full.
- The Court's appetite for Fed cases after *Cook* is hard to gauge.

## Retrieval and leakage
I ran two corpus queries; one failed because I used the wrong era token. I read the statpack. I made no CourtListener or web calls. I found nothing about this petition's disposition and do not know the outcome.
