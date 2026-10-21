# Predicted Court Reasoning and Procedural Trajectory: *Scanlan v. Coalition for Open Democracy* (No. 26A512)

## 1. Escalation Ladder and Procedural Increments (from `arrival` snapshot `2026-10-15`)

At the `arrival` moment (`2026-10-15`), the docket records only the submission of the emergency stay application to Justice Jackson (`response_requested: false`, `referred_to_court: false`, `amicus_briefs: 0`). From this baseline, the predicted procedural trajectory is:

1. **Request for a Response (`response-requested-increment`: `0.85`):**
   Justice Jackson will almost certainly call for a response from Respondent Coalition for Open Democracy on a short, expedited schedule (likely within 3 to 5 days), because the application is filed by state constitutional officers (the New Hampshire Secretary of State and Attorney General) invoking *Purcell v. Gonzalez*, 549 U.S. 1 (2006), ahead of the November 3, 2026 general election. The only scenario in which a response is not requested (`0.15`) is if the First Circuit acts on the pending stay motion almost immediately or Justice Jackson denies the application outright without calling for a response due to the pending First Circuit motion.
2. **Referral to the Full Court (`referral-increment`: `0.75`):**
   Following receipt of Respondent's opposition (or if the application is not mooted/withdrawn following a First Circuit ruling), Justice Jackson is likely to refer the application to the full Court (`0.75`), consistent with standard practice for contested state-official election-law stay applications in the final weeks before a federal general election.
3. **Amicus Filings (`amicus-increment`: `0.30`):**
   With `amicus_briefs: 0` at arrival and a compressed timeline before the November 3 election—coupled with a narrow, New Hampshire-specific dispute over whether an executive press release accurately glosses two state statutory safety valves—there is a modest (`0.30`) probability that at least one amicus brief (for example, from national political committees or voting-rights/election-integrity organizations) is submitted before disposition.
4. **Expected Timing and Form of Disposition (`interim-disposition`: `0.22`):**
   The Court is expected to dispose of the application within 5 to 10 days of arrival (around October 20–26, 2026), before the final week preceding the November 3 election. The most likely form of disposition is a brief order denying the application (`predicted_disposition: "denied"`), potentially noting that Justices Thomas, Alito, and Gorsuch would grant the application, or accompanied by a short dissent or statement respecting the denial.

---

## 2. Substantive Forecast of the Court's Disposition

The Court is predicted to **deny** the application for a stay (`interim-disposition: 0.22`) for four converging reasons:

1. **Unexhausted / Pending Appellate Posture in the First Circuit:**
   Applicants filed this emergency application in the Supreme Court just five days after reply briefing closed on their renewed emergency stay motion in the First Circuit (No. 26-2132). Absent an operational deadline such as ballot printing or mailing, the Court disfavors bypassing a circuit panel actively considering an expedited stay motion.
2. **No Enacted State Statute Was Enjoined:**
   Unlike *People Not Politicians v. Onder*, 609 U.S. ___ (Sept. 25, 2026), and *National Republican Congressional Committee v. Brown*, 609 U.S. ___ (Sept. 4, 2026), the district court **upheld** New Hampshire's enacted voter-ID statute (HB 323, amending RSA 659:13, II(a)). It enjoined only a single exclusionary rule from an April 23, 2026 Secretary of State press release prohibiting checklist supervisors from even considering a student ID alongside other evidence under the existing case-by-case statutory safety valves (RSA 654:12, I(d)(4) and RSA 659:13, I(c)(3)).
3. **Inverted *Purcell* Equities After State Compliance:**
   Following the October 2 injunction, the Secretary of State immediately updated the public website and issued revised guidance to local election officials, which was already implemented during the October 6 municipal election in Franklin, New Hampshire. Because ballot design, printing, and mailing are untouched and the revised guidance is already live on the Secretary's website, granting a stay in late October would itself cause the second rule change in three weeks and confuse voters who relied on the Secretary's posted instructions.
4. **Forfeited State-Law Premise Below:**
   The district court expressly found in its stay-denial order that the State's core statutory argument—that SB 223's addition of the word "only" to RSA 659:13, II(a) restricts the separate supervisor safety valves—was raised for the first time in the motion to stay and contradicted the State's pre-injunction written Record Supplement. That procedural defect makes certiorari or reversal unlikely under *Hollingsworth v. Perry*, 558 U.S. 183, 190 (2010), and *Merrill v. Milligan*, 142 S. Ct. 879, 880–81 (2022) (Kavanaugh, J., concurring).
