# Predictor Reasoning — `scotus/9026000518` (`evt-petition-disposition`)

## Summary of Call

- **Predicted disposition:** `denied` (`granted = 0`, `probability = 0.04`)
- **Conditioning state (`record/context.json`):** `mode = "forward"`, `band = "baseline"` (`salience_version = "sal-v8"`), `distribution_count = 1`, `cvsg_date = null`, `amicus_briefs = null`, `input_snapshot = "2026-11-09.json"`.

## Base-Rate Anchoring

1. **Primary anchor (`cert_anchor`):** In `record/context.json`, the frozen `cert_anchor` for the `baseline` band under `sal-v8` across the 10 prior Terms (`lookback_terms = 10`, OT2016–OT2025) is **`0.0516`** (5.16%). In `metrics/statpack.md` (*Segment base rate by salience band (sal-v8)*), the prior-Term bracketed `[reached]` rates for `baseline` range from `4.0%` (OT2025, `n=1290`) to `6.0%` (OT2023 `n=1283` and OT2024 `n=1243`).
2. **Marginal statpack cuts (`metrics/statpack.md`):**
   - *Modern cert petitions by originating circuit (`ca11`):* `denied 94.9%, gvr 2.1%, dismissed 1.8%, granted 1.2%` (`n=3954` resolved; grant family `3.3%`).
   - *Cert petitions by relist count (paid scored segment):* Bucket `0` (1 distribution) sits at `denied 96.8%, dismissed 1.3%, granted 1.3%, gvr 0.5%` (`n=10204`; grant family `1.8%`); Bucket `1` (2 distributions, where this petition is headed after the call for response) sits at `denied 85.5%, granted 8.3%, gvr 5.2%, dismissed 1.0%` (`n=2532`; grant family `13.5%`).
   - *Cert petitions by CVSG status (paid scored segment, `none`):* `denied 92.4%, granted 4.1%, gvr 2.3%, dismissed 1.2%` (`n=13550`; grant family `6.4%`).
   - *Cert petitions by amicus-brief count (paid scored segment, `0`):* `denied 95.0%, granted 2.0%, gvr 1.8%, dismissed 1.3%` (`n=11109`; grant family `3.8%`).

## Case-Specific Adjustments from the Anchor

Starting from the `5.16%` (`0.0516`) `baseline` reached anchor, I adjust upward for the procedural signal on the snapshot and downward for severe vehicle, preservation, and merits defects reflected in the provisioned `petition.txt` and `questions-presented.txt`:

### Upward Factors
- **Call for Response (`Oct 27 2026`):** After Respondents Hillary R. Clinton et al. filed a waiver on October 19, 2026 and the petition was distributed on October 21, 2026 for the November 6, 2026 conference, the Court requested a response on October 27, 2026 (due November 27, 2026). That takes the petition out of the summary-waiver denial pile and confirms that at least one chambers wanted adversarial briefing before conference action.
- **High-profile petitioner and sanctions size:** The lead petitioner is the sitting President (litigating in his private capacity alongside counsel Alina Habba and Habba Madaio & Associates) challenging a $937,989.39 inherent-authority sanctions award and raising Article II arguments.

### Downward Factors (Decisive)
- **No circuit split on either Question Presented:** Neither Question Presented implicates a conflict among the federal courts of appeals or state high courts. On QP 1, no court has ever held that Article II equitably tolls a sitting President's private civil claims as a plaintiff; the sole authority Petitioners cite (*Alexander v. Trump*, 413 So. 3d 795 (Fla. 4th DCA 2025)) involved a discretionary stay of active state-court proceedings, not equitable tolling of an expired limitations period.
- **Severe vehicle defects on Question Presented 1 (Equitable Tolling):**
  1. *Alternative substantive grounds for dismissal:* The district court dismissed the civil RICO claims not only as untimely (accruing by October 2017, more than four years before the March 2022 complaint), but also on alternative merits grounds—holding that the 193-page Amended Complaint failed at every step of a substantive RICO claim (no valid predicate acts, no pattern of racketeering, no enterprise, and no domestic business/property injury; Pet. App. 11a, 66a). Even if the Court reversed on equitable tolling, the RICO claims would remain subject to dismissal on the substantive grounds on remand.
  2. *Concession under Menominee Indian Tribe:* Under *Menominee Indian Tribe of Wisconsin v. United States*, 577 U.S. 250, 255–57 (2016), equitable tolling requires an extraordinary circumstance *beyond the litigant's control* that prevented timely filing. As Chief Judge William Pryor noted for a unanimous Eleventh Circuit panel (Pet. App. 20a–21a), Petitioner conceded that he made a deliberate choice to defer filing suit until after his term—and as the district court observed (Pet. App. 65a), Petitioner filed several other personal civil lawsuits while in office.
