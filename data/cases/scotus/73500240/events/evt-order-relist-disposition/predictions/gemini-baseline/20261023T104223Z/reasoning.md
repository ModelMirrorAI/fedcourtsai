# Rationale (`reasoning.md`) — *Jonathan Granado v. Juanita Ramirez* (No. 25-1338)

## 1. Summary of Numbers

- **`granted`**: `0` (`predicted_disposition`: `"denied"`)
- **`probability` (`disposition`)**: `0.22`
- **`relist-increment`**: `0.38`
- **`cvsg-increment`**: `0.01`
- **`summary-disposition-route`**: `0.77`
- **`dissent-from-denial`**: `0.28`
- **`big_case_score`**: `0.35`
- **`input_snapshot`**: `"2026-10-07.json"`

---

## 2. Base-Rate Anchor (`metrics/statpack.md`)

Per `record/context.json`, this cell runs in `forward` mode with `band: "elevated"`, `salience_version: "sal-v4"`, `distribution_count: 2`, `cvsg_date: null`, and `term: 2025` (docket No. 25-1338).

1. **Salience Band Anchor (`elevated`, `sal-v4`, strictly prior Terms 2017–2024):**  
   Pooling the bracketed `reached` figures for the `elevated` band in `metrics/statpack.md` across all rendered Terms strictly preceding OT 2025 (Terms 2017 through 2024):
   - **2024:** 17.9% ($n=336 \implies \approx 60.1$ grants)
   - **2023:** 17.5% ($n=354 \implies \approx 62.0$ grants)
   - **2022:** 19.0% ($n=300 \implies \approx 57.0$ grants)
   - **2021:** 20.5% ($n=342 \implies \approx 70.1$ grants)
   - **2020:** 16.1% ($n=397 \implies \approx 63.9$ grants)
   - **2019:** 13.8% ($n=334 \implies \approx 46.1$ grants)
   - **2018:** 15.9% ($n=347 \implies \approx 55.2$ grants)
   - **2017:** 17.5% ($n=400 \implies \approx 70.0$ grants)
   - **Pooled strictly-prior `elevated` [reached] anchor:** $\approx 484.4 / 2810 = \mathbf{17.2\%}$.

2. **Relist-Count Cut Cross-Check (`metrics/statpack.md`):**  
   In the "Cert petitions by relist count (paid scored segment)" table, pooling all buckets from `1` up (`1`, `2`, `3+`):
   - **Bucket 1** ($n=2521$ resolved): `granted` 8.3% + `gvr` 5.1% = **13.4%** ($\approx 337.8$ grants)
   - **Bucket 2** ($n=487$ resolved): `granted` 27.5% + `gvr` 13.1% = **40.6%** ($\approx 197.7$ grants)
   - **Bucket 3+** ($n=481$ resolved): `granted` 22.5% + `gvr` 14.3% = **36.8%** ($\approx 177.0$ grants)
   - **Pooled relist $\ge 1$ grant-family rate:** $\approx 712.5 / 3489 = \mathbf{20.4\%}$.  
   - **Forward relist hazard from Bucket 1:** Out of 3,489 resolved petitions that reached at least 1 relist, 968 ($487 + 481 = \mathbf{27.7\%}$) went on to be distributed at least once more (buckets 2 and 3+). Because bucket 1 in the statpack also includes pre-conference reschedules whereas *Granado* was genuinely relisted after the September 28, 2026 Long Conference, the true forward relist rate for a genuine conference relist is higher than 27.7%.

3. **Originating Circuit Cut (`ca5`):**  
   In the modern discretionary-cert table, Fifth Circuit petitions have a 3.7% overall grant-family rate (1.6% `granted` + 2.1% `gvr` over 5,396 resolved cases), slightly above the national circuit average due to higher GVR/summary-disposition activity.

---

## 3. Adjustments From the Anchor (17.2% $	o$ 22.0%)

Starting from the **17.2%** strictly-prior `elevated` [reached] base rate (and **20.4%** relist $\ge 1$ cross-check), I adjust upward to **0.22** based on the competing pulls in the provisioned documents (`questions-presented.txt`, `petition.txt`, and `brief-in-opposition.txt`):

### Upward Pressures
- **True Post-Conference Relist + 8–9 En Banc Split:** Unlike administrative reschedules that dilute the `elevated` band, this petition went through the September 28, 2026 Long Conference and was relisted on October 7, 2026. Below, the Fifth Circuit denied rehearing en banc by an 8–9 vote (Pet. App. 20a–21a), with thorough dissents by Judge Ho and Judge Oldham (joined by five judges total).
- **Explicit Invitation for Summary Reversal on Qualified Immunity Prong Two:** Judge Oldham's dissent (Pet. App. 23a–35a) is written as a roadmap for a per curiam summary reversal under *Mullenix v. Luna*, 577 U.S. 7 (2015), and *Rivas-Villegas v. Cortesluna*, 595 U.S. 1 (2021). Moreover, the panel majority's Prong Two analysis is compressed into a single paragraph (Pet. App. 13a) relying on the general rule of *Lytle v. Bexar County*, 560 F.3d 404 (5th Cir. 2009), and *Baker v. Putnal*, 75 F.3d 190 (5th Cir. 1996). Just seven months ago in *Zorn v. Linton*, 607 U.S. ___ (Mar. 23, 2026) (`scotus/72528904`), this Court summarily reversed the Second Circuit on qualified immunity for relying on an overly general circuit precedent from a summary-judgment remand.

