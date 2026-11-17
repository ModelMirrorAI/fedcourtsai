# Predictor Rationale — *Thomas M. Overton v. Florida, et al.* (No. 26A686, `evt-brief-response-disposition`)

## Summary of Forecast Numbers

- **`granted`:** `0` (`predicted_disposition`: `"denied"`)
- **`probability` / `interim-disposition`:** `0.005`
- **`response-requested-increment`:** `0.005`
- **`referral-increment`:** `0.96`
- **`amicus-increment`:** `0.03`
- **`big_case_score`:** `0.22`

## Inputs Read and Record Conditioning

I read the provisioned snapshot `data/cases/scotus/9526000686/record/snapshots/2026-11-17.json` (`input_snapshot: "2026-11-17.json"`), `record/context.json` (`mode: "forward"`, `snapshot_date: "2026-11-17"`, `cutoff: "2026-11-18"`, `band: null`), and both provisioned filings in `record/documents/` (`application.txt`, 5 pages, and `application-response.txt`, 9 pages; both clean PDF text extractions with `empty_text: false`, `ocr_derived: false`, `truncated: false`). As an interim cell with `band: null`, I did not derive a cert salience band or use any cert band base rate.

The frozen escalation state on `2026-11-17` is:
- `response_requested`: `false` (Florida filed its November 17 opposition uninvited, per routine state death-warrant practice, three days after Overton's November 14 stay application);
- `referred_to_court`: `false` (submitted to Justice Thomas on November 14; no referral entry yet);
- `amicus_briefs`: `0`.

## Base-Rate Anchor (`metrics/statpack.md` & `metrics/statpack.json`)

1. **Scored Interim Baseline (`finer_granted` / `finer_resolved`, OT2016–OT2025):**
   For an OT2026 application (`26A686`), the scored baseline pools the ten strictly prior application-Terms (`2016 <= T <= 2025`) over `finer_granted` / `finer_resolved` (partial grants counted as granted, moot dismissals excluded from both). Checking `metrics/statpack.json` and `metrics/statpack.md` ("The interim docket (applications)", whose caption already reflects the scored strictly-prior pool rule), every pooled Term in `2016–2025` has `finer_unread = 0` (with minor `unparsed` counts only in OT2017 [`1`] and OT2016 [`15`]):
   - Pooled count: `19 + 18 + 17 + 9 + 17 + 27 + 13 + 14 + 13 + 9 = 156` granted out of `218 + 189 + 124 + 103 + 107 + 133 + 119 + 113 + 124 + 107 = 1,337` resolved (`11.67%`, published as **`11.7% (156/1337)`**), clearing the 50-application floor by a wide margin.

2. **Applicant-Class Cut (`Substantive applications by applicant class`):**
   Both the caption rule (`"Thomas M. Overton, Applicant"` -> `private`) and substantive party identity classify this cell as **`private` × `capital`** (`CaseNumber: "26A686 *** CAPITAL CASE ***"`, `bCapitalCase: true`). In the committed 10-Term pool (`2016–2025`), the `private` × `capital` cell clears the 30-application floor with **`3.5% (10/288)`** (`n = 288`). I lean directly on the `private` × `capital` cell (`3.5%`) rather than the `capital` column margin (`9.5%`, `30/316`), because the column margin mixes prisoner stay applications with governmental applications to *vacate* lower-court stays of execution (`federal` capital `7/8`; `state` capital `13/20 = 65.0%`). Moreover, inspecting the per-Term `applicant_cuts` in `statpack.json` within `2016–2025` shows a sharp recent contraction inside `private` × `capital`: in the two most recent complete Terms (`OT2024`: `0/44`; `OT2025`: `0/44`), private capital applications went **`0/88` (`0.0%`)** (and `3/144 = 2.1%` across `OT2022–OT2025`). That moves my starting prior before case-specific merits from the `11.7%` overall yardstick down to `~3.5%` on the 10-Term class cut and `~1.0–1.5%` weighting recent-Term Court practice.

3. **Why `response-filed` does not adjust upward here:**
   Although substantive applications with a filed response grant at a higher rate across the whole interim docket (`115/339 = 33.9%` over `2016–2025`), that figure reflects non-capital applications where a response usually arrives because the Court requested one (`response_requested: true`) or because the Solicitor General / a State is seeking emergency relief. In active death-warrant cases, the State Attorney General routinely files an opposition automatically without any request from the Court (`response_requested: false`), as Florida did here and in *Guardado* (`26A623`) and *Reaves* (`26A524`). An unsolicited state opposition on an execution warrant carries zero positive selection signal.

## Case-Specific Adjustments to `0.005`

Adjusting downward from the `3.5%` (`10/288`) `private` × `capital` class rate (and `0/88` recent-Term rate) to **`0.005`** rests on four converging features of the record and the Florida Supreme Court's November 13, 2026 opinion below (*Overton v. State*, Nos. SC2026-1724 & SC2026-1725, retrieved via CourtListener MCP):

1. **Direct, indistinguishable recent SCOTUS denials.** Overton's 5-page stay application raises a single claim: that Florida's clemency process violated minimal due process under *Ohio Adult Parole Authority v. Woodard*, 523 U.S. 272 (1998), and the Eighth Amendment because his clemency interview occurred in December 2013, he received no formal denial notice before Governor DeSantis signed his death warrant on October 20, 2026, and he had no post-2013 update hearing. Corpus queries confirm that the Court denied stays of execution and certiorari on **this exact Florida clemency claim** without recorded dissent or opinion two weeks ago in *Jesse Guardado v. Florida* (`26A623` / `26-6013`, decided Nov. 5, 2026; 2014 clemency interview) and four weeks ago in *William Reaves v. Florida* (`26A524` / `26-5865`, decided Oct. 20, 2026), following earlier denials in *Barwick v. Governor of Florida*, 66 F.4th 896 (11th Cir.), *cert. denied*, 143 S. Ct. 1102 (2023), and *Zakrzewski v. Florida*, 146 S. Ct. 46 (2025).
2. **Independent and adequate state procedural bar.** Both the state circuit court and the Florida Supreme Court held Overton's clemency claim **untimely and procedurally barred under Fla. R. Crim. P. 3.851(d)** because Overton knew since December 2013 that his clemency process had begun and waited nearly thirteen years until a warrant issued to raise a challenge (*Overton v. State*, slip op. at 10–11 & n.6; `application-response.txt` at 5–6). On direct review of a state postconviction judgment (`26-6154`), an independent and adequate state procedural bar defeats Supreme Court jurisdiction under *Coleman v. Thompson*, 501 U.S. 722, 729 (1991), even where the state high court also rejects the federal claim on the merits in the alternative.
3. **Weak underlying *Woodard* merits and no split.** Overton received appointed clemency counsel in 2013, had a Commission interview in December 2013, remained free under Florida Executive Clemency Rule 15B to submit supplemental written materials at any time, and had clemency expressly considered and rejected on the face of the signed death warrant. No federal court of appeals or state high court holds that *Woodard*'s minimal-safeguards floor mandates a second clemency interview or pre-warrant notice under these circumstances.
4. **Equitable timing and narrow presentation.** Overton's convictions for a 1991 double murder became final in 2002, no innocence or method-of-execution question is raised, no parallel federal stay proceeding appears on CourtListener dockets (`ca11`/`flsd`/`flmd`/`flnd`), and Overton dropped his other state-court claims (including public-records objections and his 9–3 nonunanimous-jury habeas claim) from the stay application. I retain `0.005` rather than `0.000` only for irreducible emergency-warrant tail risk (conditional on non-moot resolution, as required by the scoring rule).

## Increment Claims, `order-writers`, and `big_case_score`

- **`response-requested-increment` (`0.005`):** Florida has already filed its formal opposition (`application-response.txt`), and there is no other respondent party from whom a response could be called.
- **`referral-increment` (`0.96`):** Crucially, full-Court referral is decoupled from grant likelihood on active death warrants. Corpus checks on recent Eleventh Circuit / Florida execution applications (`26A623` *Guardado*, `26A634` *Guardado*, `26A524` *Reaves*, `26A405` *Beasley*, plus Sixth Circuit capital applications `26A414` and `26A428`) show `referred_to_court: true` in **6 of 6** resolved capital applications — even when `response_requested: false` and the application was summarily denied. Justice Thomas routinely refers active-warrant stay applications paired with a cert petition (`26-6154`) to the full Court upon disposition. I discount from `1.0` to `0.96` only for the small chance of a pre-referral withdrawal, external stay mooting the matter before referral, or an atypical single-Justice chamber denial.
- **`amicus-increment` (`0.03`):** None of the comparable recent Florida warrant stay applications (`26A623`, `26A634`, `26A524`, `26A405`) drew an amicus brief, and execution is two days away with the State's opposition already filed. A `0.03` allowance covers a late institutional submission or motion reciting `amicus curiae` before Thursday evening.
- **`order-writers`:** Neither *Guardado* (`26A623`/`26A634`), *Reaves* (`26A524`), nor *Beasley* (`26A405`) produced a separate opinion (`has_opinion: false`), and Overton did not bring his 9–3 nonunanimous-jury claim in this stay application. I assign small, differentiated writing probabilities led by Justices Sotomayor (`0.025`) and Jackson (`0.015`), with `0.001–0.005` across the remaining seven Justices.
- **`big_case_score` (`0.22`):** Scored strictly on significance *if decided* rather than grant odds: a merits ruling tightening *Woodard*'s procedural due-process floor for capital clemency timeliness and notice would materially affect retentionist states' clemency administration, though the dispute is confined to capital clemency procedure and encumbered by a state timeliness bar.

## Uncertainties

My main uncertainty is on `referral-increment` (`0.96`) and `order-writers` rather than the disposition (`0.005`): while full-Court referral is overwhelming standard practice on counseled Florida execution warrants, an unrecorded docketing quirk or unexpected pre-execution state action could occasionally leave `referred_to_court` false, and any Justice retains discretion to pen a short statement on a capital warrant order even where recent indistinguishable cases drew none.
