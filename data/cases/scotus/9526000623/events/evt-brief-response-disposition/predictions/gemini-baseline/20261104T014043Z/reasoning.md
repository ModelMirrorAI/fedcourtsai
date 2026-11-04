# Prediction Reasoning: *Jesse Guardado v. Florida* (No. 26A623)

## 1. Case Overview & Provisioned Record

Petitioner Jesse Guardado is a Florida death-row prisoner scheduled for execution on November 5, 2026, at 6:00 p.m., pursuant to a death warrant signed by Governor Ron DeSantis on October 5, 2026. In 2005, Guardado waived guilt-phase counsel, pleaded guilty to first-degree murder and robbery with a weapon for the September 2004 murder of 75-year-old Jackie Malone, and was sentenced to death following a unanimous (12–0) jury recommendation and the trial court's finding of five aggravating factors (including HAC, CCP, prior violent felony, and conditional-release status).

His conviction and sentence were affirmed on direct appeal in *Guardado v. State*, 965 So. 2d 108 (Fla. 2007), *cert. denied*, 552 U.S. 1197 (2008). Initial state postconviction relief was denied and affirmed in *Guardado v. State*, 176 So. 3d 886 (Fla. 2015), successive *Hurst* collateral relief was denied and affirmed in *Guardado v. Jones*, 226 So. 3d 213 (Fla. 2017), *cert. denied*, 584 U.S. 922 (2018), and *Guardado v. State*, 238 So. 3d 162 (Fla. 2018), *cert. denied*, 586 U.S. 1004 (2018), and federal habeas relief was denied and affirmed in *Guardado v. Secretary, Florida Department of Corrections*, 112 F.4th 958 (11th Cir. 2024), *cert. denied*, 145 S. Ct. 2822 (2025).

After the Governor signed his death warrant on October 5, 2026, Guardado filed a successive motion for postconviction relief under Florida Rule of Criminal Procedure 3.851 raising three claims:
1. That Florida's clemency process violates the Fourteenth Amendment's Due Process Clause under Justice O'Connor's concurrence in *Ohio Adult Parole Authority v. Woodard*, 523 U.S. 272 (1998), because no death sentence has been commuted in Florida since 1983, the Governor allegedly has a blanket policy against clemency for murderers, and Guardado received no notice that his clemency proceeding (in which he was interviewed in July 2026) had concluded until the warrant was signed;
2. That trial and initial postconviction counsel rendered ineffective assistance by failing to investigate and present additional mitigation (including conditions at the Dozier School for Boys, trauma, and substance abuse), rendering his death sentence unreliable under the Sixth, Eighth, and Fourteenth Amendments and amounting to a "manifest injustice"; and
3. That the 31-day warrant litigation schedule deprives him of due process, fundamental fairness, and effective access to counsel.

The state circuit court summarily denied the motion on October 19, 2026, and the Florida Supreme Court affirmed on October 29, 2026 (*Guardado v. State*, No. SC2026-1605; retrieved via CourtListener MCP, `opinion_id=11516852`), holding that: (1) Guardado received clemency review and Florida's clemency process rests in the unfettered discretion of the executive with no violation of *Woodard*'s minimal safeguards; (2) the ineffective-assistance and mitigation claims are untimely under Rule 3.851(d) and procedurally barred because they could have been raised decades earlier; and (3) Florida's post-warrant schedule satisfied due process because Guardado received notice and an opportunity to be heard.

On October 30, 2026, Guardado submitted this application for a stay of execution (No. 26A623) to Justice Thomas as Circuit Justice for the Eleventh Circuit, linked with his petition for a writ of certiorari (No. 26-6013). On November 2, 2026, the State of Florida filed its response in opposition. I read the provisioned snapshot (`2026-11-03.json`), `record/context.json`, and both provisioned filings in `record/documents/` (`application.txt` and `application-response.txt`). This cell (`evt-brief-response-disposition`, `stage: interim`, `moment: response-filed`, `mode: forward`) forecasts the disposition of the application from the `2026-11-03.json` snapshot.

---

## 2. Base Rate Anchor (`interim` Stage)

Per the prompt contract (*Stage: interim*) and `metrics/statpack.md` (*The Interim Docket*), an OT2026 interim cell is scored against the pooled **finer** reading (`finer_granted` / `finer_resolved`) over the 10 application Terms strictly prior to the case's own (`2016 <= T < 2026`), requiring a floor of at least 50 resolved substantive applications and `finer_unread == 0` in every pooled Term.

Inspecting `metrics/statpack.md` (and `metrics/statpack.json`), the 10 strictly-prior application Terms (OT2016–OT2025) currently show `finer_resolved = 0` and `finer_unread = substantive_resolved` across all 10 Terms (because the historical finer-reading backfill has not yet populated those rows in the committed statpack). Consequently, the finer-reading estimator refuses a baseline while `finer_unread > 0`, and I note explicitly that under the strict finer-reading rule the cell anchors without a published finer-reading baseline.

For descriptive reference, the older registered reading (`substantive_granted` / `substantive_resolved`) across those same 10 strictly-prior Terms (OT2016–OT2025) in `metrics/statpack.md` is:
- **OT2025:** 17 granted / 226 resolved (`unparsed`: 0)
- **OT2024:** 16 granted / 194 resolved (`unparsed`: 0)
- **OT2023:** 18 granted / 127 resolved (`unparsed`: 0)
- **OT2022:** 9 granted / 103 resolved (`unparsed`: 0)
- **OT2021:** 30 granted / 120 resolved (`unparsed`: 0)
- **OT2020:** 25 granted / 133 resolved (`unparsed`: 0)
- **OT2019:** 12 granted / 119 resolved (`unparsed`: 0)
- **OT2018:** 12 granted / 113 resolved (`unparsed`: 0)
- **OT2017:** 12 granted / 124 resolved (`unparsed`: 1)
- **OT2016:** 9 granted / 107 resolved (`unparsed`: 15)

