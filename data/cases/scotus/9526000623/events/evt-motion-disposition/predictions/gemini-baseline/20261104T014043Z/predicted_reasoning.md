# Predicted Reasoning: *Jesse Guardado v. Florida* (No. 26A623)

## 1. Procedural Trajectory and Escalation Signals from Arrival

At the arrival boundary (`2026-10-31`, `cut_anchor_index: 0`), the docket records only the October 30, 2026 submission of Jesse Guardado's capital stay application to Justice Thomas as Circuit Justice for the Eleventh Circuit (`response_requested: false`, `referred_to_court: false`, `amicus_briefs: 0`). From this opening state:

- **Call for a Response (`response-requested-increment`: 0.15):** The State of Florida routinely files a response to a capital prisoner's execution-week stay application and linked certiorari petition under standard capital practice without waiting for a formal docketed request from the Court or Circuit Justice (as occurred in *William Reaves v. Florida*, No. 26A524, where Florida responded two days after filing with `response_requested: false`). Consequently, a formal docketed call for a response is unlikely (`0.15`), though the State's opposition brief will be filed before the execution date.
- **Referral to the Full Court (`referral-increment`: 0.90):** Because this is an execution-week capital stay application coupled with a concurrently pending petition for a writ of certiorari (`No. 26-6013`), Justice Thomas will almost certainly refer the application to the full Court so that the stay application and the certiorari petition are disposed of together by order of the full bench (`0.90`).
- **Amicus Filings (`amicus-increment`: 0.03):** No amicus briefs have been submitted at arrival, and given the narrow, case-specific post-warrant posture and the five-day window before the November 5, 2026 execution, it is very unlikely that any amicus curiae brief will be submitted or filed before disposition (`0.03`).

## 2. Timing and Disposition (`interim-disposition`: 0.02; `predicted_disposition`: `denied`)

The Court will dispose of the application on or before Thursday, November 5, 2026—most likely on November 4 or the afternoon of November 5, 2026, ahead of the scheduled 6:00 p.m. execution—by **denying** the application for a stay of execution in a short, unsigned order issued alongside an order denying certiorari in No. 26-6013 (`P(grant) = 0.02`).

If the Court were to reach the merits of the stay standard, it would conclude that Guardado has shown neither a reasonable probability of certiorari nor a significant possibility of reversal on his Fourteenth Amendment Due Process challenge to Florida's executive clemency process under *Ohio Adult Parole Authority v. Woodard*, 523 U.S. 272 (1998), or on his untimely and procedurally barred postconviction claims.

## 3. Separate Writings (`order-writers`)

The denial order will almost certainly issue without any separate writing. Should any Justice write a dissent or statement respecting the denial of the stay, Justices Sotomayor (`0.025`) and Jackson (`0.020`) are the likeliest authors given their occasional writings in capital stay dispositions, though even for them a separate writing is unlikely here given the settled status of *Woodard* clemency challenges and the absence of any novel Eighth Amendment or method-of-execution issue.