### Downward Pressures (Why `probability` Stays at 0.22 Rather Than >0.50)
- **Acute Factual Disputes Under *Tolan v. Cotton*, 572 U.S. 650 (2014):** Having read the full Fifth Circuit opinion, Judge Dennis's concurrence, Judge Oldham's dissent (all in `petition.txt`), and Respondent's `brief-in-opposition.txt`, this case is far messier factually than typical summary-reversal vehicles:
  1. **Two Distinct Shooting Phases & Granado's Own Audio:** Granado fired once near the car, paused as Ramirez ran across the street away from the officers, and then fired six more times, hitting Ramirez four times from **back to front** (including the back of the head). Immediately after firing the fatal shots, Granado asked Officer Watson on bodycam audio: *"did he have a gun?"* (Pet. App. 4a, 9a, 15a). The Fifth Circuit panel held that a reasonable jury could infer from Granado's own question that he did not actually know Ramirez was armed when he fired the six shots into Ramirez's back.
  2. **Fellow Officer Contradiction:** Granado claimed in his post-incident affidavit that he fired the second volley because Ramirez was "swinging his pistol in the direction of Officer Watson and [him]" (Pet. App. 8a–9a). Yet Officer Watson—who stood closest to Ramirez and never drew his weapon—stated that *"Ramirez never pointed the gun toward me or while he was running away"* (Pet. App. 4a, 10a, 16a).
  3. **Unsupported "Drive-By Shooting" Assumption:** The district court relied on Granado's statement that he heard dispatch/radio reports that the suspect vehicle was involved in "drive-by shootings" (Pet. App. 37a), but as Judge Dennis demonstrated (Pet. App. 14a–15a), the actual radio transcripts in the summary-judgment record contain no mention of drive-by shootings.
- **Tension With *Tolan v. Cotton* and *Barnes v. Felix* (2025):** Because the Fifth Circuit's denial of summary judgment rests on genuine factual disputes over whether Granado knew Ramirez had a gun during the second volley and whether Ramirez ever pointed or swung it, summarily reversing would require the Supreme Court to reweigh contested summary-judgment evidence—the exact error the Court summarily reversed the Fifth Circuit for committing in *Tolan v. Cotton*, 572 U.S. 650 (2014), and soon after the Court unanimously reversed the Fifth Circuit in *Barnes v. Felix*, 605 U.S. 73 (2025).
- **Weak Plenary Vehicle and Zero Amicus Support:** QPs 1–3 (`questions-presented.txt`) are poorly framed for plenary review (QP 1 is fact-bound; QP 2 mixes an unpreserved burden-of-proof claim with an intracircuit Fifth Circuit phrasing critique; QP 3 is an academic defense of qualified immunity's 1791 roots that was never passed on below). No amicus briefs were filed supporting the petition.

---

## 4. Rationale for Individual Claims and Big-Case Score

- **`relist-increment` (`0.38`):** Starting from the 27.7% empirical rate at which relist-bucket-1 petitions advance to bucket 2+, I adjust upward to 38% because (a) this is a genuine post-Long-Conference relist rather than a pre-conference reschedule, and (b) petitions under consideration for either a summary reversal (like *Zorn v. Linton*, which was distributed 10 times) or a dissent from denial frequently relist multiple times while writings circulate.
- **`cvsg-increment` (`0.01`):** No federal interest or statute is involved; a CVSG is virtually impossible.
- **`summary-disposition-route` (`0.77`):** Conditional on a grant ($P = 0.22$), the overwhelming majority of the probability mass (~17% out of 22%, or 77% conditional share) lies in a per curiam summary reversal on Prong Two of qualified immunity, as urged by Judge Oldham, rather than full merits briefing and oral argument (~5% unconditional, or 23% conditional share).
- **`dissent-from-denial` (`0.28`):** Conditional on denial ($P = 0.78$), there is a 28% chance that at least one Justice writes a dissent or statement respecting denial, given the 8–9 Fifth Circuit en banc vote and the recurring debate over summary-judgment qualified immunity standards.
- **`big_case_score` (`0.35`):** Decoupled from grant likelihood, if the Court were to decide this case (either by summary reversal or plenary opinion), it would be a moderately significant Fourth Amendment deadly-force and qualified-immunity precedent clarifying how *Tolan v. Cotton* and *Barnes v. Felix* interact with *Mullenix*/*Wesby* in armed-flight cases, though bounded by its fact-specific summary-judgment posture.