Summing the registered counts across OT2016–OT2025 yields **160 granted out of 1,366 substantive resolved applications (11.71%)**, or **33 granted out of 420 resolved (7.86%)** across the two most recent complete Terms (OT2024–OT2025). As `metrics/statpack.md` cautions, that unconditioned pool blends emergency stays sought by the Solicitor General and major non-capital stay applications with capital execution stays, and is not conditioned on the escalation ladder.

---

## 3. Rationale for Probability, Claims, and Votes

### A. `probability` = 0.015 / `predicted_disposition` = `denied`
Even starting from the ~8%–11.7% unconditioned substantive-application reference rate, a steep downward adjustment is warranted for a last-minute capital stay application arising from a successive state postconviction motion:
1. **Independent and Adequate State Procedural Bars:** In `application-response.txt` (pp. 4–6) and the Florida Supreme Court's opinion below (pp. 12–15), the State demonstrates that Guardado's mitigation and ineffective-assistance claims (relating to the Dozier School for Boys and penalty-phase investigation) were rejected on independent and adequate state-law grounds—namely, untimeliness under Fla. R. Crim. P. 3.851(d)(1)–(2) and Florida's procedural bar against claims that could have been raised in prior collateral proceedings. Under *Coleman v. Thompson*, 501 U.S. 722, 729 (1991), those state procedural bars foreclose Supreme Court review on certiorari, depriving Guardado of any reasonable probability of certiorari or fair prospect of reversal under *Barefoot v. Estelle*, 463 U.S. 880 (1983), and *Nken v. Holder*, 556 U.S. 418 (2009).
2. **Lack of Merit on Clemency and Warrant-Period Claims:** In `application.txt` (pp. 3–6), Guardado argues that his petition in No. 26-6013 raises substantial due process questions under Justice O'Connor's concurrence in *Ohio Adult Parole Authority v. Woodard*, 523 U.S. 272, 289 (1998), and challenges the 31-day warrant litigation period. However, the record shows Guardado had appointed clemency counsel, received a clemency interview in July 2026, and had clemency considered and denied before the warrant issued, and he litigated his successive postconviction motion through the circuit court and Florida Supreme Court with full briefing.
3. **Uniform Denials in Directly Comparable Priors:** As catalogued in the Florida Supreme Court's opinion and confirmed by corpus lookup (`scotus/9526000415`, *Beasley v. Comerford*, No. 26A415, denied Sept. 29, 2026), the Supreme Court has uniformly denied certiorari and stays of execution in recent Florida post-warrant cases raising virtually identical challenges to Florida's clemency process, Dozier School mitigation bars, and 30-day warrant schedules (*Cole*, *Tanzi*, *Hutchinson*, *Bell*, *Gudinas*, *Zakrzewski*, *Bates*, *Jones*, *Jennings*, *Reaves*).

I therefore set `probability` (and `interim-disposition`) at **0.015**, leaving only a small tail probability for an unexpected procedural hold or stay.

### B. Escalation Ladder Increment Claims (`interim-v3`)
- **`response-requested-increment` = 0.01:** `record/context.json` shows `response_requested: false`, and the `2026-11-03.json` snapshot shows that the State of Florida already filed its response in opposition on November 2, 2026. Because the response is already on the docket, the probability that the Court will subsequently enter an order calling for a response is negligible (`0.01`).
- **`referral-increment` = 0.95:** `record/context.json` shows `referred_to_court: false` as of the `2026-11-03.json` cutoff. In capital stay applications pending an imminent execution, Justice Thomas routinely refers the application to the full Court for disposition alongside the linked certiorari petition (as in *Beasley v. Comerford*, No. 26A415). I assign **0.95** to `referral-increment` (allowing a 5% chance that the application is acted on by the Circuit Justice alone or otherwise disposed of without a recorded referral clause).
- **`amicus-increment` = 0.03:** `record/context.json` shows `amicus_briefs: 0`. With execution scheduled for November 5, 2026, and no institutional amicus campaign evident in this routine successive post-warrant posture, the likelihood of an amicus brief being submitted or filed before disposition is very low (**0.03**).

### C. `votes`, `order-writers`, and `big_case_score`
- **`votes`:** All nine Justices are predicted to vote `deny`, reflecting the unanimous denials across the recent string of Florida post-warrant capital stay applications raising the same procedural and due-process issues.
- **`order-writers`:** Most recent Florida post-warrant stay denials have issued with no separate writings at all. I assign small per-Justice probabilities (`Sotomayor`: 0.04, `Jackson`: 0.03, `Kagan`: 0.008, `Thomas`: 0.005, `Gorsuch`: 0.005, `Kavanaugh`: 0.005, `Alito`: 0.003, `Barrett`: 0.003, `Roberts`: 0.002) to reflect the modest chance that Justice Sotomayor or Justice Jackson writes a brief dissent or statement respecting the denial of the stay.
- **`big_case_score` = 0.35:** While every capital execution stay application carries irreversible human stakes and draws full-Court referral, this application raises well-worn, procedurally barred successive postconviction claims with no circuit split, amicus participation, or broader doctrinal reach.

### D. Uncertainties
The primary uncertainty is whether the linked certiorari petition in No. 26-6013 contains any unprovisioned appendix material that might attract a separate statement from one of the Justices on the clemency-notice question, though the Florida Supreme Court's detailed opinion in No. SC2026-1605 and both parties' stay filings (`application.txt` and `application-response.txt`) make the posture and claims thoroughly clear.