- **Severe vehicle and forfeiture defects on Question Presented 2 (Inherent-Authority Sanctions):**
  1. *Independent, unappealed bases for bad faith:* Petitioners frame the sanctions award as punishing them for advancing their Article II equitable-tolling argument. Yet the Eleventh Circuit explicitly held that *"[e]ven setting aside the tolling arguments, the district court ruled that Trump brought several frivolous claims, including a 'malicious prosecution claim without a prosecution,' and a 'trade secret claim without a trade secret,'"* plus seven counts that stated no cause of action at all—11 counts whose dismissal Petitioners did not even appeal (Pet. App. 31a). The Eleventh Circuit also independently affirmed the bad-faith finding based on Petitioners' persistent "shotgun pleading" (incorporating 633 preceding paragraphs into subsequent counts after being warned by motions to dismiss; Pet. App. 28a–30a) and outside litigation conduct (Pet. App. 31a–32a).
  2. *Procedural and fee-apportionment forfeitures:* The Eleventh Circuit held that Petitioners forfeited their notice/safe-harbor objection, forfeited any request for an evidentiary hearing on inherent-authority sanctions, and forfeited any overarching challenge to the fee calculation beyond line-by-line billing objections (Pet. App. 26a–27a, 32a). That forfeiture directly blocks Petitioners' *Goodyear Tire & Rubber Co. v. Haeger*, 581 U.S. 101 (2017), causal-apportionment argument (Pet. 16–17).
- **Unanimous panel and no amicus support:** The Eleventh Circuit's opinion was authored by Chief Judge William Pryor and joined in full by Judges Brasher and Kidd, rehearing en banc was denied on May 12, 2026 with no recorded dissent, and zero amicus briefs have been filed in support of certiorari.

Weighing the call for response against these formidable vehicle and forfeiture barriers yields **`probability = 0.04`** (`4.0%`), just below the `5.16%` `baseline` reached anchor.

## Secondary Claims and Order-Writers Rationale

- **`relist-increment` (`0.98`):** `context.json` freezes `distribution_count = 1` (the October 21, 2026 distribution). Because the Court requested a response on October 27, 2026 (due November 27, 2026), the Clerk will redistribute the petition for conference once the response is filed or the time expires. Only a voluntary dismissal/withdrawal before redistribution would prevent `distribution_count` from rising past 1.
- **`cvsg-increment` (`0.005`):** The United States is already a respondent on the docket represented by the Solicitor General, making a formal CVSG invitation practically impossible.
- **`summary-disposition-route` (`0.55`):** Conditional on a grant, the Court is slightly more likely to issue a narrow GVR (e.g., vacating and remanding the sanctions order for reconsideration or *Goodyear Tire* fee apportionment without relying on the Article II tolling argument, as Petitioners explicitly request in the alternative at Pet. 17) than to hear oral argument in a fact-bound sanctions dispute.
- **`dissent-from-denial` (`0.12`) and `order-writers`:** The October 27, 2026 call for a response in a case with glaring vehicle defects suggests that a chambers (most likely Justice Thomas, the Eleventh Circuit Justice who granted two extensions in 26A134, or Justice Alito) wanted to see Respondents' defense of Judge Middlebrooks's sweeping sanctions order and may consider a separate statement or dissent from denial. I assign `0.12` to `dissent-from-denial` and distribute individual writing probabilities principally to `Thomas` (`0.06`), `Alito` (`0.05`), `Gorsuch` (`0.025`), and `Kavanaugh` (`0.01`), with `0.003–0.005` on the remaining Justices.
- **`big_case_score` (`0.65`):** The lawsuit pits President Trump against Hillary Clinton and prominent political figures over the 2016 campaign and Crossfire Hurricane investigation and raises an Article II tolling theory alongside nearly $1 million in sanctions, giving it high public newsworthiness despite its narrow, fact-bound legal posture.

## Uncertainties and Limitations

- **Unfiled Brief in Opposition:** Because the response is not due until November 27, 2026, only `petition.txt` and `questions-presented.txt` (including the lower-court opinions in the Petition Appendix) are on the record. However, the Eleventh Circuit's detailed 37-page opinion (Pet. App. 1a–37a) and the district court's sanctions order (Pet. App. 38a–74a) already lay out the alternative grounds and forfeitures that Respondents will emphasize in their BIO.
